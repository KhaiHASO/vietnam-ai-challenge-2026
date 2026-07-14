from abc import ABC, abstractmethod

class ObjectStorage(ABC):
    @abstractmethod
    def store(self, original_filename: str, content: bytes, content_type: str) -> str:
        """Stores a file and returns its generated unique path."""
        pass
        
    @abstractmethod
    def retrieve(self, path: str) -> bytes:
        """Retrieves a file by its path."""
        pass
