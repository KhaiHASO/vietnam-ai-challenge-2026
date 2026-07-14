from ai_layer.rag.embeddings.deterministic import DeterministicEmbeddingProvider
from ai_layer.rag.vectorstores import chroma_store


class FakeCollection:
    pass


class FakeChroma:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def HttpClient(self, **kwargs):
        self.calls.append(kwargs)
        return self

    def get_or_create_collection(self, **kwargs):
        return FakeCollection()


def test_remote_chroma_url_uses_http_client(monkeypatch) -> None:
    fake = FakeChroma()
    monkeypatch.setattr(chroma_store, "chromadb", fake, raising=False)
    monkeypatch.setattr(chroma_store, "CHROMADB_AVAILABLE", True)
    store = chroma_store.ChromaVectorStore(
        DeterministicEmbeddingProvider(), chroma_url="http://chromadb:8000"
    )
    assert store.collection is not None
    assert fake.calls == [{"host": "chromadb", "port": 8000, "ssl": False}]
