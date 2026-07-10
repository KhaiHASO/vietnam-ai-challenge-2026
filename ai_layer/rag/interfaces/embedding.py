from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """
    Abstract interface for Embedding models (e.g. OpenAI, BGE, E5, SentenceTransformers).
    """

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embeds a single search query.
        
        Args:
            text: The search query string.
            
        Returns:
            List[float]: The vector embedding.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of documents/chunks.
        
        Args:
            texts: List of text strings to embed.
            
        Returns:
            List[List[float]]: A list of vector embeddings.
        """
        pass
