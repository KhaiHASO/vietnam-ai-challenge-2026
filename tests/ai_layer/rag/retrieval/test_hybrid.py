import pytest
from ai_layer.rag.retrieval.hybrid import ReciprocalRankFusion
from ai_layer.rag.retrieval.lexical import LexicalRetriever
from ai_layer.rag.models import Chunk, ChunkMetadataModel

def test_rrf_combines_ranks():
    chunk_a = Chunk(id="A", text="a")
    chunk_b = Chunk(id="B", text="b")
    chunk_c = Chunk(id="C", text="c")
    chunk_d = Chunk(id="D", text="d")
    
    dense = [chunk_a, chunk_b, chunk_c]
    lexical = [chunk_c, chunk_d, chunk_a]
    
    fused = ReciprocalRankFusion.fuse([dense, lexical], k=60)
    
    assert len(fused) == 4
    assert fused[0].id in ("A", "C")
    assert fused[1].id in ("A", "C")


def test_lexical_retrieval_applies_scope_and_active_revision_filters(tmp_path) -> None:
    lexical = LexicalRetriever(index_path=tmp_path / "lexical.json")
    allowed = Chunk(
        id="allowed", text="bệnh đạo ôn trên lúa",
        metadata=ChunkMetadataModel(extra={
            "tenant_id": "single", "domain_id": "agriculture",
            "index_revision": "idx-2", "document_status": "active",
        }),
    )
    foreign = Chunk(
        id="foreign", text="bệnh đạo ôn trên lúa",
        metadata=ChunkMetadataModel(extra={
            "tenant_id": "other", "domain_id": "agriculture",
            "index_revision": "idx-2", "document_status": "active",
        }),
    )
    lexical.add_chunks([allowed, foreign])
    results = lexical.search(
        "đạo ôn lúa", filters={
            "tenant_id": "single", "domain_id": "agriculture",
            "index_revision": "idx-2", "document_status": "active",
        }
    )
    assert [chunk.id for chunk in results] == ["allowed"]
