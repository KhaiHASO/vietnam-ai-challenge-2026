import pytest
from app.approvals.service import ApprovalService
from app.approvals.service import ApprovalConflictError

@pytest.mark.asyncio
async def test_pending_approval_survives_service_recreation(repository, approval) -> None:
    await ApprovalService(repository).create(approval)
    loaded = await ApprovalService(repository).get(approval.approval_id)
    assert loaded.status == "pending"


@pytest.mark.asyncio
async def test_approval_decision_is_atomic(repository, approval) -> None:
    service = ApprovalService(repository)
    await service.create(approval)
    await service.approve(approval.approval_id, actor="expert-1", reason="verified")
    with pytest.raises(ApprovalConflictError):
        await service.reject(approval.approval_id, actor="expert-2", reason="late")
