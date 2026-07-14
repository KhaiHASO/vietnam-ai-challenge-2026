import pytest
import json
from app.copilot.service import CopilotService, ConversationRevisionConflict
from ai_layer.rag.contracts import Abstention, AbstentionCode, AnswerStatus, Approval, CopilotAnswer

@pytest.mark.asyncio
async def test_same_idempotency_key_runs_model_once(copilot_service, copilot_request) -> None:
    first = await copilot_service.send(copilot_request)
    second = await copilot_service.send(copilot_request)
    assert first.message_id == second.message_id
    assert copilot_service.rag.calls == 1

@pytest.mark.asyncio
async def test_stale_revision_is_rejected(copilot_service, copilot_request) -> None:
    await copilot_service.send(copilot_request)
    copilot_request.idempotency_key = "key-2"
    with pytest.raises(ConversationRevisionConflict):
        await copilot_service.send(copilot_request)


@pytest.mark.asyncio
async def test_idempotency_replays_the_full_typed_abstention(copilot_service, copilot_request) -> None:
    expected = CopilotAnswer(
        status=AnswerStatus.ABSTAINED,
        abstention=Abstention(
            code=AbstentionCode.INSUFFICIENT_EVIDENCE,
            user_message="Chưa đủ nguồn.",
            attempted_sources=2,
            recovery_actions=["ask_expert"],
            expert_handoff_available=True,
        ),
        trace_id="trace-abstain",
    )
    copilot_service.rag.process = pytest.importorskip("unittest.mock").AsyncMock(
        return_value=expected
    )
    first = await copilot_service.send(copilot_request)
    second = await copilot_service.send(copilot_request)
    assert second.model_dump(mode="json") == first.model_dump(mode="json")


@pytest.mark.asyncio
async def test_stream_returns_the_persisted_conversation_revision(copilot_service) -> None:
    chunks = [
        chunk
        async for chunk in copilot_service.process_stream(
            session_id="s-revision",
            user_id="u1",
            tenant_id="t1",
            idempotency_key="revision-key",
            request_body={"query": "Kiem tra revision", "expected_conversation_revision": 0},
        )
    ]
    final = next(chunk for chunk in chunks if "event: message.completed" in chunk)
    payload = json.loads(next(line[6:] for line in final.splitlines() if line.startswith("data: ")))

    assert payload["conversation_revision"] == 1


@pytest.mark.asyncio
async def test_stream_emits_an_approval_event_for_high_risk_actions(copilot_service) -> None:
    copilot_service.rag.process = pytest.importorskip("unittest.mock").AsyncMock(
        return_value=CopilotAnswer(
            status=AnswerStatus.APPROVAL_REQUIRED,
            approval=Approval(required=True, action_type="apply_treatment"),
        )
    )

    chunks = [
        chunk
        async for chunk in copilot_service.process_stream(
            session_id="s-approval",
            user_id="u1",
            tenant_id="t1",
            idempotency_key="approval-key",
            request_body={"query": "Xu ly ngay", "expected_conversation_revision": 0},
        )
    ]

    assert any("event: approval.required" in chunk for chunk in chunks)
