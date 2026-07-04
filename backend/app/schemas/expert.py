from pydantic import BaseModel


class ExpertReviewDecisionRequest(BaseModel):
    reviewer_id: str | None = None
    notes: str | None = None
