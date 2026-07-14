import os
import re
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_DOMAIN_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

class AISettings(BaseSettings):
    # Base Domain Root
    DOMAINS_ROOT: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "domains")
    
    # LLM Settings (Global fallback defaults, usually overridden by per-domain manifest logic)
    PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")  # ollama, openai, gemini
    MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama3.2")
    API_KEY: str = os.getenv("AI_API_KEY", "")
    BASE_URL: str = os.getenv("AI_BASE_URL", "http://localhost:11434")
    TEMPERATURE: float = 0.2
    
    # RAG Settings (Fallback defaults)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")  # local, openai, gemini
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "keepitreal/vietnamese-sbert")
    RAG_TOP_K: int = 3
    RAG_SIMILARITY_THRESHOLD: float = 0.6
    CHROMA_URL: str | None = os.getenv("CHROMA_URL") or None
    
    # Guardrail Thresholds
    PROMPT_INJECTION_THRESHOLD: float = 0.6
    HALLUCINATION_THRESHOLD: float = 0.8

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    def domain_path(self, domain_id: str) -> Path:
        normalized = domain_id.strip().lower()
        if not _DOMAIN_ID.fullmatch(normalized):
            raise ValueError("Invalid domain_id")
        return Path(self.DOMAINS_ROOT).resolve() / normalized

    def data_path(self, domain_id: str) -> Path:
        return self.domain_path(domain_id) / "data"

    def db_path_for(self, domain_id: str) -> Path:
        return self.data_path(domain_id) / "mock.db"

    def vector_db_path_for(self, domain_id: str) -> Path:
        return self.domain_path(domain_id) / ".chroma_db"

settings = AISettings()
