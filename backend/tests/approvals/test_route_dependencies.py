from app.approvals.mongo_repository import MongoApprovalRepository
from app.db.mongo import mongo_state
from app.routes import approvals


def test_approval_dependency_uses_mongo_when_database_is_ready(monkeypatch) -> None:
    monkeypatch.setattr(mongo_state, "connected", True)
    assert isinstance(approvals.get_approval_service().repository, MongoApprovalRepository)
