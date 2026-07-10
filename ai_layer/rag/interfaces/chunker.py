from abc import ABC, abstractmethod
from typing import List
from ai_layer.rag.models import Document, Chunk


class BaseChunker(ABC):
    """
    Abstract interface for all Chunking strategies.
    Chunkers break down parsed Documents into smaller, semantically meaningful Chunks.
    """

    @abstractmethod
    def split(self, documents: List[Document]) -> List[Chunk]:
        """
        Splits a list of Documents into Chunks.
        
        Args:
            documents: List of Document objects to be chunked.
            
        Returns:
            List[Chunk]: The resulting chunks.
        """
        pass
