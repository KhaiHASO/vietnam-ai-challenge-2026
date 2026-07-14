import pytest
from httpx import AsyncClient
from app.main import create_app

from httpx import ASGITransport

@pytest.mark.asyncio
async def test_rate_limiter_blocks_excessive_requests() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Trigger multiple requests to hit limit
        for _ in range(10):
            response = await client.get("/status")
            if response.status_code == 429:
                assert "retry-after" in response.headers.keys()
                assert response.json()["error"]["code"] == "RATE_LIMITED"
                assert response.json()["error"]["retryable"] is True
                return
        pytest.fail("Rate limit was not enforced")
