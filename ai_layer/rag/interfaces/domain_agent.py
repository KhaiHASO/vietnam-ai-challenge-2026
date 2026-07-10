from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, Generator

class BaseDomainAgent(ABC):
    """
    Interface cho tất cả các Domain Agents trong hệ thống.
    Mỗi ngành nghề (Nông nghiệp, Y tế, Pháp lý, v.v.) sẽ cần implement interface này
    và đặt tại thư mục domain_packs/<domain_name>/agent.py
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Trả về tên unique của domain (ví dụ: 'agriculture')"""
        pass

    @abstractmethod
    def ask(self, query: str, session_id: str = "default", tenant_id: str = "default") -> str:
        """
        Xử lý truy vấn và trả về câu trả lời hoàn chỉnh (blocking).
        """
        pass

    @abstractmethod
    def ask_stream(self, query: str, session_id: str = "default", tenant_id: str = "default") -> Generator[str, None, None]:
        """
        Xử lý truy vấn và trả về generator để stream SSE events (trạng thái + text).
        """
        pass
