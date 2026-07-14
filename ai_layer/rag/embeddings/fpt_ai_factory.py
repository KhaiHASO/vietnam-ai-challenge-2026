import os
import httpx
import logging
from typing import List

logger = logging.getLogger(__name__)

class FPTAIEmbeddingProvider:
    def __init__(self, endpoint: str | None = None, model_id: str | None = None, api_key: str | None = None):
        self.endpoint = endpoint or os.getenv("FPT_AI_FACTORY_EMBEDDING_ENDPOINT", "https://api.fpt.ai/v1/embeddings")
        self.model_id = model_id or os.getenv("FPT_AI_FACTORY_EMBEDDING_MODEL_ID", "bge-m3")
        self.api_key = api_key or os.getenv("FPT_AI_FACTORY_API_KEY", "")

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            logger.warning("FPT_AI_FACTORY_API_KEY is not set. Returning mock embeddings.")
            return [[1.0] + [0.0] * 1023 for _ in texts]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_id,
            "input": texts
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                res_data = response.json()
                embeddings = [item["embedding"] for item in res_data["data"]]
                return embeddings
        except Exception as e:
            logger.error(f"FPT AI Factory Embedding failed: {e}. Returning mock embeddings.")
            return [[1.0] + [0.0] * 1023 for _ in texts]
