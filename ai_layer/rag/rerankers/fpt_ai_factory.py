import os
import httpx
import logging
from typing import List
from ai_layer.rag.models import Chunk

logger = logging.getLogger(__name__)

class FPTAIReranker:
    def __init__(self, endpoint: str | None = None, model_id: str | None = None, api_key: str | None = None):
        self.endpoint = endpoint or os.getenv("FPT_AI_FACTORY_RERANK_ENDPOINT", "https://api.fpt.ai/v1/rerank")
        self.model_id = model_id or os.getenv("FPT_AI_FACTORY_RERANK_MODEL_ID", "bge-reranker-v2-m3")
        self.api_key = api_key or os.getenv("FPT_AI_FACTORY_API_KEY", "")

    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 3) -> List[Chunk]:
        if not chunks:
            return []
            
        if not self.api_key:
            logger.warning("FPT_AI_FACTORY_API_KEY is not set. FPTAIReranker will act as pass-through.")
            return chunks[:top_k]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_id,
            "query": query,
            "documents": [chunk.text for chunk in chunks],
            "top_n": top_k
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                res_data = response.json()
                
                results = res_data.get("results", [])
                
                reranked_chunks = []
                for item in results:
                    idx = item["index"]
                    score = item["relevance_score"]
                    if idx < len(chunks):
                        chunk = chunks[idx]
                        chunk.metadata.rerank_score = float(score)
                        reranked_chunks.append(chunk)
                
                if not reranked_chunks:
                    return chunks[:top_k]
                
                return reranked_chunks
        except Exception as e:
            logger.error(f"FPT AI Factory Reranker failed: {e}. Returning original ranking.")
            return chunks[:top_k]
