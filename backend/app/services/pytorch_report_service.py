import logging
from typing import Any

from ai_layer.pytorch_engine.inference import predict_triage

logger = logging.getLogger("backend.pytorch_report_service")


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
            return predict_triage(description, risk_metadata)
        except Exception:
            logger.exception("PyTorch triage failed")
            return {
                "risk_level": "medium",
                "priority": 0.5,
                "needs_human_review": True,
                "confidence": 0.0,
                "top_factors": ["pytorch_error_fallback"],
                "model_version": "fallback",
                "engine": "error_fallback",
            }
