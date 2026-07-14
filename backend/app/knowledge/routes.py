from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.auth.contracts import Principal, Role
from app.auth.dependencies import require_roles
from app.core.config import settings
from app.storage.local_storage import LocalStorage
from app.workers.main import MongoJobRepository

from .service import KnowledgeIngestionService

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge ingestion"])


def get_ingestion_service() -> KnowledgeIngestionService:
    return KnowledgeIngestionService(
        LocalStorage(
            settings.knowledge_storage_root_path,
            max_bytes=settings.upload_limit_mb * 1024 * 1024,
        ),
        MongoJobRepository(),
    )


@router.post("/ingestions", status_code=status.HTTP_202_ACCEPTED)
async def create_ingestion(
    file: UploadFile = File(...),
    domain_id: str = Form("agriculture"),
    principal: Principal = Depends(require_roles([Role.ADMIN, Role.EXPERT])),
    service: KnowledgeIngestionService = Depends(get_ingestion_service),
) -> dict[str, str]:
    try:
        return await service.enqueue_upload(file=file, principal=principal, domain_id=domain_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/ingestions/{job_id}")
async def get_ingestion_status(
    job_id: str,
    principal: Principal = Depends(require_roles([Role.ADMIN, Role.EXPERT])),
    service: KnowledgeIngestionService = Depends(get_ingestion_service),
) -> dict[str, object]:
    result = await service.get_status(job_id=job_id, principal=principal)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion job not found")
    return result
