from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime

class ApprovalRecord:
    def __init__(
        self,
        approval_id: str,
        policy: str,
        proposed_action: dict[str, Any],
        evidence: list[dict[str, Any]],
        requester: str,
        required_roles: list[str],
        status: str,
        decision_actor: str | None = None,
        decision_time: datetime | None = None,
        decision_reason: str | None = None,
        idempotency_key: str | None = None,
        trace_id: str | None = None
    ):
        self.approval_id = approval_id
        self.policy = policy
        self.proposed_action = proposed_action
        self.evidence = evidence
        self.requester = requester
        self.required_roles = required_roles
        self.status = status
        self.decision_actor = decision_actor
        self.decision_time = decision_time
        self.decision_reason = decision_reason
        self.idempotency_key = idempotency_key
        self.trace_id = trace_id

class ApprovalRepository(ABC):
    @abstractmethod
    async def save(self, record: ApprovalRecord) -> None:
        pass

    @abstractmethod
    async def get(self, approval_id: str) -> ApprovalRecord | None:
        pass

    @abstractmethod
    async def update_status(self, approval_id: str, old_status: str, new_status: str, actor: str, reason: str, time: datetime) -> bool:
        pass

class InMemoryApprovalRepository(ApprovalRepository):
    def __init__(self):
        self._store: dict[str, ApprovalRecord] = {}

    async def save(self, record: ApprovalRecord) -> None:
        self._store[record.approval_id] = record

    async def get(self, approval_id: str) -> ApprovalRecord | None:
        return self._store.get(approval_id)

    async def update_status(self, approval_id: str, old_status: str, new_status: str, actor: str, reason: str, time: datetime) -> bool:
        record = self._store.get(approval_id)
        if record and record.status == old_status:
            record.status = new_status
            record.decision_actor = actor
            record.decision_reason = reason
            record.decision_time = time
            return True
        return False
