import pytest
import hashlib
from ai_layer.rag.validation import AssurancePipeline, CitationValidator, EvidenceValidator, InputValidator
from ai_layer.rag.contracts import Evidence, ModelSignal
from ai_layer.rag.registries import RegistryCatalog
from ai_layer.rag.service import RAGService
from ai_layer.rag.contracts.request import CopilotRequest
from unittest.mock import AsyncMock

@pytest.fixture
def rag_service():
    gateway = AsyncMock()
    gateway.last_metadata = {"degraded": False}
    triage = AsyncMock()
    triage.analyze.return_value = ModelSignal(
        risk_level="low", priority=0.2, requires_review=False, confidence=0.9,
        model_version="test", latency_ms=1, engine_status="ok",
    )
    service = RAGService(
        catalog=RegistryCatalog(),
        cache=AsyncMock(),
        gateway=gateway,
        runner=AsyncMock(),
        validator=AssurancePipeline(InputValidator(), EvidenceValidator(), CitationValidator()),
        triage=triage,
    )
    service.cache.get.return_value = None
    return service

@pytest.fixture
def request_obj():
    return CopilotRequest(
        tenant_id="t1", domain_id="agriculture", user_id="u1", session_id="s1", query="hello"
    )

@pytest.mark.asyncio
async def test_service_abstains_when_retrieval_remains_insufficient(rag_service, request_obj) -> None:
    # Bounded runner fails to retrieve anything
    rag_service.runner.run.return_value = []
    
    answer = await rag_service.ask(request_obj)
    
    assert answer.status == "abstained"
    assert answer.abstention.code == "INSUFFICIENT_EVIDENCE"
    assert rag_service.gateway.generate.call_count == 0

@pytest.mark.asyncio
async def test_only_validated_answer_is_written_to_cache(rag_service, request_obj) -> None:
    content = "This is a safe generated answer."
    rag_service.runner.run.return_value = [
        Evidence(
            chunk_id="c1", document_id="d1", source_uri="kb://d1",
            tenant_id="t1", domain_id="agriculture", index_revision="default",
            score=0.9, content=content, checksum=hashlib.sha256(content.encode()).hexdigest(),
        )
    ]
    rag_service.gateway.generate.return_value = "This is a safe generated answer [1]."
    
    answer = await rag_service.ask(request_obj)
    
    assert answer.status == "answered"
    assert rag_service.cache.set.call_count == 1
    assert answer.validators_passed is True


@pytest.mark.asyncio
async def test_stream_never_emits_token_delta_for_unvalidated_abstention(request_obj) -> None:
    from ai_layer.rag.service import RAGService
    from unittest.mock import AsyncMock

    runner = AsyncMock()
    runner.run.return_value = []
    gateway = AsyncMock()
    gateway.last_metadata = {"degraded": False}
    triage = AsyncMock()
    triage.analyze.return_value = ModelSignal(
        risk_level="low", priority=0.2, requires_review=False, confidence=0.9,
        model_version="test", latency_ms=1, engine_status="ok",
    )
    service = RAGService(
        gateway=gateway,
        runner=runner,
        validator=AssurancePipeline(InputValidator(), EvidenceValidator(), CitationValidator()),
        triage=triage,
    )
    events = [event async for event in service.stream(request_obj)]
    assert "token.delta" not in {event.event_type.value for event in events}
    assert events[-1].event_type.value == "message.abstained"
