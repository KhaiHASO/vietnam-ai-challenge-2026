from fastapi import APIRouter

from app.services.status_service import get_health

router = APIRouter(tags=["Health"])


@router.get("/health")
def health() -> dict[str, object]:
    return get_health()
