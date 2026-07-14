import pytest
from ai_layer.rag.agentic.graph import BoundedAgenticRunner
from ai_layer.rag.contracts.request import CopilotRequest

@pytest.mark.asyncio
async def test_bounded_runner_returns_evidence():
    runner = BoundedAgenticRunner()
    req = CopilotRequest(tenant_id="t1", domain_id="d1", user_id="u1", session_id="s1", query="q")
    evidence = await runner.run(req)
    assert evidence == []
