from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ai_layer.rag.models import Chunk


class BaseVectorStore(ABC):
    """
    Abstract interface for Vector Databases (e.g. Chroma, Qdrant, Milvus).
    """

    @abstractmethod
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """
        Adds embedded chunks to the vector database.
        
        Args:
            chunks: List of Chunk objects containing text, metadata, and embeddings.
            
        Returns:
            bool: True if successful.
        """
        pass

    @abstractmethod
    def similarity_search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Searches the vector database for the most similar chunks.
        
        Args:
            query_embedding: The vector embedding of the query.
            top_k: Number of results to return.
            filters: Optional metadata filters (e.g., {"domain": "agriculture"}).
            
        Returns:
            List[Chunk]: The retrieved chunks.
        """
        pass
