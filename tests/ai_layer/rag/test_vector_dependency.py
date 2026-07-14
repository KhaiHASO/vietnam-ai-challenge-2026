from ai_layer.rag.core.dependencies import get_vector_store
from ai_layer.rag.vectorstores import chroma_store


class FakeClient:
    def HttpClient(self, **kwargs):
        self.kwargs = kwargs
        return self

    def get_or_create_collection(self, **kwargs):
        return object()


def test_vector_dependency_uses_chroma_url_when_configured(monkeypatch) -> None:
    fake = FakeClient()
    monkeypatch.setattr(chroma_store, "chromadb", fake, raising=False)
    monkeypatch.setattr(chroma_store, "CHROMADB_AVAILABLE", True)
    monkeypatch.setattr("ai_layer.rag.core.dependencies.settings.CHROMA_URL", "http://chroma:8000", raising=False)
    get_vector_store.cache_clear()
    get_vector_store("agriculture")
    assert fake.kwargs == {"host": "chroma", "port": 8000, "ssl": False}
