import logging
from typing import List
from ai_layer.rag.models import Chunk

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False


class CrossEncoderReranker:
    """
    Reranks a list of Chunks using a Cross-Encoder model.
    Cross-Encoders provide higher accuracy than Bi-Encoders (like standard embeddings)
    but are slower, so they are typically applied to a small set of top-k results.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if not CROSS_ENCODER_AVAILABLE:
            logger.warning("sentence-transformers not available. CrossEncoderReranker will act as pass-through.")
            self.model = None
        else:
            try:
                logger.info(f"Loading CrossEncoder model '{model_name}'...")
                self.model = CrossEncoder(model_name)
                logger.info("CrossEncoder model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder model: {e}")
                self.model = None

    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 3) -> List[Chunk]:
        """
        Reranks the given chunks based on their relevance to the query.
        """
        if not chunks:
            return []
            
        if not self.model:
            # Fallback to original ranking (which was based on vector similarity)
            return chunks[:top_k]
            
        try:
            # Prepare pairs of (query, document)
            pairs = [[query, chunk.text] for chunk in chunks]
            
            # Predict scores
            scores = self.model.predict(pairs)
            
            # Combine chunks with their scores
            chunk_scores = list(zip(chunks, scores))
            
            # Sort by score in descending order (higher is better for CrossEncoder)
            chunk_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update metadata with reranking score and select top_k
            reranked_chunks = []
            for i, (chunk, score) in enumerate(chunk_scores[:top_k]):
                chunk.metadata.rerank_score = float(score)
                reranked_chunks.append(chunk)
                
            logger.info(f"Reranked {len(chunks)} chunks down to {len(reranked_chunks)} chunks.")
            return reranked_chunks
            
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return chunks[:top_k]
