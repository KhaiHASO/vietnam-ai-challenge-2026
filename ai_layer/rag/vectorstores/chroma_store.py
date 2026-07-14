import os
import logging
import math
from urllib.parse import urlsplit
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
    def __init__(self, embedding_provider: BaseEmbeddingProvider, persist_directory: str = "./.chroma_db", collection_name: str = "rag_core", *, chroma_url: str | None = None, allow_in_memory_fallback: bool = False):
        self.embedding_provider = embedding_provider
        self._memory_chunks: dict[str, Chunk] | None = None
        if not CHROMADB_AVAILABLE:
            if not allow_in_memory_fallback:
                raise ImportError("chromadb is not installed")
            self._memory_chunks = {}
            self.client = None
            self.collection = None
            return
        if chroma_url:
            endpoint = urlsplit(chroma_url)
            if endpoint.scheme not in {"http", "https"} or not endpoint.hostname:
                raise ValueError("Chroma URL must be an absolute HTTP(S) URL")
            self.client = chromadb.HttpClient(
                host=endpoint.hostname,
                port=endpoint.port or (443 if endpoint.scheme == "https" else 80),
                ssl=endpoint.scheme == "https",
            )
        else:
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

        if self._memory_chunks is not None:
            for chunk in chunks:
                if not chunk.id:
                    raise ValueError("Chunk id is required")
                self._memory_chunks[chunk.id] = chunk.model_copy(deep=True)
            return True

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
        if self._memory_chunks is not None:
            ranked: list[tuple[float, Chunk]] = []
            for chunk in self._memory_chunks.values():
                if filters and any(
                    chunk.metadata.extra.get(key) != value
                    for key, value in filters.items()
                ):
                    continue
                embedding = chunk.embedding or []
                denominator = math.sqrt(sum(v * v for v in embedding)) * math.sqrt(
                    sum(v * v for v in query_embedding)
                )
                similarity = (
                    sum(a * b for a, b in zip(embedding, query_embedding)) / denominator
                    if denominator
                    else 0.0
                )
                result = chunk.model_copy(deep=True)
                result.metadata.extra["similarity_distance"] = 1.0 - similarity
                ranked.append((similarity, result))
            ranked.sort(key=lambda item: item[0], reverse=True)
            return [chunk for _, chunk in ranked[:top_k]]
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
                # Reconstruct extra metadata fields
                extra_meta = {"similarity_distance": results["distances"][0][i]}
                reserved_keys = {"source_id", "source_type", "chunk_index", "total_chunks", "rerank_score"}
                for k, v in meta.items():
                    if k not in reserved_keys:
                        extra_meta[k] = v

                meta_model = ChunkMetadataModel(
                    source_id=meta.get("source_id", ""),
                    source_type=meta.get("source_type", ""),
                    chunk_index=meta.get("chunk_index", 0),
                    total_chunks=meta.get("total_chunks", 1),
                    rerank_score=meta.get("rerank_score"),
                    extra=extra_meta,
                )
                chunk = Chunk(id=chunk_id, text=text, metadata=meta_model)
                chunks.append(chunk)
            return chunks
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
