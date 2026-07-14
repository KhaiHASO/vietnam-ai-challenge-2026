import hashlib
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from ai_layer.rag.chunkers.langchain_chunker import LangchainChunker
from ai_layer.rag.models import Document
from backend.app.storage.object_storage import ObjectStorage


class IngestionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str
    storage_path: str
    checksum: str
    index_revision: str
    chunk_count: int


class IngestionService:
    def __init__(
        self,
        storage: ObjectStorage,
        chunker: LangchainChunker,
        vector_store,
        lexical_store,
    ) -> None:
        self.storage = storage
        self.chunker = chunker
        self.vector_store = vector_store
        self.lexical_store = lexical_store
        self._by_checksum: dict[tuple[str, str, str], IngestionResult] = {}
        self._active_revisions: dict[tuple[str, str], str] = {}

    def ingest(
        self,
        original_filename: str,
        content: bytes,
        content_type: str,
        metadata: dict,
        storage_path: str | None = None,
    ) -> IngestionResult:
        tenant_id = str(metadata["tenant_id"])
        domain_id = str(metadata["domain_id"])
        checksum = hashlib.sha256(content).hexdigest()
        idempotency_key = (tenant_id, domain_id, checksum)
        if idempotency_key in self._by_checksum:
            return self._by_checksum[idempotency_key]

        storage_path = storage_path or self.storage.store(original_filename, content, content_type)
        index_revision = f"idx-{uuid4().hex}"
        document_id = str(uuid4())
        text_content = content.decode("utf-8", errors="replace")
        provenance = {
            **metadata,
            "tenant_id": tenant_id,
            "domain_id": domain_id,
            "index_revision": index_revision,
            "checksum": checksum,
            "document_status": "active",
            "source_uri": storage_path,
            "parser_version": "text-v1",
            "chunker_version": "recursive-v1",
        }
        document = Document(
            id=document_id,
            knowledge_item_id=str(metadata.get("knowledge_item_id", document_id)),
            text_content=text_content,
            metadata=provenance,
        )
        chunks = self.chunker.split([document])
        if not chunks:
            raise RuntimeError("Ingestion produced no chunks")
        for chunk in chunks:
            chunk.metadata.extra.update(provenance)

        if self.vector_store.add_chunks(chunks) is False:
            raise RuntimeError("Dense index staging failed")
        if self.lexical_store is not None and self.lexical_store.add_chunks(chunks) is False:
            raise RuntimeError("Lexical index staging failed")

        result = IngestionResult(
            document_id=document_id,
            storage_path=storage_path,
            checksum=checksum,
            index_revision=index_revision,
            chunk_count=len(chunks),
        )
        self._active_revisions[(tenant_id, domain_id)] = index_revision
        self._by_checksum[idempotency_key] = result
        return result

    def active_revision(self, tenant_id: str, domain_id: str) -> str | None:
        return self._active_revisions.get((tenant_id, domain_id))
