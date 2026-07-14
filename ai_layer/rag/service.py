import re
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Any
from uuid import uuid4

from ai_layer.rag.cache.backend import InMemoryCacheBackend
from ai_layer.rag.cache.keys import CacheKeyInput, build_response_cache_key
from ai_layer.rag.cache.policy import CacheDecisionContext, ResponseCachePolicy
from ai_layer.rag.contracts.answer import (
    Abstention,
    AbstentionCode,
    AnswerStatus,
    CopilotAnswer,
    RecoveryAction,
    VersionSet,
)
from ai_layer.rag.contracts.events import CopilotEvent, CopilotEventType, RiskLevel
from ai_layer.rag.contracts.memory import Citation, Evidence
from ai_layer.rag.contracts.request import CopilotRequest
from ai_layer.rag.memory.models import MemoryScope, Turn
from ai_layer.rag.memory.repository import InMemoryMemoryRepository
from ai_layer.rag.memory.service import MemoryService
from ai_layer.rag.providers.gateway import ProviderError
from ai_layer.rag.registries.catalog import RegistryCatalog, UnknownDomainError
from ai_layer.rag.tools.pytorch_triage import PyTorchTriage
from ai_layer.rag.validation import (
    AssuranceAction,
    AssurancePipeline,
    CitationValidator,
    EvidencePolicy,
    EvidenceValidator,
    InputValidator,
)


class RAGService:
    def __init__(
        self,
        catalog=None,
        memory=None,
        cache=None,
        gateway=None,
        runner=None,
        validator=None,
        *,
        triage=None,
        ingestion_service=None,
    ) -> None:
        self.catalog = catalog or RegistryCatalog()
        self.memory = memory or MemoryService(InMemoryMemoryRepository(), self.catalog)
        self.cache = cache or InMemoryCacheBackend()
        self.gateway = gateway
        self.runner = runner
        self.validator = validator or AssurancePipeline(
            InputValidator(), EvidenceValidator(), CitationValidator()
        )
        self.triage = triage or PyTorchTriage()
        self.ingestion_service = ingestion_service
        self.cache_policy = ResponseCachePolicy()

    async def ask(self, request: CopilotRequest) -> CopilotAnswer:
        input_result = self.validator.input_val.validate(request)
        if not input_result.passed:
            return self.validator.run(request=request, evidence=[]).answer

        try:
            resolved = self.catalog.resolve_request_context(
                request.domain_id, request.tenant_id
            )
        except UnknownDomainError:
            return self._abstained(
                request,
                AbstentionCode.OUT_OF_DOMAIN,
                "Miền kiến thức được yêu cầu chưa được cấu hình.",
            )

        manifest = resolved.manifest
        versions = {
            **resolved.versions,
            "knowledge_index": resolved.versions.get("knowledge_index", "default"),
            "provider_model": resolved.versions.get("provider", "unresolved"),
        }
        scope = MemoryScope(
            tenant_id=request.tenant_id,
            domain_id=request.domain_id,
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_revision=request.expected_conversation_revision,
        )
        memory_context = await self.memory.load_context(scope)
        cache_key = self._cache_key(request, versions)
        cached = await self.cache.get(cache_key)
        if cached:
            try:
                answer = CopilotAnswer.model_validate_json(cached)
                answer.validators_passed = True
                return answer
            except Exception:
                await self.cache.delete(cache_key)

        triage_signal = await self.triage.analyze(
            request.query, domain=request.domain_id
        )
        route_class = self._route_class(request, triage_signal)
        evidence = (
            await self.runner.run(request, route_class=route_class)
            if self.runner is not None
            else []
        )
        evidence_policy = EvidencePolicy(
            minimum_score=manifest.retrieval.similarity_threshold,
            minimum_source_diversity=manifest.retrieval.minimum_source_diversity,
            maximum_age_days=manifest.retrieval.maximum_age_days,
        )
        evidence_gate = self.validator.run(
            request=request,
            evidence=evidence,
            memory_facts=memory_context.facts,
            evidence_policy=evidence_policy,
            retrieval_attempt=1,
            max_retrieval_attempts=1,
        )
        if evidence_gate.action != AssuranceAction.PASS:
            return evidence_gate.answer
        if self.gateway is None:
            return self._abstained(
                request,
                AbstentionCode.PROVIDER_UNAVAILABLE,
                "Dịch vụ mô hình hiện chưa sẵn sàng.",
                attempted_sources=len(evidence),
            )

        try:
            generated_text = await self.gateway.generate(
                request.query,
                evidence,
                high_risk=triage_signal.requires_review,
                domain_policy=manifest,
            )
        except ProviderError:
            return self._abstained(
                request,
                AbstentionCode.PROVIDER_UNAVAILABLE,
                "Dịch vụ mô hình hiện chưa sẵn sàng.",
                attempted_sources=len(evidence),
            )

        draft = self._draft(generated_text, evidence, versions, triage_signal)
        outcome = self.validator.run(
            request=request,
            evidence=evidence,
            answer=draft,
            memory_facts=memory_context.facts,
            evidence_policy=evidence_policy,
            high_risk=triage_signal.risk_level == RiskLevel.HIGH,
            action_requires_approval=triage_signal.requires_review,
            repair_attempt=0,
            max_repair_attempts=1,
        )
        if outcome.action == AssuranceAction.REPAIR:
            try:
                repaired_text = await self.gateway.generate(
                    request.query
                    + "\nTrả lời lại với trích dẫn dạng [1], [2] và chỉ dùng dữ liệu trong nguồn.",
                    evidence,
                    high_risk=triage_signal.requires_review,
                    domain_policy=manifest,
                )
            except ProviderError:
                repaired_text = ""
            repaired = self._draft(repaired_text, evidence, versions, triage_signal)
            outcome = self.validator.run(
                request=request,
                evidence=evidence,
                answer=repaired,
                memory_facts=memory_context.facts,
                evidence_policy=evidence_policy,
                high_risk=triage_signal.risk_level == RiskLevel.HIGH,
                action_requires_approval=triage_signal.requires_review,
                repair_attempt=1,
                max_repair_attempts=1,
            )

        final_answer = outcome.answer or draft
        pii = bool(input_result.metadata.get("contains_pii"))
        degraded = bool(getattr(self.gateway, "last_metadata", {}).get("degraded"))
        cache_context = CacheDecisionContext(
            stream_completed=True,
            exact_scope=True,
            contains_pii=pii,
            sensitive_context=bool(memory_context.facts),
            provider_degraded=degraded,
            high_risk=triage_signal.risk_level == RiskLevel.HIGH,
            approval_required=final_answer.status == AnswerStatus.APPROVAL_REQUIRED,
        )
        if self.cache_policy.is_eligible(final_answer, [triage_signal], cache_context):
            await self.cache.set(cache_key, final_answer.model_dump_json(), ttl_seconds=300)

        await self.memory.append_turn(
            scope,
            Turn(
                role="user",
                content=request.query,
                sequence=request.expected_conversation_revision * 2,
                trace_id=final_answer.trace_id,
            ),
        )
        await self.memory.append_turn(
            scope,
            Turn(
                role="assistant",
                content=final_answer.answer or final_answer.abstention.user_message,
                sequence=request.expected_conversation_revision * 2 + 1,
                trace_id=final_answer.trace_id,
            ),
        )
        return final_answer

    async def process(self, request: CopilotRequest) -> CopilotAnswer:
        return await self.ask(request)

    async def stream(self, request: CopilotRequest) -> AsyncIterator[CopilotEvent]:
        sequence = 0
        message_id = str(uuid4())
        trace_id = request.idempotency_key

        def event(kind: CopilotEventType, payload: dict[str, Any]) -> CopilotEvent:
            nonlocal sequence
            value = CopilotEvent(
                event_id=f"evt-{message_id}-{sequence}",
                sequence=sequence,
                session_id=request.session_id,
                message_id=message_id,
                occurred_at=datetime.now(timezone.utc),
                trace_id=trace_id,
                event_type=kind,
                payload=payload,
            )
            sequence += 1
            return value

        yield event(CopilotEventType.MESSAGE_STARTED, {"status": "started"})
        answer = await self.ask(request)
        if answer.model_signals:
            signal = answer.model_signals[0]
            yield event(
                CopilotEventType.ROUTE_SELECTED,
                {
                    "risk_level": signal.risk_level.value,
                    "requires_review": signal.requires_review,
                    "engine_status": signal.engine_status,
                },
            )
        if answer.status == AnswerStatus.ABSTAINED:
            yield event(
                CopilotEventType.MESSAGE_ABSTAINED,
                answer.model_dump(mode="json"),
            )
            return
        if answer.answer:
            yield event(CopilotEventType.TOKEN_DELTA, {"text": answer.answer})
        for citation in answer.citations:
            yield event(
                CopilotEventType.CITATION_ADDED,
                citation.model_dump(mode="json"),
            )
        if answer.status == AnswerStatus.APPROVAL_REQUIRED:
            yield event(
                CopilotEventType.APPROVAL_REQUIRED,
                answer.approval.model_dump(mode="json"),
            )
        yield event(
            CopilotEventType.MESSAGE_COMPLETED,
            answer.model_dump(mode="json"),
        )

    def ingest(self, request):
        if self.ingestion_service is None:
            raise RuntimeError("Ingestion service is not configured")
        return self.ingestion_service.ingest(request)

    @classmethod
    def build_durable(cls, *, redis_client, facts_collection):
        """Create the production RAG composition without leaking internals to FastAPI."""
        from ai_layer.rag.cache.backend import RedisCacheBackend
        from ai_layer.rag.core.dependencies import build_rag_service
        from ai_layer.rag.memory.mongo_redis_repository import MongoRedisMemoryRepository
        from ai_layer.rag.memory.service import MemoryService
        from ai_layer.rag.registries.catalog import RegistryCatalog

        catalog = RegistryCatalog()
        memory = MemoryService(
            MongoRedisMemoryRepository(
                redis_client=redis_client,
                facts_collection=facts_collection,
            ),
            catalog,
        )
        return build_rag_service(memory=memory, cache=RedisCacheBackend(redis_client))

    @staticmethod
    def build_default():
        from ai_layer.rag.core.dependencies import get_rag_service

        return get_rag_service()

    @staticmethod
    def build_memory_scope(**values):
        from ai_layer.rag.memory.models import MemoryScope

        return MemoryScope(**values)

    @staticmethod
    def build_ingestion_handlers(*, storage, lexical_root: str | Path) -> dict[str, Any]:
        """Own the RAG ingestion graph while the backend owns job transport only."""
        from ai_layer.rag.chunkers.langchain_chunker import LangchainChunker
        from ai_layer.rag.core.dependencies import get_vector_store
        from ai_layer.rag.ingestion.service import IngestionService
        from ai_layer.rag.retrieval.lexical import LexicalRetriever

        handlers: dict[str, Any] = {}
        lexical_root = Path(lexical_root)

        async def ingest(job) -> None:
            domain_id = str(job.payload["domain_id"])
            handler = handlers.get(domain_id)
            if handler is None:
                processor = IngestionService(
                    storage=storage,
                    chunker=LangchainChunker(),
                    vector_store=get_vector_store(domain_id),
                    lexical_store=LexicalRetriever(lexical_root / f"{domain_id}.json"),
                )

                async def handler(current_job) -> None:
                    payload = current_job.payload
                    content = storage.retrieve(str(payload["storage_path"]))
                    processor.ingest(
                        original_filename=str(payload["filename"]),
                        content=content,
                        content_type=str(payload["content_type"]),
                        metadata={
                            "tenant_id": payload["tenant_id"],
                            "domain_id": payload["domain_id"],
                        },
                        storage_path=str(payload["storage_path"]),
                    )

                handlers[domain_id] = handler
            await handler(job)

        return {"knowledge.ingest": ingest}

    @staticmethod
    def _route_class(request: CopilotRequest, signal) -> str:
        if signal.risk_level == RiskLevel.HIGH or signal.requires_review:
            return "complex"
        return "fast" if len(request.query.split()) <= 3 else "standard"

    @staticmethod
    def _draft(text: str, evidence: list[Evidence], versions: dict[str, str], signal) -> CopilotAnswer:
        citations = []
        for index, chunk in enumerate(evidence, start=1):
            marker = f"[{index}]"
            if marker in text:
                citations.append(Citation(chunk_id=chunk.chunk_id, inline_reference=marker))
        return CopilotAnswer(
            status=AnswerStatus.ANSWERED,
            answer=text,
            citations=citations,
            versions=VersionSet(
                domain_pack=versions.get("domain_pack", "unknown"),
                knowledge_index=versions.get("knowledge_index", "unknown"),
                prompt=versions.get("prompt", "unknown"),
                policy=versions.get("policy", "unknown"),
                provider_model=versions.get("provider_model", "unknown"),
                validator_bundle=versions.get("validator_bundle", "unknown"),
            ),
            model_signals=[signal],
        )

    @staticmethod
    def _cache_key(request: CopilotRequest, versions: dict[str, str]) -> str:
        return build_response_cache_key(
            CacheKeyInput(
                tenant_id=request.tenant_id,
                domain_id=request.domain_id,
                domain_pack=versions.get("domain_pack", "unknown"),
                knowledge_index=versions.get("knowledge_index", "unknown"),
                prompt_version=versions.get("prompt", "unknown"),
                policy_version=versions.get("policy", "unknown"),
                provider_id=versions.get("provider", "unknown"),
                model_revision=versions.get("provider_model", "unknown"),
                validator_bundle=versions.get("validator_bundle", "unknown"),
                query=request.query,
                user_id=request.user_id,
                session_id=request.session_id,
                conversation_revision=request.expected_conversation_revision,
            )
        )

    @staticmethod
    def _abstained(
        request: CopilotRequest,
        code: AbstentionCode,
        message: str,
        attempted_sources: int = 0,
    ) -> CopilotAnswer:
        return CopilotAnswer(
            status=AnswerStatus.ABSTAINED,
            abstention=Abstention(
                code=code,
                user_message=message,
                attempted_sources=attempted_sources,
                recovery_actions=[
                    RecoveryAction.REFINE_QUESTION,
                    RecoveryAction.UPLOAD_DOCUMENT,
                    RecoveryAction.ASK_EXPERT,
                ],
                expert_handoff_available=True,
            ),
            trace_id=request.idempotency_key,
        )


def get_rag_service() -> RAGService:
    from ai_layer.rag.core.dependencies import get_rag_service as resolve

    return resolve()
