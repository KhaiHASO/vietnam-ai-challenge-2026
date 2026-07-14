from pathlib import Path


def test_nginx_enforces_tls_when_behind_a_tls_terminating_proxy() -> None:
    config = (Path(__file__).resolve().parents[3] / "deploy" / "nginx.conf").read_text(encoding="utf-8")

    assert "X-Forwarded-Proto" in config
    assert "return 308 https://$host$request_uri" in config
