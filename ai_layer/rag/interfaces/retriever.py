from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ai_layer.rag.models import Chunk


class BaseRetriever(ABC):
    """
    Abstract interface for Retrieval Pipelines.
    Retrievers orchestrate the search process (e.g., calling Embeddings -> VectorStore -> Re-ranker).
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Chunk]:
        """
        Executes a full retrieval pipeline for a given query.
        
        Args:
            query: The user's search query.
            top_k: The final number of chunks to return after retrieval and ranking.
            filters: Optional metadata filters.
            
        Returns:
            List[Chunk]: The top ranked retrieved chunks.
        """
        pass
