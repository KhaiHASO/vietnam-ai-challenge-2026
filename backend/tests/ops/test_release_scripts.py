from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_backup_script_keeps_artifacts_inside_a_configured_root() -> None:
    script = (ROOT / "scripts" / "backup.ps1").read_text(encoding="utf-8")

    assert "BackupRoot" in script
    assert "Resolve-Path" in script
    assert "mongodump" in script


def test_restore_verification_uses_an_isolated_compose_project_and_cleans_it_up() -> None:
    script = (ROOT / "scripts" / "restore_verify.ps1").read_text(encoding="utf-8")

    assert "-p $ProjectName" in script
    assert "down -v" in script
    assert "mongorestore" in script
