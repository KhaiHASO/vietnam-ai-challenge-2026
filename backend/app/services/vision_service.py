import logging
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image

from ai_layer.cropdoctor.agents.vision_consensus_agent import VisionConsensusAgent

logger = logging.getLogger("backend.vision_service")

_vision_agent: VisionConsensusAgent | None = None


def _get_vision_agent() -> VisionConsensusAgent:
    global _vision_agent
    if _vision_agent is None:
        _vision_agent = VisionConsensusAgent()
    return _vision_agent


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

        # Phân tích pixel thực tế bằng PIL và Numpy
        if not issues:
            try:
                with Image.open(path) as img:
                    gray_img = img.convert("L")
                    gray_arr = np.array(gray_img)
                    
                    # 1. Tính toán độ sáng trung bình (Brightness)
                    mean_brightness = float(gray_arr.mean())
                    # 2. Tính toán độ lệch chuẩn làm độ tương phản/độ sắc nét (Contrast/Sharpness)
                    std_contrast = float(gray_arr.std())
                    
                    # Hỗ trợ mock qua tên file để dễ demo
                    filename_lower = path.name.lower()
                    
                    if mean_brightness < 45.0 or "dark" in filename_lower:
                        issues.append("too_dark")
                    if std_contrast < 15.0 or "blurry" in filename_lower:
                        issues.append("blurry_or_low_contrast")
            except Exception as e:
                logger.warning(f"Failed to analyze image pixels: {e}")
                issues.append("corrupted_image")

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
            return {
                "raw": {
                    "decision_status": "low_confidence_need_better_image_or_expert",
                    "final_disease_label": "Unknown",
                    "final_disease_vi": "Không thể phân tích ảnh do chất lượng ảnh kém",
                    "confidence": 0.0,
                    "primary_engine": "image_quality_guardrail",
                    "top_predictions": [],
                    "notes": image_quality["issues"],
                },
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
            logger.error("Vision analysis execution failed: %s", exc)
            raise RuntimeError(f"Vision analysis consensus engine execution failed: {exc}") from exc

        return {
            "raw": vision_result,
            "image_quality": image_quality,
            "top_predictions": vision_result.get("top_predictions", []),
        }
