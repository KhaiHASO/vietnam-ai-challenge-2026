import time
import logging
import uuid
import json
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from ai_layer.rag.observability.context import get_trace_id
from ai_layer.rag.observability.database import TelemetryDB

logger = logging.getLogger(__name__)

_SECRET_KEYS = {
    "token",
    "authorization",
    "password",
    "refresh_token",
    "api_key",
    "secret",
    "query",
    "prompt",
    "response",
    "answer",
    "content",
}
_PHONE = re.compile(r"(?<!\d)(?:\+?84|0)\d{9,10}(?!\d)")
_EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")


def _redact(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in _SECRET_KEYS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(item_key): _redact(item_value, str(item_key)) for item_key, item_value in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return _EMAIL.sub("[REDACTED_EMAIL]", _PHONE.sub("[REDACTED_PHONE]", value))
    return value


@dataclass(frozen=True)
class RedactedTraceEvent:
    payload: dict[str, Any]
    serialized: str


class TraceRecorder:
    """Records metadata only; raw prompts, secrets, and chain-of-thought never enter traces."""

    def record(self, payload: dict[str, Any]) -> RedactedTraceEvent:
        safe = _redact(payload)
        return RedactedTraceEvent(payload=safe, serialized=json.dumps(safe, ensure_ascii=False, sort_keys=True))

class Span:
    def __init__(self, step_name: str, domain_id: str = "agriculture"):
        self.step_name = step_name
        self.domain_id = domain_id
        self.start_time = 0.0
        self.end_time = 0.0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0
        self.span_id = ""
        self.trace_id = ""

    def __enter__(self):
        self.span_id = str(uuid.uuid4())
        self.trace_id = get_trace_id() or "no-trace-id"
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        latency_ms = int((self.end_time - self.start_time) * 1000)
        try:
            TelemetryDB.log_span(
                span_id=self.span_id,
                trace_id=self.trace_id,
                step_name=self.step_name,
                latency_ms=latency_ms,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                cost_usd=self.cost_usd,
                domain_id=self.domain_id
            )
        except Exception as e:
            logger.warning(f"Failed to log span: {e}")

def trace_provider_call(
    provider_name: str,
    model_version: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    cache_savings: bool,
    status_code: int,
    request_id: str
):
    """
    Trace provider specific details as specified in the plan:
    Trace only provider name, model/version, token counts, latency, cache savings, status code class, and request ID.
    """
    status_class = f"{status_code // 100}xx" if status_code else "unknown"
    payload = {
        "provider_name": provider_name,
        "model_version": model_version,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "cache_savings": cache_savings,
        "status_class": status_class,
        "request_id": request_id
    }
    logger.info(f"[Trace Provider Call] {payload}")
    try:
        TelemetryDB.log_event("provider_call", "single", payload)
    except Exception as e:
        logger.warning(f"Failed to log provider call event: {e}")
