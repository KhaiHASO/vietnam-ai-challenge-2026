import asyncio
import logging
import random
import time
from typing import Any

import httpx

from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.observability.trace import trace_provider_call

logger = logging.getLogger(__name__)


class ProviderError(RuntimeError):
    pass


class ProviderConfigurationError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderUnavailableError(ProviderError):
    pass


class ProviderGatewayProtocol:
    async def generate(self, query: str, evidence: list[Evidence]) -> str: ...


class ProviderGateway:
    def __init__(
        self,
        provider_adapter,
        fallback_adapters: list[Any] | None = None,
        *,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        failure_threshold: int = 3,
        cooldown_period: float = 60.0,
    ) -> None:
        self.adapter = provider_adapter
        self.fallback_adapters = fallback_adapters or []
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        self._circuit_failures: dict[str, int] = {}
        self._circuit_tripped_until: dict[str, float] = {}
        self.last_metadata: dict[str, Any] = {}

    @staticmethod
    def _get_provider_id(adapter) -> str:
        return getattr(adapter, "provider_name", adapter.__class__.__name__)

    def _is_tripped(self, provider_id: str) -> bool:
        tripped_until = self._circuit_tripped_until.get(provider_id, 0.0)
        if time.monotonic() < tripped_until:
            return True
        if provider_id in self._circuit_tripped_until:
            self._circuit_tripped_until.pop(provider_id, None)
            self._circuit_failures[provider_id] = 0
        return False

    def _record_failure(self, provider_id: str) -> None:
        failures = self._circuit_failures.get(provider_id, 0) + 1
        self._circuit_failures[provider_id] = failures
        if failures >= self.failure_threshold:
            self._circuit_tripped_until[provider_id] = (
                time.monotonic() + self.cooldown_period
            )

    def _record_success(self, provider_id: str) -> None:
        self._circuit_failures[provider_id] = 0
        self._circuit_tripped_until.pop(provider_id, None)

    @staticmethod
    def _is_transient(exc: Exception) -> bool:
        if isinstance(exc, (asyncio.TimeoutError, httpx.TimeoutException, httpx.NetworkError)):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code == 429 or exc.response.status_code >= 500
        return False

    async def generate(
        self,
        query: str,
        evidence: list[Evidence],
        high_risk: bool = False,
        domain_policy: Any = None,
    ) -> str:
        last_exception: Exception | None = None
        for index, adapter in enumerate([self.adapter, *self.fallback_adapters]):
            provider_id = self._get_provider_id(adapter)
            degraded = index > 0
            if degraded and high_risk and not bool(
                getattr(domain_policy, "allow_high_risk_fallback", False)
            ):
                continue
            if self._is_tripped(provider_id):
                continue

            for attempt in range(1, self.max_retries + 1):
                started = time.perf_counter()
                task = asyncio.create_task(adapter.generate(query, evidence))
                try:
                    response = await asyncio.wait_for(task, timeout=self.timeout_seconds)
                    if not isinstance(response, str) or not response.strip():
                        raise ProviderError("Provider returned an empty response")
                    self._record_success(provider_id)
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    self.last_metadata = {
                        "provider": provider_id,
                        "model_revision": getattr(adapter, "model_id", "unknown"),
                        "latency_ms": latency_ms,
                        "degraded": degraded,
                    }
                    trace_provider_call(
                        provider_name=provider_id,
                        model_version=self.last_metadata["model_revision"],
                        input_tokens=0,
                        output_tokens=0,
                        latency_ms=latency_ms,
                        cache_savings=False,
                        status_code=200,
                        request_id="unavailable",
                    )
                    return response
                except Exception as exc:
                    last_exception = exc
                    if not task.done():
                        task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                    if not self._is_transient(exc):
                        self._record_failure(provider_id)
                        if isinstance(exc, ProviderError):
                            raise
                        raise ProviderError(str(exc)) from exc
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2 ** (attempt - 1))
                        await asyncio.sleep(delay + random.uniform(0, delay * 0.2))
            self._record_failure(provider_id)

        if isinstance(last_exception, (asyncio.TimeoutError, httpx.TimeoutException)):
            raise ProviderTimeoutError("Provider timeout") from last_exception
        if last_exception is not None:
            raise ProviderUnavailableError(str(last_exception)) from last_exception
        raise ProviderUnavailableError(
            "All providers are unavailable or disallowed by fallback policy"
        )
