from fastapi.testclient import TestClient

from ai_layer.rag.memory.models import Fact, FactStatus, MemoryScope
from app.auth.contracts import Principal, Role
from app.auth.dependencies import get_current_user
from app.copilot.memory_routes import get_memory_service
from app.main import create_app


class FakeMemoryService:
    def __init__(self) -> None:
        self.fact = Fact(
            fact_id="fact-1",
            key="crop",
            value="rice",
            source_type="user_message",
            source_message_id="message-1",
        )

    async def list_facts(self, scope: MemoryScope):
        assert scope.tenant_id == "t1"
        assert scope.user_id == "u1"
        return [self.fact]

    async def confirm_fact(self, scope: MemoryScope, fact_id: str, *, consent: bool):
        assert fact_id == self.fact.fact_id
        self.fact.status = FactStatus.CONFIRMED if consent else FactStatus.REJECTED
        self.fact.consent = consent
        return self.fact

    async def forget_fact(self, scope: MemoryScope, fact_id: str):
        assert fact_id == self.fact.fact_id
        self.fact.status = FactStatus.FORGOTTEN
        return self.fact


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: Principal(
        user_id="u1", tenant_id="t1", roles=frozenset([Role.OPERATOR])
    )
    app.dependency_overrides[get_memory_service] = lambda: FakeMemoryService()
    return TestClient(app)


def test_memory_list_is_scoped_to_the_authenticated_user() -> None:
    response = _client().get("/api/v1/copilot/memory?domain_id=agriculture")

    assert response.status_code == 200
    assert response.json()["facts"][0]["fact_id"] == "fact-1"
    assert response.json()["facts"][0]["value"] == "rice"


def test_memory_confirmation_and_deletion_are_typed() -> None:
    client = _client()

    confirmed = client.patch(
        "/api/v1/copilot/memory/fact-1?domain_id=agriculture",
        json={"consent": True},
    )
    forgotten = client.delete("/api/v1/copilot/memory/fact-1?domain_id=agriculture")

    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert forgotten.status_code == 200
    assert forgotten.json()["status"] == "forgotten"
