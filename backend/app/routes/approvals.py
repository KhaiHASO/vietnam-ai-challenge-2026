from fastapi import APIRouter

from app.services.approval_service import (
    approve_action,
    get_pending_approvals,
    reject_action,
)

router = APIRouter(prefix="/api", tags=["Approvals"])


@router.get("/approvals")
def approvals() -> list[dict[str, object]]:
    return get_pending_approvals()


@router.post("/approvals/{approval_id}/approve")
def approve_approval(approval_id: str) -> dict[str, object]:
    return approve_action(approval_id)


@router.post("/approvals/{approval_id}/reject")
def reject_approval(approval_id: str) -> dict[str, object]:
    return reject_action(approval_id)
