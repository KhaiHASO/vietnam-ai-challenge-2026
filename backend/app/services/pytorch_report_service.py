import logging
from typing import Any

from ai_layer.pytorch_engine.inference import predict_triage

logger = logging.getLogger("backend.pytorch_report_service")


def _uses_heuristic_fallback(result: dict[str, Any]) -> bool:
    engine = str(result.get("engine", "")).lower()
    model_version = str(result.get("model_version", "")).lower()
    return (
        bool(result.get("fallback_used"))
        or "fallback" in engine
        or model_version.startswith("fallback")
    )


def _heuristic_fallback(reason: str) -> dict[str, Any]:
    return {
        "risk_level": "medium",
        "priority": 0.5,
        "needs_human_review": True,
        "confidence": 0.0,
        "top_factors": ["pytorch_error_fallback"],
        "model_version": "fallback-heuristics-v1.0",
        "engine": "Heuristic Fallback",
        "fallback_used": True,
        "fallback_reason": reason,
    }


class PyTorchReportService:
    def assess_risk(
        self,
        vision_result: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        description = " ".join(
            str(part)
            for part in (
                vision_result.get("final_disease_vi"),
                vision_result.get("final_disease_label"),
                vision_result.get("decision_status"),
            )
            if part
        )

        risk_metadata = dict(metadata or {})
        risk_metadata.setdefault("leaf_damage_percent", 0.0)

        try:
            result = predict_triage(description, risk_metadata)
            if not isinstance(result, dict):
                return _heuristic_fallback("invalid_pytorch_response")

            normalized = dict(result)
            fallback_used = _uses_heuristic_fallback(normalized)
            normalized["fallback_used"] = fallback_used
            if fallback_used:
                normalized.setdefault("fallback_reason", "heuristic_fallback")
            return normalized
        except Exception as exc:
            logger.warning("PyTorch triage failed; using heuristic fallback: %s", exc.__class__.__name__)
            return _heuristic_fallback(exc.__class__.__name__)
