import logging
from typing import Any

from ai_layer.cropdoctor.agents.deepseek_reasoning_agent import DeepSeekReasoningAgent

logger = logging.getLogger("backend.reasoning_service")

_reasoning_agent: DeepSeekReasoningAgent | None = None


def _get_reasoning_agent() -> DeepSeekReasoningAgent:
    global _reasoning_agent
    if _reasoning_agent is None:
        _reasoning_agent = DeepSeekReasoningAgent()
    return _reasoning_agent


class ReasoningService:
    def finalize_diagnosis(
        self,
        vision_result: dict[str, Any],
        symptoms: str,
        crop_hint: str = "",
    ) -> dict[str, Any]:
        try:
            return _get_reasoning_agent().reason(
                vision_result=vision_result,
                symptoms=symptoms,
                crop_hint=crop_hint,
            )
        except Exception as exc:
            logger.exception("Reasoning finalization failed")
            raise RuntimeError("Reasoning finalization failed") from exc
