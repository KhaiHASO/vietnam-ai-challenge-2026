import uuid
from datetime import datetime, timezone
from typing import Any

STRONG_CHEMICAL_KEYWORDS = (
    "ridomil",
    "metalaxyl",
    "mancozeb",
    "chlorothalonil",
    "propiconazole",
    "difenoconazole",
    "thuốc đặc trị",
    "thuốc hóa học",
    "hóa chất",
    "phun bao vây dập dịch",
    "liều lượng lớn",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class SafetyIpmService:
    def has_strong_chemical_recommendation(self, recommended_actions: list[str]) -> bool:
        combined_actions = " ".join(recommended_actions).lower()
        return any(keyword in combined_actions for keyword in STRONG_CHEMICAL_KEYWORDS)

    def expert_review_reasons(
        self,
        risk_level: str,
        recommended_actions: list[str],
    ) -> list[str]:
        reasons = []
        if risk_level == "high":
            reasons.append("high_risk")
        if self.has_strong_chemical_recommendation(recommended_actions):
            reasons.append("strong_chemical_recommendation")
        return reasons

    def requires_expert_review(
        self,
        risk_level: str,
        recommended_actions: list[str],
    ) -> bool:
        return bool(self.expert_review_reasons(risk_level, recommended_actions))

    def build_follow_up_questions(
        self,
        vision_result: dict[str, Any],
        reasoning_result: dict[str, Any] | None = None,
    ) -> list[str]:
        content = (reasoning_result or {}).get("content", {})
        reasoning_questions = content.get("questions_to_confirm")
        if isinstance(reasoning_questions, list) and reasoning_questions:
            return [str(question) for question in reasoning_questions]

        label = vision_result.get("final_disease_label", "").lower()
        decision_status = vision_result.get("decision_status", "")
        questions = [
            "Vết bệnh xuất hiện đầu tiên ở lá già sát mặt đất hay lá non phía trên?",
            "Trong 7 ngày gần đây vườn có mưa lớn, sương đêm hoặc tưới phun lên lá không?",
            "Tỷ lệ cây hoặc diện tích lá bị ảnh hưởng ước tính là bao nhiêu phần trăm?",
        ]

        if "late_blight" in label:
            questions.append("Mặt dưới lá có lớp tơ trắng mỏng khi trời ẩm không?")
        elif "early_blight" in label:
            questions.append("Vết đốm có dạng vòng tròn đồng tâm như hình bia bắn không?")
        elif "bacterial" in label:
            questions.append("Trên quả hoặc mặt dưới lá có nốt sần nhỏ như mụn cóc không?")
        elif "healthy" in label:
            questions.append("Cây có dấu hiệu héo rũ ban ngày dù đất vẫn đủ ẩm không?")
        else:
            questions.append("Triệu chứng có lan nhanh sang cây bên cạnh trong 48 giờ gần nhất không?")

        if decision_status == "low_confidence_need_better_image_or_expert":
            questions.append("Bạn có thể chụp thêm ảnh cận cảnh mặt trên và mặt dưới lá trong ánh sáng tự nhiên không?")

        return questions

    def build_recommended_actions(
        self,
        reasoning_result: dict[str, Any] | None,
        risk_level: str,
    ) -> list[str]:
        content = (reasoning_result or {}).get("content", {})
        recommendations = content.get("safe_recommendations")
        if isinstance(recommendations, list) and recommendations:
            return [str(action) for action in recommendations]

        actions = [
            "Hoàn tất câu hỏi triệu chứng trước khi áp dụng biện pháp xử lý.",
            "Ưu tiên IPM: vệ sinh vườn, tỉa lá bệnh, tránh tưới phun lên lá và theo dõi lây lan.",
        ]
        if risk_level == "high":
            actions.append("Liên hệ chuyên gia hoặc cán bộ khuyến nông trước khi dùng biện pháp hóa học.")
        return actions

    def expert_required(
        self,
        risk_level: str,
        recommended_actions: list[str] | None = None,
    ) -> bool:
        return self.requires_expert_review(risk_level, recommended_actions or [])

    def build_diagnosis(
        self,
        vision_result: dict[str, Any],
        reasoning_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        content = (reasoning_result or {}).get("content", {})
        return {
            "label": vision_result.get("final_disease_label", "Unknown"),
            "label_vi": vision_result.get("final_disease_vi", "Không xác định"),
            "decision_status": vision_result.get("decision_status", "uncertain"),
            "summary": content.get("short_diagnosis")
            or vision_result.get("final_disease_vi")
            or "Không xác định",
            "diagnosis_level": content.get("diagnosis_level"),
            "consensus_achieved": vision_result.get("consensus_achieved", False),
        }

    def build_ai_response(
        self,
        vision_report: dict[str, Any],
        triage_result: dict[str, Any],
        reasoning_result: dict[str, Any] | None = None,
        agent_logs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        vision_result = vision_report.get("raw", {})
        risk_level = triage_result.get("risk_level", "medium")
        recommended_actions = self.build_recommended_actions(reasoning_result, risk_level)
        fallback_sources = []
        if vision_result.get("fallback_used"):
            fallback_sources.append("vision")
        if triage_result.get("fallback_used"):
            fallback_sources.append("pytorch")
        if (reasoning_result or {}).get("fallback_used"):
            fallback_sources.append("reasoning")
        return {
            "image_quality": vision_report.get("image_quality", {}),
            "top_predictions": vision_report.get("top_predictions", []),
            "diagnosis": self.build_diagnosis(vision_result, reasoning_result),
            "recommended_actions": recommended_actions,
            "follow_up_questions": self.build_follow_up_questions(vision_result, reasoning_result),
            "risk_level": risk_level,
            "confidence": vision_result.get("confidence", triage_result.get("confidence", 0.0)),
            "expert_required": self.expert_required(risk_level, recommended_actions),
            "fallback_used": bool(fallback_sources),
            "fallback_sources": fallback_sources,
            "agent_logs": agent_logs or [],
        }

    def build_treatment_plan(
        self,
        case_id: str,
        reasoning_result: dict[str, Any],
        risk_level: str = "medium",
    ) -> dict[str, Any]:
        content = reasoning_result.get("content", {})
        now = _now()
        recommendations = self.build_recommended_actions(reasoning_result, risk_level)
        needs_approval = self.expert_required(risk_level, recommendations)
        return {
            "plan_id": _new_id("plan"),
            "case_id": case_id,
            "status": "pending_approval" if needs_approval else "draft",
            "diagnosis_level": content.get("diagnosis_level", "uncertain"),
            "short_diagnosis": content.get("short_diagnosis", "Chưa đủ dữ liệu chẩn đoán"),
            "recommendations": recommendations,
            "approval_required": needs_approval,
            "approval_reasons": self.expert_review_reasons(risk_level, recommendations),
            "safety_notes": content.get("why", []),
            "when_to_call_expert": content.get("when_to_call_expert", []),
            "disclaimer": content.get("disclaimer", ""),
            "created_at": now,
            "updated_at": now,
        }

    def build_expert_review(
        self,
        case_id: str,
        risk_level: str,
        treatment_plan: dict[str, Any],
    ) -> dict[str, Any] | None:
        recommendations = treatment_plan.get("recommendations", [])
        reasons = self.expert_review_reasons(risk_level, recommendations)
        if not reasons:
            return None

        now = _now()
        return {
            "review_id": _new_id("review"),
            "case_id": case_id,
            "status": "pending",
            "reviewer_id": None,
            "notes": "Tự động tạo vì kế hoạch xử lý cần chuyên gia phê duyệt trước khi áp dụng.",
            "risk_level": risk_level,
            "treatment_plan_id": treatment_plan["plan_id"],
            "reason": ",".join(reasons),
            "reasons": reasons,
            "recommended_actions": recommendations,
            "created_at": now,
            "updated_at": now,
        }
