from typing import List, Dict, Any, Optional
from ai_layer.rag.models import Chunk
from ai_layer.rag.vectorstores.chroma_store import ChromaVectorStore
from ai_layer.rag.retrieval.lexical import LexicalRetriever

class ReciprocalRankFusion:
    @staticmethod
    def fuse(results_lists: List[List[Chunk]], k: int = 60) -> List[Chunk]:
        chunk_map: Dict[str, Chunk] = {}
        score_map: Dict[str, float] = {}
        
        for results in results_lists:
            for rank, chunk in enumerate(results, start=1):
                if chunk.id not in chunk_map:
                    chunk_map[chunk.id] = chunk
                    score_map[chunk.id] = 0.0
                score_map[chunk.id] += 1.0 / (k + rank)
                
        sorted_ids = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        return [chunk_map[cid] for cid in sorted_ids]

class HybridRetriever:
    def __init__(self, dense_store: ChromaVectorStore, lexical_store: LexicalRetriever):
        self.dense = dense_store
        self.lexical = lexical_store
        
    def retrieve(self, query: str, query_embedding: List[float], top_k: int = 5, filters: Optional[dict] = None) -> List[Chunk]:
        dense_results = self.dense.similarity_search(query_embedding, top_k=top_k, filters=filters)
        lexical_results = self.lexical.search(query, top_k=top_k, filters=filters)
        
        fused = ReciprocalRankFusion.fuse([dense_results, lexical_results])
        return fused[:top_k]
