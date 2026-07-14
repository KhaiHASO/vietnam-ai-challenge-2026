import pytest
from ai_layer.rag.memory.models import MemoryScope, Turn
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

def user_turn(content: str) -> Turn:
    return Turn(role="user", content=content)

@pytest.mark.asyncio
async def test_memory_never_crosses_user_scope(memory_service) -> None:
    await memory_service.append_turn(scope("user-a"), user_turn("Ruộng của tôi ở Đồng Tháp"))
    context = await memory_service.load_context(scope("user-b"))
    assert context.recent_turns == []


@pytest.mark.asyncio
async def test_working_memory_is_keyed_by_conversation_revision(memory_service) -> None:
    revision_one = scope("user-a")
    revision_two = revision_one.model_copy(update={"conversation_revision": 2})
    await memory_service.append_turn(revision_one, user_turn("revision one"))
    assert (await memory_service.load_context(revision_two)).recent_turns == []


@pytest.mark.asyncio
async def test_confirmed_long_term_fact_follows_user_across_sessions(memory_service) -> None:
    original = scope("user-a")
    proposal = await memory_service.propose_fact(
        original, key="location", value="Đồng Tháp",
        source_type="user_message", source_id="msg-1",
    )
    await memory_service.confirm_fact(original, proposal.fact.fact_id, consent=True)
    other_session = original.model_copy(
        update={"session_id": "session-2", "conversation_revision": 0}
    )
    assert [fact.value for fact in (await memory_service.load_context(other_session)).facts] == ["Đồng Tháp"]
