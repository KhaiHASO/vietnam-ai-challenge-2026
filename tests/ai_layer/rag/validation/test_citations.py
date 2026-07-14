import pytest
import hashlib
from ai_layer.rag.validation.citations import CitationValidator
from ai_layer.rag.contracts.answer import CopilotAnswer, AnswerStatus
from ai_layer.rag.contracts.memory import Citation, Evidence

@pytest.fixture
def citation_validator():
    return CitationValidator()

def test_citation_from_another_tenant_is_rejected(citation_validator) -> None:
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="ok",
        citations=[Citation(chunk_id="chunk-1", inline_reference="[1]")]
    )
    foreign = Evidence(
        chunk_id="chunk-1",
        document_id="doc-1",
        source_uri="http",
        tenant_id="other",
        domain_id="agriculture",
        index_revision="i",
        score=0.9,
        content="abc",
        checksum=hashlib.sha256(b"abc").hexdigest()
    )
    
    result = citation_validator.validate(answer, [foreign], tenant_id="single", domain_id="agriculture")
    assert result.passed is False
    assert result.code == "CROSS_TENANT_CITATION"


def test_uncited_factual_answer_is_rejected(citation_validator) -> None:
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Bệnh đạo ôn gây vết cháy trên lá lúa.",
    )
    content = "Bệnh đạo ôn gây vết cháy trên lá lúa."
    evidence = Evidence(
        chunk_id="chunk-1", document_id="doc-1", source_uri="kb://doc-1",
        tenant_id="single", domain_id="agriculture", index_revision="idx-1",
        score=0.9, content=content, checksum=hashlib.sha256(content.encode()).hexdigest(),
    )
    result = citation_validator.validate(
        answer, [evidence], tenant_id="single", domain_id="agriculture",
        active_index_revision="idx-1",
    )
    assert result.passed is False
    assert result.code == "UNCITED_FACTUAL_CLAIM"


def test_citation_that_does_not_support_the_claim_is_rejected(citation_validator) -> None:
    content = "Lúa cần nước trong giai đoạn làm đòng."
    evidence = Evidence(
        chunk_id="chunk-1", document_id="doc-1", source_uri="kb://doc-1",
        tenant_id="single", domain_id="agriculture", index_revision="idx-1",
        score=0.9, content=content, checksum=hashlib.sha256(content.encode()).hexdigest(),
    )
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Bệnh đạo ôn do vi khuẩn gây ra [1].",
        citations=[Citation(chunk_id="chunk-1", inline_reference="[1]")],
    )
    result = citation_validator.validate(
        answer, [evidence], tenant_id="single", domain_id="agriculture",
        active_index_revision="idx-1",
    )
    assert result.passed is False
    assert result.code == "UNSUPPORTED_CLAIM"
