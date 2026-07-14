from __future__ import annotations

import hashlib
from typing import Any
from uuid import uuid4

from fastapi import UploadFile

from app.auth.contracts import Principal
from app.core.config import settings
from app.storage.object_storage import ObjectStorage
from app.storage.local_storage import LocalStorage
from app.workers.main import Job


class KnowledgeIngestionService:
    def __init__(self, storage: ObjectStorage, jobs: Any) -> None:
        self.storage = storage
        self.jobs = jobs

    async def enqueue_upload(self, *, file: UploadFile, principal: Principal, domain_id: str) -> dict[str, str]:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded document is empty")
        content_type = file.content_type or "application/octet-stream"
        storage_path = self.storage.store(file.filename or "upload", content, content_type)
        checksum = hashlib.sha256(content).hexdigest()
        job = await self.jobs.enqueue(Job(
            job_id=str(uuid4()),
            job_type="knowledge.ingest",
            idempotency_key=f"knowledge:{principal.tenant_id}:{domain_id}:{checksum}",
            payload={
                "storage_path": storage_path,
                "filename": file.filename or "upload",
                "content_type": content_type,
                "tenant_id": principal.tenant_id,
                "domain_id": domain_id,
                "requested_by": principal.user_id,
            },
        ))
        return {"job_id": job.job_id, "status": job.status}

    async def get_status(
        self, *, job_id: str, principal: Principal
    ) -> dict[str, object] | None:
        job = await self.jobs.get_for_tenant(job_id, principal.tenant_id)
        if job is None:
            return None
        return {
            "job_id": job.job_id,
            "status": job.status,
            "attempts": job.attempts,
            "last_error": job.last_error,
        }


def build_ingestion_handler(storage: ObjectStorage, processor: Any):
    """Build a worker handler that indexes the already validated object-store blob."""
    async def handle(job: Job) -> None:
        payload = job.payload
        content = storage.retrieve(str(payload["storage_path"]))
        processor.ingest(
            original_filename=str(payload["filename"]),
            content=content,
            content_type=str(payload["content_type"]),
            metadata={"tenant_id": payload["tenant_id"], "domain_id": payload["domain_id"]},
            storage_path=str(payload["storage_path"]),
        )
    return handle


def build_runtime_handlers() -> dict[str, Any]:
    """Create lazy per-domain processors for the background worker process."""
    from ai_layer.rag.service import RAGService

    storage = LocalStorage(
        settings.knowledge_storage_root_path,
        max_bytes=settings.upload_limit_mb * 1024 * 1024,
    )
    return RAGService.build_ingestion_handlers(
        storage=storage,
        lexical_root=settings.knowledge_storage_root_path.parent / "lexical",
    )
