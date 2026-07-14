import pytest
from fastapi.testclient import TestClient

from app.auth.contracts import Principal, Role
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.main import create_app
from app.workers.main import Job


class FakeIngestionService:
    async def enqueue_upload(self, **kwargs):
        return {"job_id": "job-1", "status": "queued"}

    async def get_status(self, *, job_id, principal):
        if principal.tenant_id != "t1":
            return None
        return {
            "job_id": job_id,
            "status": "completed",
            "attempts": 1,
            "last_error": None,
        }


def test_ingestion_requires_expert_and_returns_a_job() -> None:
    app = create_app()
    from app.knowledge.routes import get_ingestion_service

    app.dependency_overrides[get_ingestion_service] = lambda: FakeIngestionService()
    client = TestClient(app)
    file = {"file": ("policy.txt", b"VietGAP policy", "text/plain")}
    app.dependency_overrides[get_current_user] = lambda: Principal(user_id="op", tenant_id="t1", roles=frozenset([Role.OPERATOR]))
    assert client.post("/api/v1/knowledge/ingestions", files=file).status_code == 403
    app.dependency_overrides[get_current_user] = lambda: Principal(user_id="expert", tenant_id="t1", roles=frozenset([Role.EXPERT]))
    response = client.post("/api/v1/knowledge/ingestions", files=file)
    assert response.status_code == 202
    assert response.json()["status"] == "queued"


def test_knowledge_ingestion_uses_private_object_storage() -> None:
    from app.knowledge.routes import get_ingestion_service

    service = get_ingestion_service()

    assert service.storage.root_dir == settings.knowledge_storage_root_path


def test_ingestion_status_requires_expert_and_returns_tenant_scoped_job() -> None:
    app = create_app()
    from app.knowledge.routes import get_ingestion_service

    app.dependency_overrides[get_ingestion_service] = lambda: FakeIngestionService()
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id="operator", tenant_id="t1", roles=frozenset([Role.OPERATOR])
    )
    assert client.get("/api/v1/knowledge/ingestions/job-1").status_code == 403

    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id="expert", tenant_id="t1", roles=frozenset([Role.EXPERT])
    )
    response = client.get("/api/v1/knowledge/ingestions/job-1")
    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-1",
        "status": "completed",
        "attempts": 1,
        "last_error": None,
    }


@pytest.mark.asyncio
async def test_ingestion_job_uses_the_prevalidated_stored_document() -> None:
    from app.knowledge.service import build_ingestion_handler

    class Storage:
        def retrieve(self, path):
            assert path == "doc-1.txt"
            return b"VietGAP policy"

    class Processor:
        def __init__(self):
            self.kwargs = None

        def ingest(self, **kwargs):
            self.kwargs = kwargs

    processor = Processor()
    handler = build_ingestion_handler(Storage(), processor)
    await handler(Job("j1", "knowledge.ingest", "k1", {
        "storage_path": "doc-1.txt", "filename": "policy.txt", "content_type": "text/plain", "tenant_id": "t1", "domain_id": "agriculture",
    }))
    assert processor.kwargs["storage_path"] == "doc-1.txt"


def test_runtime_handlers_can_be_created_for_the_worker_process() -> None:
    from app.knowledge.service import build_runtime_handlers

    handlers = build_runtime_handlers()

    assert "knowledge.ingest" in handlers
