import hashlib
import math
from typing import List

from ai_layer.rag.interfaces.embedding import BaseEmbeddingProvider


class DeterministicEmbeddingProvider(BaseEmbeddingProvider):
    """
    Lightweight fallback embedding provider for local tests and degraded startup.
    It is not a semantic model, but it keeps the vector path deterministic.
    """

    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions

    def embed_query(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]
