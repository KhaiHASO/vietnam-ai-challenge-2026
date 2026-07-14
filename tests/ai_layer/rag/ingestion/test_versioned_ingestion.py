from ai_layer.rag.ingestion.service import IngestionService
from ai_layer.rag.chunkers.langchain_chunker import LangchainChunker


class Storage:
    def __init__(self):
        self.calls = 0

    def store(self, original_filename, content, content_type):
        self.calls += 1
        return f"objects/{self.calls}.txt"


class Store:
    def __init__(self, succeeds=True):
        self.succeeds = succeeds
        self.calls = 0
        self.chunks = []

    def add_chunks(self, chunks):
        self.calls += 1
        self.chunks.extend(chunks)
        return self.succeeds


def test_checksum_idempotency_and_atomic_active_revision_switch() -> None:
    dense, lexical = Store(), Store()
    service = IngestionService(Storage(), LangchainChunker(), dense, lexical)
    metadata = {"tenant_id": "single", "domain_id": "agriculture", "knowledge_item_id": "ki-1"}

    first = service.ingest("guide.txt", b"rice blast guidance", "text/plain", metadata)
    repeated = service.ingest("guide.txt", b"rice blast guidance", "text/plain", metadata)

    assert repeated.index_revision == first.index_revision
    assert dense.calls == 1
    assert service.active_revision("single", "agriculture") == first.index_revision
    assert dense.chunks[0].metadata.extra["checksum"] == first.checksum


def test_failed_staging_does_not_replace_previous_active_revision() -> None:
    dense, lexical = Store(), Store()
    service = IngestionService(Storage(), LangchainChunker(), dense, lexical)
    metadata = {"tenant_id": "single", "domain_id": "agriculture", "knowledge_item_id": "ki-1"}
    first = service.ingest("one.txt", b"first version", "text/plain", metadata)

    dense.succeeds = False
    try:
        service.ingest("two.txt", b"second version", "text/plain", metadata)
    except RuntimeError:
        pass
    else:
        raise AssertionError("failed staging was accepted")

    assert service.active_revision("single", "agriculture") == first.index_revision
