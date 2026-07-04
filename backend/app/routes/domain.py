from fastapi import APIRouter

from app.schemas.common import SwitchDomainRequest
from app.services.domain_service import get_domain_status, switch_domain

router = APIRouter(prefix="/api/domain", tags=["Domain"])


@router.post("/switch")
def switch_active_domain(request: SwitchDomainRequest) -> dict[str, object]:
    return switch_domain(request.domain)


@router.get("/status")
def domain_status() -> dict[str, object]:
    return get_domain_status()
