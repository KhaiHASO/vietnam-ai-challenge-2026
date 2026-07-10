import math
from typing import Any, Dict, List, Optional

from ai_layer.rag.interfaces.embedding import BaseEmbeddingProvider
from ai_layer.rag.interfaces.vectorstore import BaseVectorStore
from ai_layer.rag.models import Chunk


class InMemoryVectorStore(BaseVectorStore):
    """
    Degraded vector store for tests and local startup when ChromaDB is absent.
    It preserves the BaseVectorStore contract without external persistence.
    """

    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
        self._chunks: List[Chunk] = []

    def add_chunks(self, chunks: List[Chunk]) -> bool:
        if not chunks:
            return True

        texts_to_embed = [chunk.text for chunk in chunks if chunk.embedding is None]
        embeddings = self.embedding_provider.embed_documents(texts_to_embed) if texts_to_embed else []
        embedding_index = 0

        for chunk in chunks:
            if chunk.embedding is None:
                chunk.embedding = embeddings[embedding_index]
                embedding_index += 1
            self._chunks.append(chunk)

        return True

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        candidates = [
            chunk for chunk in self._chunks if self._matches_filters(chunk.metadata, filters)
        ]
        scored = sorted(
            candidates,
            key=lambda chunk: self._cosine_similarity(query_embedding, chunk.embedding or []),
            reverse=True,
        )

        results = []
        for chunk in scored[:top_k]:
            chunk.metadata["similarity_distance"] = 1.0 - self._cosine_similarity(
                query_embedding,
                chunk.embedding or [],
            )
            results.append(chunk)
        return results

    @staticmethod
    def _matches_filters(metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        return all(metadata.get(key) == value for key, value in filters.items())

    @staticmethod
    def _cosine_similarity(left: List[float], right: List[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)
