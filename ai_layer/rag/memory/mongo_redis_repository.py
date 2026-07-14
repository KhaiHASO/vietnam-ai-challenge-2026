"""Durable fact storage in MongoDB; revision-scoped working memory in Redis."""

from __future__ import annotations

from typing import Any

from .models import Fact, FactStatus, MemoryScope, Turn


class MongoRedisMemoryRepository:
    def __init__(self, *, redis_client: Any, facts_collection: Any, ttl_seconds: int = 86_400) -> None:
        if ttl_seconds <= 0:
            raise ValueError("Memory TTL must be positive")
        self.redis = redis_client
        self.facts = facts_collection
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _working_key(scope: MemoryScope, kind: str) -> str:
        return ":".join(("rag", "memory", "v1", kind, scope.tenant_id, scope.domain_id, scope.user_id, scope.session_id, str(scope.conversation_revision)))

    @staticmethod
    def _fact_filter(scope: MemoryScope) -> dict[str, str]:
        return {"tenant_id": scope.tenant_id, "domain_id": scope.domain_id, "user_id": scope.user_id}

    async def append_turn(self, scope: MemoryScope, turn: Turn) -> None:
        key = self._working_key(scope, "turns")
        await self.redis.rpush(key, turn.model_dump_json())
        await self.redis.expire(key, self.ttl_seconds)

    async def fetch_recent_turns(self, scope: MemoryScope) -> list[Turn]:
        raw_turns = await self.redis.lrange(self._working_key(scope, "turns"), 0, -1)
        return [Turn.model_validate_json(item.decode() if isinstance(item, bytes) else item) for item in raw_turns]

    async def get_rolling_summary(self, scope: MemoryScope) -> str | None:
        value = await self.redis.get(self._working_key(scope, "summary"))
        return value.decode() if isinstance(value, bytes) else value

    async def set_rolling_summary(self, scope: MemoryScope, summary: str) -> None:
        key = self._working_key(scope, "summary")
        await self.redis.set(key, summary, ex=self.ttl_seconds)

    def _require_facts(self) -> Any:
        if self.facts is None:
            raise RuntimeError("Mongo facts collection is required")
        return self.facts

    async def list_facts(self, scope: MemoryScope) -> list[Fact]:
        cursor = self._require_facts().find(self._fact_filter(scope), {"_id": 0, "tenant_id": 0, "domain_id": 0, "user_id": 0})
        docs = await cursor.to_list(length=1_000)
        return [Fact.model_validate(doc) for doc in docs]

    async def get_fact(self, scope: MemoryScope, fact_id: str) -> Fact | None:
        document = await self._require_facts().find_one({**self._fact_filter(scope), "fact_id": fact_id}, {"_id": 0, "tenant_id": 0, "domain_id": 0, "user_id": 0})
        return Fact.model_validate(document) if document else None

    async def save_fact(self, scope: MemoryScope, fact: Fact) -> None:
        document = {**fact.model_dump(mode="python"), **self._fact_filter(scope)}
        await self._require_facts().update_one({**self._fact_filter(scope), "fact_id": fact.fact_id}, {"$set": document}, upsert=True)

    async def forget_facts(self, scope: MemoryScope, keys: set[str]) -> None:
        if not keys:
            return
        await self._require_facts().update_many(
            {**self._fact_filter(scope), "key": {"$in": sorted(keys)}, "status": {"$in": [FactStatus.CONFIRMED.value, FactStatus.PENDING_CONFIRMATION.value]}},
            {"$set": {"status": FactStatus.FORGOTTEN.value}},
        )
