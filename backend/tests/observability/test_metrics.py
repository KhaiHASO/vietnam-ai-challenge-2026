from app.observability.metrics import MetricRegistry


def test_metrics_export_has_no_raw_query_or_secret() -> None:
    registry = MetricRegistry()
    registry.record("copilot_requests_total", 1, labels={"provider": "fpt-ai-factory"})
    exported = registry.render()
    assert "copilot_requests_total" in exported
    assert "query" not in exported
    assert "secret" not in exported
