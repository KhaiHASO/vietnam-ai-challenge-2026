import pytest
import hashlib
from datetime import datetime, timedelta, timezone

from ai_layer.rag.validation.evidence import EvidenceValidator
from ai_layer.rag.contracts.request import CopilotRequest
from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.validation.evidence import EvidencePolicy

@pytest.fixture
def evidence_validator():
    return EvidenceValidator()

def test_memory_fact_does_not_make_empty_evidence_sufficient(evidence_validator) -> None:
    req = CopilotRequest(
        tenant_id="t1", domain_id="agriculture", user_id="u1", session_id="s1",
        query="lúa"
    )
    result = evidence_validator.validate(request=req, evidence=[], memory_facts=["crop=rice"])
    assert result.passed is False
    assert result.code == "INSUFFICIENT_EVIDENCE"


def make_evidence(**updates) -> Evidence:
    content = updates.pop("content", "Bệnh đạo ôn gây vết cháy trên lá lúa.")
    values = {
        "chunk_id": "chunk-1", "document_id": "doc-1", "source_uri": "kb://doc-1",
        "tenant_id": "t1", "domain_id": "agriculture", "index_revision": "idx-2",
        "score": 0.91, "content": content,
        "checksum": hashlib.sha256(content.encode()).hexdigest(),
        "source_title": "Cẩm nang lúa", "document_status": "active",
    }
    values.update(updates)
    return Evidence(**values)


def request() -> CopilotRequest:
    return CopilotRequest(
        tenant_id="t1", domain_id="agriculture", user_id="u1", session_id="s1", query="đạo ôn"
    )


@pytest.mark.parametrize(
    ("evidence", "code"),
    [
        (make_evidence(tenant_id="other"), "EVIDENCE_SCOPE_MISMATCH"),
        (make_evidence(domain_id="finance"), "EVIDENCE_SCOPE_MISMATCH"),
        (make_evidence(index_revision="old"), "STALE_INDEX_REVISION"),
        (make_evidence(score=0.0), "WEAK_EVIDENCE"),
        (make_evidence(checksum="wrong"), "INVALID_EVIDENCE_CHECKSUM"),
        (make_evidence(document_status="archived"), "INACTIVE_EVIDENCE"),
        (make_evidence(contradiction=True), "CONFLICTING_EVIDENCE"),
        (make_evidence(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)), "STALE_EVIDENCE"),
    ],
)
def test_evidence_gate_rejects_wrong_scope_stale_weak_or_invalid_evidence(
    evidence_validator, evidence, code
) -> None:
    result = evidence_validator.validate(
        request(), [evidence], policy=EvidencePolicy(active_index_revision="idx-2")
    )
    assert result.passed is False
    assert result.code == code


def test_source_diversity_counts_documents_not_duplicate_chunks(evidence_validator) -> None:
    first = make_evidence(chunk_id="chunk-1")
    duplicate_document = make_evidence(chunk_id="chunk-2")
    result = evidence_validator.validate(
        request(), [first, duplicate_document],
        policy=EvidencePolicy(active_index_revision="idx-2", minimum_source_diversity=2),
    )
    assert result.passed is False
    assert result.code == "INSUFFICIENT_SOURCE_DIVERSITY"
