from abc import ABC, abstractmethod
from typing import List, Optional
from ai_layer.rag.models import Document, SourceType


class BaseParser(ABC):
    """
    Abstract interface for all Document Parsers.
    Parsers are responsible for converting raw files (PDF, DOCX, Image, etc.) 
    into standard Document objects containing text and basic metadata.
    """

    @abstractmethod
    def parse(self, file_path: str, source_type: SourceType, knowledge_item_id: str) -> List[Document]:
        """
        Parses a file and returns a list of Document objects (e.g. one per page).
        
        Args:
            file_path: The path to the file to parse.
            source_type: The type of the source file.
            knowledge_item_id: The ID of the parent knowledge item.
            
        Returns:
            List[Document]: The parsed documents.
        """
        pass
