import pytest
from datetime import datetime, timedelta, timezone

from ai_layer.rag.memory.models import MemoryScope
from ai_layer.rag.memory.repository import InMemoryMemoryRepository
from ai_layer.rag.memory.service import MemoryService
from ai_layer.rag.registries.catalog import RegistryCatalog

@pytest.fixture
def memory_service():
    repo = InMemoryMemoryRepository()
    catalog = RegistryCatalog()
    return MemoryService(repository=repo, catalog=catalog)

def scope(user_id: str) -> MemoryScope:
    return MemoryScope(
        tenant_id="tenant_1",
        domain_id="agriculture",
        session_id="session_1",
        user_id=user_id,
        conversation_revision=1
    )

@pytest.mark.asyncio
async def test_retrieved_document_cannot_write_user_fact(memory_service) -> None:
    proposal = await memory_service.propose_fact(
        scope("user-a"), 
        key="location", 
        value="Đồng Tháp",
        source_type="retrieved_document", 
        source_id="chunk-7",
    )
    assert proposal.status == "rejected"

@pytest.mark.asyncio
async def test_user_message_can_write_user_fact(memory_service) -> None:
    proposal = await memory_service.propose_fact(
        scope("user-a"), 
        key="location", 
        value="Đồng Tháp",
        source_type="user_message", 
        source_id="msg-1",
    )
    assert proposal.status == "pending_confirmation"


@pytest.mark.asyncio
async def test_fact_requires_confirmation_and_expired_facts_are_not_loaded(memory_service) -> None:
    proposal = await memory_service.propose_fact(
        scope("user-a"), key="location", value="Đồng Tháp",
        source_type="user_message", source_id="msg-1",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    before = await memory_service.load_context(scope("user-a"))
    assert before.facts == []

    confirmed = await memory_service.confirm_fact(
        scope("user-a"), proposal.fact.fact_id, consent=True
    )
    assert confirmed.status == "confirmed"
    after = await memory_service.load_context(scope("user-a"))
    assert [fact.key for fact in after.facts] == ["location"]

    confirmed.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    expired = await memory_service.load_context(scope("user-a"))
    assert expired.facts == []


@pytest.mark.asyncio
async def test_unknown_domain_fails_closed_without_storing_fact(memory_service) -> None:
    unknown = scope("user-a").model_copy(update={"domain_id": "missing-domain"})
    proposal = await memory_service.propose_fact(
        unknown, key="anything", value="poison",
        source_type="user_message", source_id="msg-2",
    )
    assert proposal.status == "rejected"
    assert (await memory_service.load_context(unknown)).facts == []


@pytest.mark.asyncio
async def test_supersede_and_forget_preserve_history_but_hide_inactive_facts(memory_service) -> None:
    proposal = await memory_service.propose_fact(
        scope("user-a"), key="location", value="Đồng Tháp",
        source_type="user_message", source_id="msg-1",
    )
    await memory_service.confirm_fact(scope("user-a"), proposal.fact.fact_id, consent=True)
    replacement = await memory_service.supersede_fact(
        scope("user-a"), proposal.fact.fact_id, value="An Giang", source_message_id="msg-2"
    )
    await memory_service.confirm_fact(scope("user-a"), replacement.fact_id, consent=True)
    assert [fact.value for fact in (await memory_service.load_context(scope("user-a"))).facts] == ["An Giang"]

    await memory_service.forget_facts(scope("user-a"), keys={"location"})
    assert (await memory_service.load_context(scope("user-a"))).facts == []
