import logging
from pathlib import Path
from typing import Any

from ai_layer.cropdoctor.agents.vision_consensus_agent import VisionConsensusAgent

logger = logging.getLogger("backend.vision_service")

_vision_agent: VisionConsensusAgent | None = None

DEMO_TOP_PREDICTIONS: list[dict[str, Any]] = [
    {
        "label": "Tomato___Early_blight",
        "label_vi": "Bệnh úa sớm trên cây cà chua",
        "score": 0.35,
    },
    {
        "label": "Tomato___Late_blight",
        "label_vi": "Bệnh mốc sương trên cây cà chua",
        "score": 0.22,
    },
    {
        "label": "healthy",
        "label_vi": "Cây trồng khỏe mạnh",
        "score": 0.18,
    },
]


def _get_vision_agent() -> VisionConsensusAgent:
    global _vision_agent
    if _vision_agent is None:
        _vision_agent = VisionConsensusAgent()
    return _vision_agent


def _demo_vision_result(
    crop_hint: str,
    image_quality: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    return {
        "crop_hint": crop_hint,
        "decision_status": "need_more_symptoms",
        "consensus_achieved": False,
        "final_disease_label": "DemoFallback___NeedsReview",
        "final_disease_vi": "Chẩn đoán demo ổn định - cần xác minh thêm triệu chứng",
        "confidence": 0.35,
        "primary_engine": "demo_vision_fallback",
        "top_predictions": DEMO_TOP_PREDICTIONS,
        "engines": {
            "fallback": {
                "success": True,
                "fallback_used": True,
                "reason": reason,
            }
        },
        "fallback_used": True,
        "fallback_reason": reason,
        "notes": [
            "AI vision service is unavailable, so the backend returned a stable demo response.",
            "Do not treat this as a final diagnosis without symptom answers or expert review.",
            f"Image quality status: {image_quality.get('status', 'unknown')}",
        ],
    }


class VisionService:
    def inspect_image_quality(self, image_path: str) -> dict[str, Any]:
        path = Path(image_path)
        issues: list[str] = []

        if not path.exists():
            issues.append("image_not_found")
            return {
                "status": "invalid",
                "usable": False,
                "issues": issues,
                "size_bytes": 0,
                "extension": path.suffix.lower().lstrip("."),
            }

        size_bytes = path.stat().st_size
        extension = path.suffix.lower().lstrip(".")
        if size_bytes <= 0:
            issues.append("empty_file")
        if extension not in {"jpg", "jpeg", "png", "webp"}:
            issues.append("unsupported_extension")

        return {
            "status": "ok" if not issues else "needs_review",
            "usable": not issues,
            "issues": issues,
            "size_bytes": size_bytes,
            "extension": extension,
        }

    def analyze_image(
        self,
        image_path: str,
        crop_hint: str = "",
        original_filename: str = "",
    ) -> dict[str, Any]:
        image_quality = self.inspect_image_quality(image_path)
        if not image_quality["usable"]:
            vision_result = _demo_vision_result(
                crop_hint=crop_hint,
                image_quality=image_quality,
                reason="image_quality_guardrail",
            )
            vision_result.update(
                {
                    "decision_status": "low_confidence_need_better_image_or_expert",
                    "final_disease_label": "Unknown",
                    "final_disease_vi": "Không thể phân tích ảnh",
                    "confidence": 0.0,
                    "primary_engine": "image_quality_guardrail",
                    "top_predictions": [],
                    "notes": image_quality["issues"],
                }
            )
            return {
                "raw": vision_result,
                "image_quality": image_quality,
                "top_predictions": [],
            }

        try:
            vision_result = _get_vision_agent().predict(
                image_path=image_path,
                crop_hint=crop_hint,
                original_filename=original_filename,
            )
        except Exception as exc:
            logger.warning("Vision analysis failed; using demo fallback: %s", exc.__class__.__name__)
            vision_result = _demo_vision_result(
                crop_hint=crop_hint,
                image_quality=image_quality,
                reason=exc.__class__.__name__,
            )
            return {
                "raw": vision_result,
                "image_quality": image_quality,
                "top_predictions": vision_result["top_predictions"],
            }

        return {
            "raw": vision_result,
            "image_quality": image_quality,
            "top_predictions": vision_result.get("top_predictions", []),
        }
