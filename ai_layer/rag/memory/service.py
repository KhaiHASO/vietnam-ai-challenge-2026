from datetime import datetime, timezone
from typing import Any

from ai_layer.rag.registries.catalog import RegistryCatalog, UnknownDomainError

from .models import (
    Fact,
    FactProposal,
    FactStatus,
    MemoryContext,
    MemoryScope,
    TrustLevel,
    Turn,
)
from .repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository, catalog: RegistryCatalog):
        self.repository = repository
        self.catalog = catalog

    async def append_turn(self, scope: MemoryScope, turn: Turn) -> None:
        await self.repository.append_turn(scope, turn)

    async def set_rolling_summary(self, scope: MemoryScope, summary: str) -> None:
        await self.repository.set_rolling_summary(scope, summary)

    async def load_context(self, scope: MemoryScope) -> MemoryContext:
        now = datetime.now(timezone.utc)
        facts = [
            fact
            for fact in await self.repository.list_facts(scope)
            if fact.status == FactStatus.CONFIRMED
            and fact.consent
            and (fact.expires_at is None or fact.expires_at > now)
        ]
        return MemoryContext(
            conversation_revision=scope.conversation_revision,
            recent_turns=await self.repository.fetch_recent_turns(scope),
            rolling_summary=await self.repository.get_rolling_summary(scope),
            facts=facts,
        )

    async def list_facts(self, scope: MemoryScope) -> list[Fact]:
        """Return user-managed facts only; callers must still enforce the scope."""
        return await self.repository.list_facts(scope)

    async def propose_fact(
        self,
        scope: MemoryScope,
        key: str,
        value: Any,
        source_type: str,
        source_id: str,
        expires_at: datetime | None = None,
    ) -> FactProposal:
        if source_type != "user_message":
            return FactProposal(
                status=FactStatus.REJECTED,
                reason="Only explicit user messages may propose facts",
            )
        try:
            context = self.catalog.resolve_request_context(
                scope.domain_id, scope.tenant_id
            )
        except UnknownDomainError:
            return FactProposal(
                status=FactStatus.REJECTED,
                reason="Unknown domain memory policy",
            )
        if key not in context.manifest.memory_policy.allowed_fact_fields:
            return FactProposal(
                status=FactStatus.REJECTED,
                reason="Fact key is not allowed by the domain policy",
            )

        fact = Fact(
            key=key,
            value=value,
            source_type="user_message",
            source_message_id=source_id,
            expires_at=expires_at,
        )
        await self.repository.save_fact(scope, fact)
        return FactProposal(status=FactStatus.PENDING_CONFIRMATION, fact=fact)

    async def confirm_fact(
        self, scope: MemoryScope, fact_id: str, *, consent: bool
    ) -> Fact:
        fact = await self.repository.get_fact(scope, fact_id)
        if fact is None or fact.status != FactStatus.PENDING_CONFIRMATION:
            raise ValueError("Unknown or inactive fact")
        if not consent:
            fact.status = FactStatus.REJECTED
            await self.repository.save_fact(scope, fact)
            return fact
        fact.status = FactStatus.CONFIRMED
        fact.trust_level = TrustLevel.USER_CONFIRMED
        fact.consent = True
        fact.updated_at = datetime.now(timezone.utc)
        await self.repository.save_fact(scope, fact)
        return fact

    async def supersede_fact(
        self,
        scope: MemoryScope,
        fact_id: str,
        *,
        value: Any,
        source_message_id: str,
    ) -> Fact:
        previous = await self.repository.get_fact(scope, fact_id)
        if previous is None or previous.status != FactStatus.CONFIRMED:
            raise ValueError("Only a confirmed fact can be superseded")
        previous.status = FactStatus.SUPERSEDED
        previous.updated_at = datetime.now(timezone.utc)
        await self.repository.save_fact(scope, previous)
        replacement = Fact(
            key=previous.key,
            value=value,
            source_type="user_message",
            source_message_id=source_message_id,
            expires_at=previous.expires_at,
            supersedes_fact_id=previous.fact_id,
        )
        await self.repository.save_fact(scope, replacement)
        return replacement

    async def forget_facts(self, scope: MemoryScope, *, keys: set[str]) -> None:
        await self.repository.forget_facts(scope, keys)

    async def forget_fact(self, scope: MemoryScope, fact_id: str) -> Fact:
        fact = await self.repository.get_fact(scope, fact_id)
        if fact is None or fact.status in {FactStatus.FORGOTTEN, FactStatus.REJECTED}:
            raise ValueError("Unknown or inactive fact")
        fact.status = FactStatus.FORGOTTEN
        fact.updated_at = datetime.now(timezone.utc)
        await self.repository.save_fact(scope, fact)
        return fact
