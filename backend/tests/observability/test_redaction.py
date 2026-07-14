from ai_layer.rag.observability.trace import TraceRecorder


def test_trace_redacts_prompt_pii_and_secrets() -> None:
    event = TraceRecorder().record({"query": "Gọi tôi qua 0912345678", "token": "secret"})
    assert "0912345678" not in event.serialized
    assert "secret" not in event.serialized


def test_trace_never_persists_raw_query_content() -> None:
    event = TraceRecorder().record({"query": "No raw prompt may be stored", "route": "fast"})

    assert event.payload["query"] == "[REDACTED]"
    assert "No raw prompt" not in event.serialized
