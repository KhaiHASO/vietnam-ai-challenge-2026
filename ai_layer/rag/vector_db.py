"""Compatibility wrapper — preserves the old LocalVectorDB API while delegating
to the new RAG system that uses ChunkMetadataModel / Chunk."""
import uuid
from typing import List, Tuple, Dict

try:
    from .app_context import app_context
    from .models import Chunk, ChunkMetadataModel
    _READY = True
except Exception:
    _READY = False


if _READY:
    def _doc_to_chunk(doc: Dict) -> Chunk:
        ki = doc.get("knowledge_item_id", "") or ""
        meta_raw = doc.get("metadata", {}) or {}
        meta = ChunkMetadataModel(
            source_id=doc.get("id", ""),
            source_type=meta_raw.get("source_type", "mock"),
            chunk_index=0,
            extra={k: v for k, v in meta_raw.items() if k != "source_type"},
        )
        return Chunk(id=doc.get("id", str(uuid.uuid4())), text=doc.get("content", ""), metadata=meta)
else:
    def _doc_to_chunk(doc):
        return doc


class LocalVectorDB:
    """Backward-compatible shim wrapping the new retriever / vector store."""

    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        if _READY:
            try:
                self._vs = app_context.vector_store
            except Exception:
                self._vs = None
        else:
            self._vs = None

    def get_embedding(self, text: str):
        if _READY:
            return app_context.embedding_provider.embed_query(text)
        return None

    def add_documents(self, docs):
        if self._vs is None:
            return
        chunks = [_doc_to_chunk(d) for d in docs]
        for c in chunks:
            self.documents[c.id] = {"content": c.text}
        self._vs.add_chunks(chunks)

    def search(self, query: str, top_k: int = 2) -> List[Tuple[Dict, float]]:
        if self._vs is None:
            return []
        results = app_context.retriever.retrieve(query, top_k=top_k)
        out = []
        for c in results:
            score = c.metadata.rerank_score if _READY and hasattr(c.metadata, "rerank_score") else 0.0
            out.append(({"id": c.id, "content": c.text}, score))
        return out

    def save_db(self):
        pass

    def load_db(self):
        pass
