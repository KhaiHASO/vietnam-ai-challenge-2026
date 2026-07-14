import pytest
from ai_layer.rag.tools.pytorch_triage import PyTorchTriage

@pytest.mark.asyncio
async def test_pytorch_triage_signal():
    triage = PyTorchTriage()
    signal = await triage.analyze("hello")
    assert signal.risk_level == "low"
    assert signal.requires_review is False
