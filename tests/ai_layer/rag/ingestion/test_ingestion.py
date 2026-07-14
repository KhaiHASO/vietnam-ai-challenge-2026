import pytest
from ai_layer.rag.models import Document, Chunk, ChunkMetadataModel
from ai_layer.rag.chunkers.langchain_chunker import LangchainChunker
from ai_layer.rag.vectorstores.chroma_store import ChromaVectorStore
from ai_layer.rag.embeddings.deterministic import DeterministicEmbeddingProvider
import uuid

@pytest.fixture
def chunker():
    return LangchainChunker()

@pytest.fixture
def document():
    return Document(
        id=str(uuid.uuid4()),
        knowledge_item_id="ki-123",
        text_content="This is a test document."
    )

def test_chunker_emits_canonical_chunk_metadata(chunker, document) -> None:
    chunk = chunker.split([document])[0]
    assert chunk.metadata.source_id == document.id
    assert chunk.metadata.chunk_index == 0
    assert chunk.metadata.extra.get("knowledge_item_id") == document.knowledge_item_id

import tempfile
import shutil

def test_chroma_round_trip_preserves_scope_and_provenance() -> None:
    path = tempfile.mkdtemp()
    try:
        provider = DeterministicEmbeddingProvider()
        store = ChromaVectorStore(
            embedding_provider=provider,
            persist_directory=path,
            allow_in_memory_fallback=True,
        )
        
        chunk = Chunk(
            id="chunk-123",
            text="test text",
            metadata=ChunkMetadataModel(
                source_id="doc-123",
                extra={"tenant_id": "single", "domain_id": "agriculture", "index_revision": "idx-2"}
            )
        )
        
        assert store.add_chunks([chunk])
        
        embedding = provider.embed_documents(["test text"])[0]
        
        results = store.similarity_search(embedding, filters={"tenant_id": "single"})
        assert len(results) == 1
        
        result = results[0]
        assert result.metadata.extra["domain_id"] == "agriculture"
        assert result.metadata.extra["index_revision"] == "idx-2"
    finally:
        shutil.rmtree(path, ignore_errors=True)
