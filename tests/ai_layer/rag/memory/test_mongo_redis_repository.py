from ai_layer.rag.memory.models import MemoryScope, Turn
from ai_layer.rag.memory.mongo_redis_repository import MongoRedisMemoryRepository


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, list[str] | str] = {}

    async def rpush(self, key: str, value: str) -> None:
        self.values.setdefault(key, [])
        assert isinstance(self.values[key], list)
        self.values[key].append(value)

    async def expire(self, key: str, seconds: int) -> None:
        assert seconds > 0

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        value = self.values.get(key, [])
        assert isinstance(value, list)
        return value[start:] if end == -1 else value[start : end + 1]


async def test_working_memory_is_scoped_and_uses_a_ttl() -> None:
    redis = FakeRedis()
    repository = MongoRedisMemoryRepository(redis_client=redis, facts_collection=None, ttl_seconds=60)
    scope = MemoryScope(tenant_id="t1", domain_id="agriculture", user_id="u1", session_id="s1", conversation_revision=3)
    await repository.append_turn(scope, Turn(role="user", content="Độ ẩm đất bao nhiêu?"))
    assert [turn.content for turn in await repository.fetch_recent_turns(scope)] == ["Độ ẩm đất bao nhiêu?"]
    another_scope = scope.model_copy(update={"tenant_id": "t2"})
    assert await repository.fetch_recent_turns(another_scope) == []
