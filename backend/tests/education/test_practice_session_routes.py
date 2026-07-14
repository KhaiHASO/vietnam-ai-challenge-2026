from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.contracts import Principal, Role
from app.auth.tokens import TokenService


HASH = "sha256:" + "b" * 64


def _auth(user_id: str, tenant_id: str, *roles: Role) -> dict[str, str]:
    token = TokenService().create_access_token(
        Principal(user_id=user_id, tenant_id=tenant_id, roles=frozenset(roles))
    )
    return {"Authorization": f"Bearer {token}"}


def test_practice_session_duplicate_key_returns_one_version_pinned_session(
    client: TestClient,
) -> None:
    payload = {
        "student_id": "STU-001",
        "target_skill_id": "A11-CAL-07",
        "idempotency_key": "session-key-001",
    }

    first = client.post(
        "/api/v1/education/practice-sessions",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
        json=payload,
    )
    second = client.post(
        "/api/v1/education/practice-sessions",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["session_id"] == second.json()["session_id"]
    assert first.json()["versions"] == {
        "graph": "gdpt2018-v1",
        "question": "questions-v1",
        "policy": "mathpath-policy-v1",
        "model": "bkt-elo-v1",
    }
    assert second.json()["created"] is False


def test_step_attempt_duplicate_key_creates_one_attempt_and_one_state_update(
    client: TestClient,
) -> None:
    session = client.post(
        "/api/v1/education/practice-sessions",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
        json={
            "student_id": "STU-001",
            "target_skill_id": "A11-CAL-07",
            "idempotency_key": "session-key-002",
        },
    ).json()
    payload = {
        "idempotency_key": "attempt-key-001",
        "question_id": "Q-007",
        "skill_id": "A11-CAL-07",
        "step_index": 0,
        "raw_step": "x != 1; apply the quotient rule",
        "normalized_step": "x*(x-2)/(x-1)^2",
        "verification_status": "verified",
        "math_evidence_hash": HASH,
        "math_tool_version": "mathpath-sympy-v1",
        "question_difficulty": 0.55,
        "hint_level": 0,
    }

    first = client.post(
        f"/api/v1/education/practice-sessions/{session['session_id']}/step-attempts",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
        json=payload,
    )
    second = client.post(
        f"/api/v1/education/practice-sessions/{session['session_id']}/step-attempts",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["attempt_id"] == second.json()["attempt_id"]
    assert first.json()["state_update"]["status"] == "applied"
    assert second.json()["state_update"]["status"] == "duplicate"
    assert second.json()["state"]["evidence_count"] == 1
    assert second.json()["versions"]["graph"] == "gdpt2018-v1"
    assert second.json()["versions"]["model"] == "bkt-elo-v1"
