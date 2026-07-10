import os
import logging
from typing import List, Dict, Any, Optional
from ai_layer.rag.interfaces.vectorstore import BaseVectorStore
from ai_layer.rag.interfaces.embedding import BaseEmbeddingProvider
from ai_layer.rag.models import Chunk, ChunkMetadataModel

logger = logging.getLogger(__name__)

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, embedding_provider: BaseEmbeddingProvider, persist_directory: str = "./.chroma_db", collection_name: str = "rag_core"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb is not installed")
        self.embedding_provider = embedding_provider
        abs_persist_dir = os.path.abspath(persist_directory)
        self.client = chromadb.PersistentClient(path=abs_persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[Chunk], *, sys_hash: str | None = None) -> bool:
        if not chunks:
            return True
        ids = []
        documents = []
        metadatas = []
        embeddings_for_chroma = []
        texts_to_embed = []
        chunks_to_embed = []

        for chunk in chunks:
            if chunk.embedding is None:
                texts_to_embed.append(chunk.text)
                chunks_to_embed.append(chunk)

        if texts_to_embed:
            embeddings = self.embedding_provider.embed_documents(texts_to_embed)
            for i, chunk in enumerate(chunks_to_embed):
                chunk.embedding = embeddings[i]

        for chunk in chunks:
            ids.append(chunk.id)
            documents.append(chunk.text)
            meta = chunk.metadata
            safe_metadata = {
                "source_id": meta.source_id,
                "source_type": meta.source_type,
                "chunk_index": meta.chunk_index,
                "total_chunks": meta.total_chunks,
            }
            if meta.rerank_score is not None:
                safe_metadata["rerank_score"] = meta.rerank_score
            if meta.extra:
                for k, v in meta.extra.items():
                    if isinstance(v, (str, int, float, bool)):
                        safe_metadata[k] = v
            metadatas.append(safe_metadata)
            embeddings_for_chroma.append(chunk.embedding)

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings_for_chroma,
                metadatas=metadatas,
                documents=documents,
            )
            return True
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB: {e}")
            return False

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters if filters else None,
                include=["metadatas", "documents", "distances"],
            )
            chunks = []
            if not results["ids"] or not results["ids"][0]:
                return chunks
            for i in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][i]
                text = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                meta_model = ChunkMetadataModel(
                    source_id=meta.get("source_id", ""),
                    source_type=meta.get("source_type", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    total_chunks=meta.get("total_chunks", 1),
                    rerank_score=meta.get("rerank_score"),
                    extra={"similarity_distance": results["distances"][0][i]},
                )
                chunk = Chunk(id=chunk_id, text=text, metadata=meta_model)
                chunks.append(chunk)
            return chunks
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
