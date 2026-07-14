from ai_layer.rag.core.dependencies import get_rag_service


def test_runtime_uses_configured_fpt_adapter_not_a_dummy_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("FPT_AI_FACTORY_ENDPOINT", "https://factory.example/chat")
    get_rag_service.cache_clear()
    service = get_rag_service()
    assert service.gateway.adapter.endpoint == "https://factory.example/chat"
