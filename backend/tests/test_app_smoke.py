from fastapi.testclient import TestClient
from app.main import create_app


def test_application_factory_builds_the_existing_api() -> None:
    app = create_app()
    assert app.title == "MathPath THPT Backend"
    
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_legacy_diagnosis_and_private_knowledge_uploads_are_not_mounted() -> None:
    app = create_app()
    mounted_paths = {route.path for route in app.routes if hasattr(route, "app")}

    assert "/uploads" not in mounted_paths
    assert "/uploads/diagnosis_cases" not in mounted_paths


def test_liveness_is_public_and_typed() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_checks_dependencies() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert set(data["dependencies"]) == {
        "mongo",
        "redis",
        "chroma",
        "registry",
        "primary_provider",
    }


def test_legacy_status_routes_resolve_the_domain_without_global_state() -> None:
    app = create_app()
    client = TestClient(app, raise_server_exceptions=False)

    status_response = client.get("/api/status")
    domain_response = client.get("/api/domain/status")

    assert status_response.status_code == 404
    assert domain_response.status_code == 404
