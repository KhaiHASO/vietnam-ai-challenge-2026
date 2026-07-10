import logging
from typing import List, Dict, Any, Optional
from ai_layer.rag.interfaces.retriever import BaseRetriever
from ai_layer.rag.interfaces.vectorstore import BaseVectorStore
from ai_layer.rag.interfaces.embedding import BaseEmbeddingProvider
from ai_layer.rag.interfaces.llm import BaseLLMProvider
from ai_layer.rag.models import Chunk
from ai_layer.rag.retrievers.reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)


class CoreRetriever(BaseRetriever):
    """Pipeline: HyDE → Embed → Vector Search → Threshold filter → Rerank."""

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
        llm_provider: Optional[BaseLLMProvider] = None,
        top_k: int = 3,
        similarity_threshold: float = 0.6,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.reranker = CrossEncoderReranker()
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        if not query or query.strip() == "":
            return []

        search_query = query

        # HyDE query expansion
        if self.llm_provider:
            hyde_prompt = (
                "Viết đoạn văn ngắn trả lời chi tiết câu hỏi sau để hỗ trợ tìm kiếm tài liệu.\n"
                f"Câu hỏi: {query}"
            )
            try:
                hypothetical = self.llm_provider.generate(
                    prompt=hyde_prompt,
                    system_prompt="Trợ lý tạo câu trả lời giả định (HyDE).",
                )
                if hypothetical:
                    search_query = hypothetical
                    logger.info(f"[HyDE] {search_query[:100]}...")
            except Exception as e:
                logger.warning(f"[HyDE] fallback original: {e}")

        query_embedding = self.embedding_provider.embed_query(search_query)
        fetch_k = max(self.top_k * 3, 10)
        chunks = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=fetch_k,
            filters=filters,
        )

        # Threshold filter — only apply when threshold < 1.0 and we have enough results
        good = chunks
        if self.similarity_threshold < 1.0 and len(chunks) > self.top_k:
            good = []
            for c in chunks:
                dist = c.metadata.extra.get("similarity_distance", 99) if hasattr(c.metadata, "extra") else 99
                if dist <= self.similarity_threshold:
                    good.append(c)
            if not good:
                good = chunks[:self.top_k]

        if good:
            good = self.reranker.rerank(query=search_query, chunks=good, top_k=top_k)

        logger.info(f"[Retriever] {len(chunks)}→{len(good)} chunks")
        return good
