from collections import Counter
import logging
from typing import Any

from ai_layer.tools.db_mock import load_db

from app.repositories.diagnosis_repository import DiagnosisRepository

try:
    from ai_layer.cropdoctor.agents.crop_health_agent import MOCK_DISEASE_DETAILS
except Exception:
    MOCK_DISEASE_DETAILS = {}

logger = logging.getLogger("backend.dashboard_list_service")

KNOWLEDGE_FALLBACK_MESSAGE = "không đủ căn cứ"


class DashboardListService:
    def __init__(self, repository: DiagnosisRepository | None = None) -> None:
        self.repository = repository or DiagnosisRepository()

    async def dashboard_overview(self) -> dict[str, Any]:
        cases = await self.repository.find_many("diagnosis_cases", {}, sort=[("created_at", -1)])
        expert_reviews = await self.repository.find_many("expert_reviews", {})
        treatment_plans = await self.repository.find_many("treatment_plans", {})
        reminders = await self.repository.find_many("reminders", {})

        risk_counts = Counter(case.get("risk_level") or "unknown" for case in cases)
        status_counts = Counter(case.get("status") or "unknown" for case in cases)
        pending_reviews = [
            review for review in expert_reviews if review.get("status") == "pending"
        ]
        pending_plans = [
            plan for plan in treatment_plans if plan.get("status") == "pending_approval"
        ]
        active_reminders = [
            reminder for reminder in reminders if reminder.get("status") in {"pending", "scheduled"}
        ]

        return {
            "summary": {
                "farms": len((await self.list_farms())["farms"]),
                "diagnosis_cases": len(cases),
                "pending_expert_reviews": len(pending_reviews),
                "pending_treatment_plans": len(pending_plans),
                "active_reminders": len(active_reminders),
            },
            "risk_counts": dict(risk_counts),
            "case_status_counts": dict(status_counts),
            "recent_cases": cases[:5],
            "pending_reviews": pending_reviews[:5],
            "follow_up_required": pending_plans[:5] + active_reminders[:5],
        }

    async def list_farms(self) -> dict[str, Any]:
        farms = await self.repository.find_many("farms", {}, sort=[("name", 1)])
        if not farms:
            farms = self._demo_farms()
        return {"farms": farms}

    async def diagnosis_history(self) -> dict[str, Any]:
        cases = await self.repository.find_many("diagnosis_cases", {}, sort=[("created_at", -1)])
        for case in cases:
            if not case.get("image_url"):
                image = await self.repository.find_one("case_images", {"case_id": case["case_id"]})
                if image:
                    case["image_url"] = image.get("uri")
        return {"cases": cases}

    async def diagnosis_follow_up(self) -> dict[str, Any]:
        cases = await self.repository.find_many("diagnosis_cases", {}, sort=[("updated_at", -1)])
        expert_reviews = await self.repository.find_many("expert_reviews", {}, sort=[("created_at", -1)])
        treatment_plans = await self.repository.find_many("treatment_plans", {}, sort=[("created_at", -1)])
        reminders = await self.repository.find_many("reminders", {}, sort=[("due_at", 1)])

        return {
            "cases_waiting_for_symptoms": [
                case for case in cases if case.get("status") == "symptom_questions_ready"
            ],
            "pending_expert_reviews": [
                review for review in expert_reviews if review.get("status") == "pending"
            ],
            "pending_treatment_plans": [
                plan for plan in treatment_plans if plan.get("status") == "pending_approval"
            ],
            "active_reminders": [
                reminder for reminder in reminders if reminder.get("status") in {"pending", "scheduled"}
            ],
        }

    async def season_logs(self) -> dict[str, Any]:
        season_logs = await self.repository.find_many("season_logs", {}, sort=[("created_at", -1)])
        return {"season_logs": season_logs}

    async def reminders(self) -> dict[str, Any]:
        reminders = await self.repository.find_many("reminders", {}, sort=[("due_at", 1)])
        return {"reminders": reminders}

    def knowledge_diseases(self) -> dict[str, Any]:
        try:
            if not MOCK_DISEASE_DETAILS:
                return self._knowledge_fallback("diseases")

            diseases = []
            for disease_id, details in MOCK_DISEASE_DETAILS.items():
                diseases.append(
                    {
                        "disease_id": disease_id,
                        "name": details.get("disease_name"),
                        "symptoms": details.get("symptoms"),
                        "description": details.get("description"),
                        "severity": details.get("severity"),
                        "treatment": details.get("treatment"),
                    }
                )
            return {"diseases": diseases, "fallback_used": False}
        except Exception as exc:
            logger.warning(
                "Knowledge disease lookup failed; returning fallback: %s",
                exc.__class__.__name__,
            )
            return self._knowledge_fallback("diseases")

    def knowledge_ipm(self) -> dict[str, Any]:
        try:
            if not MOCK_DISEASE_DETAILS:
                return self._knowledge_fallback("ipm")

            ipm_items = []
            for disease_id, details in MOCK_DISEASE_DETAILS.items():
                treatment = details.get("treatment", {})
                ipm_items.append(
                    {
                        "disease_id": disease_id,
                        "diagnosis": details.get("disease_name"),
                        "biological": treatment.get("biological"),
                        "prevention": treatment.get("prevention"),
                        "chemical_requires_expert_review": bool(treatment.get("chemical")),
                        "chemical": treatment.get("chemical"),
                    }
                )
            return {
                "principles": [
                    "Ưu tiên vệ sinh đồng ruộng, tỉa lá bệnh và giảm nguồn lây.",
                    "Theo dõi triệu chứng và điều kiện thời tiết trước khi can thiệp.",
                    "Chỉ dùng hóa chất khi cần thiết và cần chuyên gia duyệt với ca rủi ro cao.",
                ],
                "ipm": ipm_items,
                "fallback_used": False,
            }
        except Exception as exc:
            logger.warning(
                "Knowledge IPM lookup failed; returning fallback: %s",
                exc.__class__.__name__,
            )
            return self._knowledge_fallback("ipm")

    async def cooperative_disease_map(self) -> dict[str, Any]:
        farms = (await self.list_farms())["farms"]
        cases = await self.repository.find_many("diagnosis_cases", {}, sort=[("created_at", -1)])
        farm_by_id = {farm.get("farm_id"): farm for farm in farms}

        map_items = []
        for case in cases:
            farm = farm_by_id.get(case.get("farm_id"), {})
            map_items.append(
                {
                    "case_id": case.get("case_id"),
                    "farm_id": case.get("farm_id"),
                    "farm_name": farm.get("name"),
                    "location": case.get("location") or farm.get("location"),
                    "crop": case.get("crop") or farm.get("crop_type"),
                    "risk_level": case.get("risk_level"),
                    "status": case.get("status"),
                    "summary": case.get("summary"),
                    "created_at": case.get("created_at"),
                }
            )

        return {
            "map_points": map_items,
            "risk_counts": dict(Counter(item.get("risk_level") or "unknown" for item in map_items)),
        }

    def _demo_farms(self) -> list[dict[str, Any]]:
        state = load_db()
        return state.get("farms", [])

    def _knowledge_fallback(self, key: str) -> dict[str, Any]:
        payload = {
            key: [],
            "message": KNOWLEDGE_FALLBACK_MESSAGE,
            "fallback_used": True,
        }
        if key == "ipm":
            payload["principles"] = []
        return payload
