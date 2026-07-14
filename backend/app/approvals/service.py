from datetime import datetime, timezone
from typing import Any
from .repository import ApprovalRepository, ApprovalRecord

class ApprovalConflictError(Exception):
    pass

class ApprovalService:
    def __init__(self, repository: ApprovalRepository):
        self.repository = repository

    async def create(self, approval_data: dict[str, Any] | ApprovalRecord) -> ApprovalRecord:
        if isinstance(approval_data, dict):
            record = ApprovalRecord(**approval_data)
        else:
            record = approval_data
        await self.repository.save(record)
        return record

    async def get(self, approval_id: str) -> ApprovalRecord | None:
        return await self.repository.get(approval_id)

    async def approve(self, approval_id: str, actor: str, reason: str = "") -> bool:
        success = await self.repository.update_status(
            approval_id, "pending", "approved", actor, reason, datetime.now(timezone.utc)
        )
        if not success:
            raise ApprovalConflictError(f"Approval {approval_id} is no longer pending or does not exist.")
        return True

    async def reject(self, approval_id: str, actor: str, reason: str = "") -> bool:
        success = await self.repository.update_status(
            approval_id, "pending", "rejected", actor, reason, datetime.now(timezone.utc)
        )
        if not success:
            raise ApprovalConflictError(f"Approval {approval_id} is no longer pending or does not exist.")
        return True
