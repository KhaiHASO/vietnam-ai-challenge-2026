import os
import logging
from typing import List
from ai_layer.rag.interfaces.embedding import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Embedding Provider using Google Gemini API directly via HTTP.
    Reads GEMINI_API_KEY from environment.
    """
    
    def __init__(self, model_name: str = None, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set.")
            
        self.model_name = model_name or os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        if self.model_name.startswith("models/"):
            self.model_name = self.model_name[7:]
            
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:embedContent?key={self.api_key}"

    def embed_query(self, text: str) -> List[float]:
        try:
            import requests
        except ImportError as exc:
            raise ImportError("requests library is not installed. Run `pip install requests`") from exc

        payload = {
            "model": f"models/{self.model_name}",
            "content": {
                "parts": [{"text": text}]
            }
        }
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]["values"]
        except Exception as e:
            logger.error(f"Error embedding query with Gemini HTTP: {e}")
            if isinstance(e, requests.exceptions.HTTPError):
                logger.error(e.response.text)
            raise ValueError(f"Lỗi khi embed query: {e}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # For simplicity, if multiple texts, we can batch them using batchEmbedContents, 
        # but wait, batchEmbedContents has a different URL.
        # Let's just loop over them since it's just for mock data
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings
