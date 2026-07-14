from datetime import datetime, timezone

import pytest

from app.approvals.mongo_repository import MongoApprovalRepository
from app.approvals.repository import ApprovalRecord


class FakeCollection:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}

    async def replace_one(self, selector, document, upsert=False):
        self.documents[selector["approval_id"]] = document

    async def find_one(self, selector, projection=None):
        document = self.documents.get(selector["approval_id"])
        return dict(document) if document else None

    async def update_one(self, selector, update):
        document = self.documents.get(selector["approval_id"])
        if not document or document["status"] != selector["status"]:
            return type("Result", (), {"modified_count": 0})()
        document.update(update["$set"])
        return type("Result", (), {"modified_count": 1})()


@pytest.mark.asyncio
async def test_mongo_repository_applies_decision_once() -> None:
    repository = MongoApprovalRepository(FakeCollection())
    record = ApprovalRecord("a1", "policy", {}, [], "u1", ["expert"], "pending")
    await repository.save(record)
    assert await repository.update_status("a1", "pending", "approved", "e1", "verified", datetime.now(timezone.utc))
    assert not await repository.update_status("a1", "pending", "rejected", "e2", "late", datetime.now(timezone.utc))
    assert (await repository.get("a1")).status == "approved"
