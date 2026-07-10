import pytest
from app.copilot.service import CopilotService, ConversationRevisionConflict

@pytest.mark.asyncio
async def test_same_idempotency_key_runs_model_once(copilot_service, copilot_request) -> None:
    first = await copilot_service.send(copilot_request)
    second = await copilot_service.send(copilot_request)
    assert first.message_id == second.message_id
    assert copilot_service.rag.calls == 1

@pytest.mark.asyncio
async def test_stale_revision_is_rejected(copilot_service, copilot_request) -> None:
    await copilot_service.send(copilot_request)
    with pytest.raises(ConversationRevisionConflict):
        await copilot_service.send(copilot_request)
