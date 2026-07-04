from fastapi import APIRouter, Depends, Query

from app.services.ai_observability_service import AiObservabilityService

router = APIRouter(prefix="/api/ai", tags=["AI"])


def get_ai_observability_service() -> AiObservabilityService:
    return AiObservabilityService()


@router.get("/model-report")
async def model_report(
    service: AiObservabilityService = Depends(get_ai_observability_service),
) -> dict[str, object]:
    return await service.model_report()


@router.get("/agent-logs")
async def agent_logs(
    case_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    service: AiObservabilityService = Depends(get_ai_observability_service),
) -> dict[str, object]:
    return await service.agent_logs(case_id=case_id, limit=limit)
