import os
from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    # LLM Settings
    PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")  # ollama, openai, gemini
    MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama3.2")
    API_KEY: str = os.getenv("AI_API_KEY", "")
    BASE_URL: str = os.getenv("AI_BASE_URL", "http://localhost:11434")
    TEMPERATURE: float = 0.2
    
    # RAG Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")  # local, openai, gemini
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vector_store.json")
    RAG_TOP_K: int = 3
    RAG_SIMILARITY_THRESHOLD: float = 0.4
    
    # Guardrail Thresholds
    PROMPT_INJECTION_THRESHOLD: float = 0.6
    HALLUCINATION_THRESHOLD: float = 0.5
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = AISettings()
