from __future__ import annotations

from datetime import datetime
from typing import Any

from app.db.mongo import get_database

from .repository import ApprovalRecord, ApprovalRepository


class MongoApprovalRepository(ApprovalRepository):
    """Mongo-backed compare-and-set approval persistence."""

    def __init__(self, collection: Any | None = None) -> None:
        self._collection = collection

    @property
    def collection(self) -> Any:
        return self._collection if self._collection is not None else get_database().approvals

    @staticmethod
    def _document(record: ApprovalRecord) -> dict[str, Any]:
        return {
            "approval_id": record.approval_id,
            "policy": record.policy,
            "proposed_action": record.proposed_action,
            "evidence": record.evidence,
            "requester": record.requester,
            "required_roles": record.required_roles,
            "status": record.status,
            "decision_actor": record.decision_actor,
            "decision_time": record.decision_time,
            "decision_reason": record.decision_reason,
            "idempotency_key": record.idempotency_key,
            "trace_id": record.trace_id,
        }

    @staticmethod
    def _record(document: dict[str, Any]) -> ApprovalRecord:
        document.pop("_id", None)
        return ApprovalRecord(**document)

    async def save(self, record: ApprovalRecord) -> None:
        await self.collection.replace_one({"approval_id": record.approval_id}, self._document(record), upsert=True)

    async def get(self, approval_id: str) -> ApprovalRecord | None:
        document = await self.collection.find_one({"approval_id": approval_id})
        return self._record(document) if document else None

    async def update_status(self, approval_id: str, old_status: str, new_status: str, actor: str, reason: str, time: datetime) -> bool:
        result = await self.collection.update_one(
            {"approval_id": approval_id, "status": old_status},
            {"$set": {"status": new_status, "decision_actor": actor, "decision_reason": reason, "decision_time": time}},
        )
        return result.modified_count == 1

    async def list_for_requester(self, requester: str) -> list[ApprovalRecord]:
        cursor = self.collection.find({"requester": requester}).sort("decision_time", -1)
        return [self._record(document) for document in await cursor.to_list(length=100)]
