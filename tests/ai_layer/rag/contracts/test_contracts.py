import pytest
from pydantic import ValidationError

from datetime import datetime, timezone

from ai_layer.rag.contracts import (
    Abstention,
    AbstentionCode,
    AnswerStatus,
    CopilotAnswer,
    CopilotEvent,
    CopilotEventType,
    CopilotRequest,
    ModelSignal,
)

def test_request_rejects_blank_query() -> None:
    with pytest.raises(ValidationError):
        CopilotRequest(
            session_id="s1", 
            user_id="u1", 
            tenant_id="single",
            domain_id="agriculture", 
            query="   ",
            expected_conversation_revision=0, 
            idempotency_key="k1",
        )

def test_request_strips_whitespace() -> None:
    request = CopilotRequest(
        session_id="s1", 
        user_id="u1", 
        tenant_id="single",
        domain_id="agriculture", 
        query=" valid query ",
        expected_conversation_revision=0, 
        idempotency_key="k1",
    )
    assert request.query == "valid query"

def test_abstained_answer_requires_abstention_and_no_answer() -> None:
    with pytest.raises(ValidationError):
        # Having both answer text and abstained status should fail
        CopilotAnswer(
            status=AnswerStatus.ABSTAINED, 
            answer="guessed"
        )
        
    with pytest.raises(ValidationError):
        # Abstained status requires an abstention object
        CopilotAnswer(
            status=AnswerStatus.ABSTAINED,
        )

def test_answered_status_requires_answer_text() -> None:
    with pytest.raises(ValidationError):
        # Answered status requires answer text
        CopilotAnswer(
            status=AnswerStatus.ANSWERED
        )
    
    # Valid answer should pass
    CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="This is a valid answer."
    )


def test_abstention_codes_match_the_public_wire_contract() -> None:
    assert {code.value for code in AbstentionCode} == {
        "INSUFFICIENT_EVIDENCE",
        "CONFLICTING_EVIDENCE",
        "OUT_OF_DOMAIN",
        "POLICY_BLOCKED",
        "PROVIDER_UNAVAILABLE",
        "VALIDATION_FAILED",
    }


def test_abstention_has_graceful_recovery_fields_and_at_most_three_actions() -> None:
    abstention = Abstention(
        code=AbstentionCode.INSUFFICIENT_EVIDENCE,
        user_message="Tôi chưa có đủ nguồn đáng tin cậy để kết luận.",
        attempted_sources=4,
        recovery_actions=["refine_question", "upload_document", "ask_expert"],
        expert_handoff_available=True,
    )
    answer = CopilotAnswer(status=AnswerStatus.ABSTAINED, abstention=abstention)
    assert answer.model_dump()["abstention"]["attempted_sources"] == 4

    with pytest.raises(ValidationError):
        Abstention(
            code=AbstentionCode.INSUFFICIENT_EVIDENCE,
            user_message="Không đủ bằng chứng.",
            recovery_actions=["refine_question", "upload_document", "ask_expert", "refine_question"],
        )


def test_event_type_and_required_replay_metadata_are_typed() -> None:
    event = CopilotEvent(
        event_id="evt-1",
        sequence=1,
        session_id="session-1",
        message_id="message-1",
        occurred_at=datetime.now(timezone.utc),
        trace_id="trace-1",
        event_type=CopilotEventType.MESSAGE_STARTED,
        payload={"conversation_revision": 3},
    )
    assert event.event_type == CopilotEventType.MESSAGE_STARTED
    with pytest.raises(ValidationError):
        CopilotEvent(**{**event.model_dump(), "event_type": "chain_of_thought"})


def test_model_signal_is_typed_non_evidence_and_priority_is_numeric() -> None:
    signal = ModelSignal(
        risk_level="high",
        priority=0.91,
        requires_review=True,
        confidence=0.88,
        model_version="impact-triage-v1",
        latency_ms=12.4,
        engine_status="ready",
    )
    assert signal.priority == pytest.approx(0.91)
    with pytest.raises(ValidationError):
        ModelSignal(**{**signal.model_dump(), "priority": "urgent"})


def test_internal_validator_flag_never_leaks_to_public_answer() -> None:
    answer = CopilotAnswer(
        status=AnswerStatus.ANSWERED,
        answer="Nội dung đã xác minh.",
        validators_passed=True,
    )
    assert "validators_passed" not in answer.model_dump()
