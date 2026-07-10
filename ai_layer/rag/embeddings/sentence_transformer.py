from typing import List

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class SentenceTransformerSingleton:
    """Singleton pattern for SentenceTransformer model to load weights only once."""

    _instance = None

    def __new__(cls, model_name: str = "keepitreal/vietnamese-sbert"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
            cls._instance.model_name = model_name
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")
        print(f"Loading Embedding model '{self.model_name}'...")
        self.model = SentenceTransformer(self.model_name)
        print("Embedding model loaded.")

    def encode(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.encode([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.encode(texts)


class LocalEmbeddingProvider:
    """Embedding Provider using local huggingface models."""

    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert"):
        self.embedding_engine = SentenceTransformerSingleton(model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.embedding_engine.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_engine.embed_documents(texts)
