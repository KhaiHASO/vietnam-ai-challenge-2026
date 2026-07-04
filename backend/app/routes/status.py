from fastapi import APIRouter

from app.services.status_service import get_status

router = APIRouter(prefix="/api", tags=["Status"])


@router.get("/status")
def status() -> dict[str, object]:
    return get_status()
