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


def _diagnosis_level(vision_result: dict[str, Any]) -> str:
    decision_status = vision_result.get("decision_status")
    if decision_status == "confident_preliminary_diagnosis":
        return "confident"
    if decision_status == "need_more_symptoms":
        return "uncertain"
    return "low_confidence"


def _demo_reasoning_result(
    vision_result: dict[str, Any],
    symptoms: str,
    crop_hint: str,
    reason: str,
) -> dict[str, Any]:
    disease_vi = vision_result.get("final_disease_vi") or "Chưa xác định"
    disease_label = vision_result.get("final_disease_label") or "Unknown"
    confidence = float(vision_result.get("confidence") or 0.0)
    symptoms_note = symptoms.strip() if symptoms.strip() else "Chưa có mô tả triệu chứng bổ sung."

    return {
        "engine": "demo_reasoning_fallback",
        "model": "demo-stable-reasoning-v1",
        "fallback_used": True,
        "fallback_reason": reason,
        "content": {
            "diagnosis_level": _diagnosis_level(vision_result),
            "short_diagnosis": f"{disease_vi} - cần xác minh thêm trước khi xử lý.",
            "top_possibilities": [
                f"Kết quả thị giác sơ bộ: {disease_label} với độ tin cậy {round(confidence * 100, 1)}%.",
                "Có thể là stress sinh lý hoặc bệnh lá phổ biến; cần đối chiếu thêm triệu chứng tại ruộng.",
                "Không đủ căn cứ để khuyến nghị hóa chất mạnh khi dịch vụ lập luận AI lỗi.",
            ],
            "why": [
                "AI reasoning service không khả dụng nên backend dùng demo response ổn định.",
                f"Cây trồng/ngữ cảnh: {crop_hint or 'chưa cung cấp'}.",
                f"Triệu chứng đã ghi nhận: {symptoms_note}",
            ],
            "questions_to_confirm": [
                "Vết bệnh bắt đầu từ lá già hay lá non?",
                "Triệu chứng có lan nhanh trong 48 giờ gần nhất không?",
                "Tỷ lệ diện tích lá hoặc số cây bị ảnh hưởng ước tính là bao nhiêu phần trăm?",
            ],
            "safe_recommendations": [
                "Tạm thời cách ly cây/lá nghi bệnh và vệ sinh dụng cụ sau khi thao tác.",
                "Chụp thêm ảnh cận cảnh mặt trên, mặt dưới lá trong ánh sáng tự nhiên.",
                "Ưu tiên biện pháp IPM an toàn: tỉa lá bệnh, giảm ẩm tán lá, theo dõi lây lan trước khi can thiệp mạnh.",
            ],
            "when_to_call_expert": [
                "Khi bệnh lan rộng, cây héo nhanh hoặc ảnh hưởng hơn 30% diện tích lá.",
                "Khi cần dùng thuốc hóa học hoặc hoạt chất đặc trị.",
            ],
            "disclaimer": "Đây là fallback demo khi AI reasoning lỗi; không thay thế tư vấn của chuyên gia nông nghiệp.",
        },
    }


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
            logger.warning(
                "Reasoning finalization failed; using demo fallback: %s",
                exc.__class__.__name__,
            )
            return _demo_reasoning_result(
                vision_result=vision_result,
                symptoms=symptoms,
                crop_hint=crop_hint,
                reason=exc.__class__.__name__,
            )
