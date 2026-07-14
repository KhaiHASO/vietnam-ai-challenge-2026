from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from typing import Any

# For now, we mock the dependency injection of ApprovalService
from app.approvals.repository import InMemoryApprovalRepository
from app.approvals.mongo_repository import MongoApprovalRepository
from app.approvals.service import ApprovalService
from app.db.mongo import mongo_state
from app.auth.dependencies import get_current_user, require_roles
from app.auth.contracts import Principal, Role

router = APIRouter(prefix="/api", tags=["Approvals"])

_repo = InMemoryApprovalRepository()
_service = ApprovalService(_repo)

def get_approval_service() -> ApprovalService:
    if mongo_state.connected:
        return ApprovalService(MongoApprovalRepository())
    return _service


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(default="", max_length=1000)

@router.get("/approvals")
async def approvals(service: ApprovalService = Depends(get_approval_service), current_user: Principal = Depends(get_current_user)) -> list[dict[str, object]]:
    # In a real app we'd query the DB for pending
    return []

@router.post("/approvals/{approval_id}/approve")
async def approve_approval(approval_id: str, request: DecisionRequest, service: ApprovalService = Depends(get_approval_service), current_user: Principal = Depends(require_roles([Role.ADMIN, Role.EXPERT]))) -> dict[str, object]:
    try:
        await service.approve(approval_id, actor=current_user.user_id, reason=request.reason)
        return {"success": True, "message": "Approved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approvals/{approval_id}/reject")
async def reject_approval(approval_id: str, request: DecisionRequest, service: ApprovalService = Depends(get_approval_service), current_user: Principal = Depends(require_roles([Role.ADMIN, Role.EXPERT]))) -> dict[str, object]:
    try:
        await service.reject(approval_id, actor=current_user.user_id, reason=request.reason)
        return {"success": True, "message": "Rejected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
