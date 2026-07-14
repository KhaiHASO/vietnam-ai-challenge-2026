from pathlib import Path


def test_ci_runs_release_smoke_and_dependency_audits() -> None:
    workflow = (Path(__file__).resolve().parents[3] / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "docker-smoke" in workflow
    assert "docker compose up --build -d" in workflow
    assert "pip-audit" in workflow
    assert "npm audit" in workflow
