from fastapi import APIRouter, Body, Depends, Query

from app.schemas.expert import ExpertReviewDecisionRequest
from app.services.expert_review_service import ExpertReviewService

router = APIRouter(prefix="/api/expert", tags=["Expert"])


def get_expert_review_service() -> ExpertReviewService:
    return ExpertReviewService()


@router.get("/reviews")
async def list_expert_reviews(
    status: str | None = Query(default=None),
    service: ExpertReviewService = Depends(get_expert_review_service),
) -> dict[str, object]:
    return await service.list_reviews(status=status)


@router.post("/reviews/{review_id}/approve")
async def approve_expert_review(
    review_id: str,
    request: ExpertReviewDecisionRequest | None = Body(default=None),
    service: ExpertReviewService = Depends(get_expert_review_service),
) -> dict[str, object]:
    return await service.approve_review(review_id, request or ExpertReviewDecisionRequest())


@router.post("/reviews/{review_id}/reject")
async def reject_expert_review(
    review_id: str,
    request: ExpertReviewDecisionRequest | None = Body(default=None),
    service: ExpertReviewService = Depends(get_expert_review_service),
) -> dict[str, object]:
    return await service.reject_review(review_id, request or ExpertReviewDecisionRequest())
