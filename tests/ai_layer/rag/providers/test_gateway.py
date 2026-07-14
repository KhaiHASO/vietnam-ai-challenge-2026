import pytest
import asyncio
from ai_layer.rag.providers.gateway import ProviderGateway

class MockAdapter:
    provider_name = "mock"

    async def generate(self, query: str, evidence: list) -> str:
        return "mock_res"


class SlowAdapter:
    provider_name = "slow"

    async def generate(self, query: str, evidence: list) -> str:
        await asyncio.sleep(1)
        return "late"

@pytest.mark.asyncio
async def test_gateway_timeout_enforcement():
    gateway = ProviderGateway(SlowAdapter(), timeout_seconds=0.01, max_retries=1)
    with pytest.raises(Exception, match="Provider timeout"):
        await gateway.generate("q", [])


@pytest.mark.asyncio
async def test_gateway_does_not_retry_non_transient_configuration_error():
    class BrokenAdapter:
        provider_name = "broken"

        def __init__(self):
            self.calls = 0

        async def generate(self, query, evidence):
            from ai_layer.rag.providers.gateway import ProviderConfigurationError
            self.calls += 1
            raise ProviderConfigurationError("missing credential")

    adapter = BrokenAdapter()
    gateway = ProviderGateway(adapter, max_retries=3)
    with pytest.raises(Exception, match="missing credential"):
        await gateway.generate("q", [])
    assert adapter.calls == 1
