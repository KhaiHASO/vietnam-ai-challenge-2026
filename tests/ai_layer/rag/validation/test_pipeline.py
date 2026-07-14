import hashlib

from ai_layer.rag.contracts import (
    AnswerStatus,
    Citation,
    CopilotAnswer,
    CopilotRequest,
    Evidence,
)
from ai_layer.rag.validation import (
    AssuranceAction,
    AssurancePipeline,
    CitationValidator,
    EvidencePolicy,
    EvidenceValidator,
    InputValidator,
)


def request() -> CopilotRequest:
    return CopilotRequest(
        tenant_id="single", domain_id="agriculture", user_id="u1", session_id="s1",
        query="Bệnh đạo ôn là gì?",
    )


def evidence() -> Evidence:
    content = "Bệnh đạo ôn gây vết cháy trên lá lúa."
    return Evidence(
        chunk_id="chunk-1", document_id="doc-1", source_uri="kb://doc-1",
        tenant_id="single", domain_id="agriculture", index_revision="idx-1",
        score=0.92, content=content, checksum=hashlib.sha256(content.encode()).hexdigest(),
    )


def pipeline() -> AssurancePipeline:
    return AssurancePipeline(InputValidator(), EvidenceValidator(), CitationValidator())


def test_pipeline_requests_retrieval_rewrite_then_typed_abstention() -> None:
    first = pipeline().run(
        request=request(), evidence=[], retrieval_attempt=0, max_retrieval_attempts=1
    )
    assert first.action == AssuranceAction.RETRIEVAL_REWRITE
    final = pipeline().run(
        request=request(), evidence=[], retrieval_attempt=1, max_retrieval_attempts=1
    )
    assert final.action == AssuranceAction.ABSTAIN
    assert final.answer.status == AnswerStatus.ABSTAINED
    assert final.answer.abstention.code == "INSUFFICIENT_EVIDENCE"


def test_pipeline_requests_repair_then_abstains_for_uncited_claim() -> None:
    uncited = CopilotAnswer(status=AnswerStatus.ANSWERED, answer="Bệnh đạo ôn gây cháy lá.")
    first = pipeline().run(
        request=request(), evidence=[evidence()], answer=uncited,
        evidence_policy=EvidencePolicy(active_index_revision="idx-1"), repair_attempt=0,
    )
    assert first.action == AssuranceAction.REPAIR
    final = pipeline().run(
        request=request(), evidence=[evidence()], answer=uncited,
        evidence_policy=EvidencePolicy(active_index_revision="idx-1"), repair_attempt=1,
    )
    assert final.action == AssuranceAction.ABSTAIN
    assert final.answer.abstention.code == "VALIDATION_FAILED"


def test_pipeline_passes_supported_answer_and_marks_it_cache_eligible() -> None:
    supported = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Bệnh đạo ôn gây vết cháy trên lá lúa [1].",
        citations=[Citation(chunk_id="chunk-1", inline_reference="[1]")],
    )
    outcome = pipeline().run(
        request=request(), evidence=[evidence()], answer=supported,
        evidence_policy=EvidencePolicy(active_index_revision="idx-1"),
    )
    assert outcome.action == AssuranceAction.PASS
    assert outcome.answer.validators_passed is True


def test_pipeline_routes_high_risk_action_to_typed_approval() -> None:
    content = "Chỉ sử dụng thuốc theo hướng dẫn chuyên gia."
    custom_evidence = Evidence(
        chunk_id="chunk-1", document_id="doc-1", source_uri="kb://doc-1",
        tenant_id="single", domain_id="agriculture", index_revision="idx-1",
        score=0.92, content=content, checksum=hashlib.sha256(content.encode()).hexdigest(),
    )
    supported = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Chỉ sử dụng thuốc theo hướng dẫn chuyên gia [1].",
        citations=[Citation(chunk_id="chunk-1", inline_reference="[1]")],
    )
    outcome = pipeline().run(
        request=request(), evidence=[custom_evidence], answer=supported,
        evidence_policy=EvidencePolicy(active_index_revision="idx-1"),
        action_requires_approval=True,
    )
    assert outcome.action == AssuranceAction.APPROVAL
    assert outcome.answer.status == AnswerStatus.APPROVAL_REQUIRED
    assert outcome.answer.approval.required is True
