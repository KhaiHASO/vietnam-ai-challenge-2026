from typing import Protocol

from .models import Fact, FactStatus, MemoryScope, Turn


class MemoryRepository(Protocol):
    async def append_turn(self, scope: MemoryScope, turn: Turn) -> None: ...
    async def fetch_recent_turns(self, scope: MemoryScope) -> list[Turn]: ...
    async def get_rolling_summary(self, scope: MemoryScope) -> str | None: ...
    async def set_rolling_summary(self, scope: MemoryScope, summary: str) -> None: ...
    async def list_facts(self, scope: MemoryScope) -> list[Fact]: ...
    async def get_fact(self, scope: MemoryScope, fact_id: str) -> Fact | None: ...
    async def save_fact(self, scope: MemoryScope, fact: Fact) -> None: ...
    async def forget_facts(self, scope: MemoryScope, keys: set[str]) -> None: ...


MemoryRepositoryProtocol = MemoryRepository


class InMemoryMemoryRepository:
    def __init__(self) -> None:
        self._turns: dict[str, list[Turn]] = {}
        self._summaries: dict[str, str] = {}
        self._facts: dict[str, list[Fact]] = {}

    @staticmethod
    def _working_scope_key(scope: MemoryScope) -> str:
        return ":".join(
            (
                scope.tenant_id,
                scope.domain_id,
                scope.user_id,
                scope.session_id,
                str(scope.conversation_revision),
            )
        )

    @staticmethod
    def _fact_scope_key(scope: MemoryScope) -> str:
        return ":".join((scope.tenant_id, scope.domain_id, scope.user_id))

    async def append_turn(self, scope: MemoryScope, turn: Turn) -> None:
        self._turns.setdefault(self._working_scope_key(scope), []).append(turn)

    async def fetch_recent_turns(self, scope: MemoryScope) -> list[Turn]:
        return list(self._turns.get(self._working_scope_key(scope), []))

    async def get_rolling_summary(self, scope: MemoryScope) -> str | None:
        return self._summaries.get(self._working_scope_key(scope))

    async def set_rolling_summary(self, scope: MemoryScope, summary: str) -> None:
        self._summaries[self._working_scope_key(scope)] = summary

    async def list_facts(self, scope: MemoryScope) -> list[Fact]:
        return list(self._facts.get(self._fact_scope_key(scope), []))

    async def get_fact(self, scope: MemoryScope, fact_id: str) -> Fact | None:
        return next(
            (fact for fact in await self.list_facts(scope) if fact.fact_id == fact_id),
            None,
        )

    async def save_fact(self, scope: MemoryScope, fact: Fact) -> None:
        key = self._fact_scope_key(scope)
        facts = self._facts.setdefault(key, [])
        for index, existing in enumerate(facts):
            if existing.fact_id == fact.fact_id:
                facts[index] = fact
                return
        facts.append(fact)

    async def forget_facts(self, scope: MemoryScope, keys: set[str]) -> None:
        for fact in await self.list_facts(scope):
            if fact.key in keys and fact.status in {
                FactStatus.CONFIRMED,
                FactStatus.PENDING_CONFIRMATION,
            }:
                fact.status = FactStatus.FORGOTTEN
                await self.save_fact(scope, fact)
