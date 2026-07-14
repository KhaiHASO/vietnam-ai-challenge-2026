from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.contracts import Principal, Role
from app.auth.tokens import TokenService


def _auth(user_id: str, tenant_id: str, *roles: Role) -> dict[str, str]:
    token = TokenService().create_access_token(
        Principal(user_id=user_id, tenant_id=tenant_id, roles=frozenset(roles))
    )
    return {"Authorization": f"Bearer {token}"}


def test_admin_and_assigned_teacher_can_read_class_roster(client: TestClient) -> None:
    admin = client.get(
        "/api/v1/education/classes/CLASS-10A1",
        headers=_auth("ADMIN-01", "tenant-demo", Role.ADMIN),
    )
    teacher = client.get(
        "/api/v1/education/classes/CLASS-10A1",
        headers=_auth("TEACHER-01", "tenant-demo", Role.TEACHER),
    )

    assert admin.status_code == 200
    assert teacher.status_code == 200
    assert admin.json()["class_id"] == "CLASS-10A1"
    assert teacher.json()["teacher_id"] == "TEACHER-01"
    assert admin.json()["students"]
    assert "email" not in admin.text
    assert "full_name" not in admin.text


def test_teacher_cross_class_and_cross_tenant_access_are_sanitized_not_found(
    client: TestClient,
) -> None:
    cross_class = client.get(
        "/api/v1/education/classes/CLASS-10A1",
        headers=_auth("TEACHER-02", "tenant-demo", Role.TEACHER),
    )
    cross_tenant = client.get(
        "/api/v1/education/classes/CLASS-10A1",
        headers=_auth("ADMIN-02", "tenant-other", Role.ADMIN),
    )

    assert cross_class.status_code == 404
    assert cross_tenant.status_code == 404
    assert "CLASS-10A1" not in cross_class.text
    assert "tenant-demo" not in cross_tenant.text


def test_student_can_read_only_own_summary(client: TestClient) -> None:
    own = client.get(
        "/api/v1/education/students/STU-001/summary",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
    )
    other_student = client.get(
        "/api/v1/education/students/STU-002/summary",
        headers=_auth("STU-001", "tenant-demo", Role.STUDENT),
    )

    assert own.status_code == 200
    assert own.json()["student_id"] == "STU-001"
    assert own.json()["pseudonym"].startswith("MP26-")
    assert other_student.status_code == 404
    assert "STU-002" not in other_student.text


def test_unapproved_role_cannot_access_education_routes(client: TestClient) -> None:
    response = client.get(
        "/api/v1/education/classes/CLASS-10A1",
        headers=_auth("operator-1", "tenant-demo", Role.OPERATOR),
    )

    assert response.status_code == 403
    assert response.json()["error"]["message"] == "Insufficient permissions"
    assert "CLASS-10A1" not in response.text
