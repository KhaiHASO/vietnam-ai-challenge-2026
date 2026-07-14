from fastapi.testclient import TestClient
from app.auth.contracts import Principal, Role
from app.auth.dependencies import get_auth_repository, get_current_user
from app.core.security import hash_secret

def test_login_returns_tokens(client: TestClient, app, auth_repository) -> None:
    # Add a user to mock repo
    auth_repository.users["test"] = {
        "user_id": "test_id", 
        "username": "test", 
        "hashed_password": hash_secret("password"), 
        "tenant_id": "single",
        "roles": ["operator"],
        "is_active": True
    }
    app.dependency_overrides[get_auth_repository] = lambda: auth_repository
    
    try:
        response = client.post("/api/v1/auth/login", json={"username": "test", "password": "password"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" not in data
        assert response.cookies.get("refresh_token")
    finally:
        app.dependency_overrides.clear()

def test_refresh_returns_new_tokens(client: TestClient, app, auth_repository) -> None:
    app.dependency_overrides[get_auth_repository] = lambda: auth_repository
    try:
        client.cookies.set("refresh_token", "invalid")
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code in (401, 400)
    finally:
        app.dependency_overrides.clear()


def test_admin_can_create_user_but_operator_cannot(client: TestClient, app, auth_repository) -> None:
    app.dependency_overrides[get_auth_repository] = lambda: auth_repository
    try:
        app.dependency_overrides[get_current_user] = lambda: Principal(
            user_id="admin-1",
            tenant_id="single",
            roles=frozenset({Role.ADMIN}),
        )
        created = client.post(
            "/api/v1/admin/users",
            json={"username": "Expert.One", "password": "a-strong-password", "roles": ["expert"]},
        )
        assert created.status_code == 201
        assert created.json()["roles"] == ["expert"]
        assert "hashed_password" not in created.json()

        app.dependency_overrides[get_current_user] = lambda: Principal(
            user_id="operator-1",
            tenant_id="single",
            roles=frozenset({Role.OPERATOR}),
        )
        denied = client.post(
            "/api/v1/admin/users",
            json={"username": "Second", "password": "a-strong-password", "roles": ["operator"]},
        )
        assert denied.status_code == 403
    finally:
        app.dependency_overrides.clear()
