import pytest

def test_state_changing_legacy_routes_reject_anonymous_access(client) -> None:
    for method, path in [("post", "/api/approvals/a1/approve"), ("post", "/api/domain/switch")]:
        response = getattr(client, method)(path, json={})
        assert response.status_code == 401


def test_api_status_and_domain_metadata_require_authentication(client) -> None:
    assert client.get("/api/status").status_code == 401
    assert client.get("/api/domain/status").status_code == 401


def test_operator_cannot_decide_high_risk_approval(client, auth_header) -> None:
    response = client.post(
        "/api/approvals/a1/approve",
        headers=auth_header,
        json={"reason": "operator should not approve"},
    )
    assert response.status_code == 403
