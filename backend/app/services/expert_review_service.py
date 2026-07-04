from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from app.repositories.diagnosis_repository import DiagnosisRepository
from app.schemas.expert import ExpertReviewDecisionRequest
from app.services.agent_log_service import AgentLogService


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ExpertReviewService:
    def __init__(self, repository: DiagnosisRepository | None = None) -> None:
        self.repository = repository or DiagnosisRepository()
        self.agent_log_service = AgentLogService(self.repository)

    async def list_reviews(self, status: str | None = None) -> dict[str, Any]:
        query = {"status": status} if status else {}
        reviews = await self.repository.find_many(
            "expert_reviews",
            query,
            sort=[("created_at", -1)],
        )
        return {"reviews": reviews}

    async def approve_review(
        self,
        review_id: str,
        request: ExpertReviewDecisionRequest,
    ) -> dict[str, Any]:
        return await self._decide_review(review_id, "approved", request)

    async def reject_review(
        self,
        review_id: str,
        request: ExpertReviewDecisionRequest,
    ) -> dict[str, Any]:
        return await self._decide_review(review_id, "rejected", request)

    async def _decide_review(
        self,
        review_id: str,
        decision: str,
        request: ExpertReviewDecisionRequest,
    ) -> dict[str, Any]:
        review = await self.repository.find_one("expert_reviews", {"review_id": review_id})
        if not review:
            raise HTTPException(status_code=404, detail=f"Expert review '{review_id}' not found")

        previous_status = review.get("status")
        if previous_status != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Expert review '{review_id}' is already {previous_status}",
            )

        now = _now()
        treatment_plan_id = review.get("treatment_plan_id")
        treatment_plan = None
        treatment_plan_status = "approved" if decision == "approved" else "rejected"
        if treatment_plan_id:
            treatment_plan = await self.repository.update_one(
                "treatment_plans",
                {"plan_id": treatment_plan_id},
                {
                    "status": treatment_plan_status,
                    "expert_decision": decision,
                    "expert_reviewer_id": request.reviewer_id,
                    "expert_decision_notes": request.notes,
                    "expert_decided_at": now,
                    "updated_at": now,
                },
            )

        updated_review = await self.repository.update_one(
            "expert_reviews",
            {"review_id": review_id},
            {
                "status": decision,
                "reviewer_id": request.reviewer_id,
                "decision_notes": request.notes,
                "decided_at": now,
                "updated_at": now,
            },
        )

        audit_log = await self.agent_log_service.record(
            case_id=review["case_id"],
            agent="ExpertApprovalAgent",
            status=decision,
            trace={
                "review_id": review_id,
                "action": decision,
                "previous_review_status": previous_status,
                "new_review_status": decision,
                "treatment_plan_id": treatment_plan_id,
                "treatment_plan_status": treatment_plan_status if treatment_plan_id else None,
                "reviewer_id": request.reviewer_id,
                "decision_notes": request.notes,
                "risk_level": review.get("risk_level"),
                "reasons": review.get("reasons", []),
                "recommended_actions": review.get("recommended_actions", []),
            },
            duration_ms=0.0,
        )

        return {
            "review": updated_review,
            "treatment_plan": treatment_plan,
            "audit_log": audit_log,
        }
