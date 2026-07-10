import os
from ai_layer.rag.interfaces.parser import BaseParser
from ai_layer.rag.models import SourceType
from ai_layer.rag.parsers.pdf_parser import PDFParser
from ai_layer.rag.parsers.image_parser import ImageParser

class FileDetector:
    """
    Router that detects the file type based on its extension
    and returns the corresponding SourceType and Parser instance.
    """
    
    # Mapping of extensions to SourceType
    EXTENSION_MAP = {
        ".pdf": SourceType.PDF,
        ".png": SourceType.IMAGE,
        ".jpg": SourceType.IMAGE,
        ".jpeg": SourceType.IMAGE,
        ".docx": SourceType.DOCX,
        ".xlsx": SourceType.EXCEL,
        ".csv": SourceType.CSV,
    }

    # Lazy-loaded parsers to avoid heavy initialization on startup
    _parsers = {}

    @classmethod
    def get_source_type(cls, file_path: str) -> SourceType:
        """Determines the SourceType from the file extension."""
        _, ext = os.path.splitext(file_path.lower())
        if ext in cls.EXTENSION_MAP:
            return cls.EXTENSION_MAP[ext]
        raise ValueError(f"Unsupported file extension: {ext}")

    @classmethod
    def get_parser(cls, source_type: SourceType) -> BaseParser:
        """Returns the appropriate Parser instance for the SourceType."""
        if source_type == SourceType.PDF:
            if SourceType.PDF not in cls._parsers:
                cls._parsers[SourceType.PDF] = PDFParser()
            return cls._parsers[SourceType.PDF]
            
        elif source_type == SourceType.IMAGE:
            if SourceType.IMAGE not in cls._parsers:
                cls._parsers[SourceType.IMAGE] = ImageParser()
            return cls._parsers[SourceType.IMAGE]
            
        else:
            raise NotImplementedError(f"Parser for {source_type} is not yet implemented.")
            
    @classmethod
    def detect_and_parse(cls, file_path: str, knowledge_item_id: str):
        """Convenience method to detect and parse a file in one go."""
        source_type = cls.get_source_type(file_path)
        parser = cls.get_parser(source_type)
        return parser.parse(file_path, source_type, knowledge_item_id)
