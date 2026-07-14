import pytest
from ai_layer.rag.providers.fpt_ai_factory import FPTAIChatAdapter

@pytest.mark.asyncio
async def test_fpt_ai_adapter_basic():
    adapter = FPTAIChatAdapter("http://fpt", "model-1", api_key="")
    with pytest.raises(Exception, match="API key"):
        await adapter.generate("q", [])
