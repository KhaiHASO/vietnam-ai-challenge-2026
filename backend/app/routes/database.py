from fastapi import APIRouter

from app.services.database_service import get_database_state, reset_database_state

router = APIRouter(prefix="/api", tags=["Database"])


@router.get("/database")
def database_state() -> dict[str, object]:
    return get_database_state()


@router.post("/database/reset")
def reset_database() -> dict[str, object]:
    return reset_database_state()
