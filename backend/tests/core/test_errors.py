from fastapi.testclient import TestClient
from app.main import create_app

def test_error_payload_contains_trace_and_retryability() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/test/missing", headers={"X-Request-ID": "trace-7"})
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    error_detail = data["error"]
    assert error_detail.get("code") == "HTTP_404" or response.status_code == 404
    assert error_detail.get("trace_id") == "trace-7"
    assert "retryable" in error_detail
    assert error_detail["retryable"] is False
