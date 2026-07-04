import os
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    # Active Domain
    ACTIVE_DOMAIN: str = os.getenv("ACTIVE_DOMAIN", "agriculture")  # sme, education, agriculture
    
    # LLM Settings
    PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")  # ollama, openai, gemini
    MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama3.2")
    API_KEY: str = os.getenv("AI_API_KEY", "")
    BASE_URL: str = os.getenv("AI_BASE_URL", "http://localhost:11434")
    TEMPERATURE: float = 0.2
    
    # RAG Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")  # local, openai, gemini
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    RAG_TOP_K: int = 3
    RAG_SIMILARITY_THRESHOLD: float = 0.4
    
    # Guardrail Thresholds
    PROMPT_INJECTION_THRESHOLD: float = 0.6
    HALLUCINATION_THRESHOLD: float = 0.5
    
    @property
    def domain_dir(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "domains", self.ACTIVE_DOMAIN)

    @property
    def db_path(self) -> str:
        return os.path.join(self.domain_dir, "data", "db_state.json")

    @property
    def vector_db_path(self) -> str:
        return os.path.join(self.domain_dir, "data", "vector_store.json")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = AISettings()
