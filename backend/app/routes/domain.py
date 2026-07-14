from fastapi import APIRouter, Depends

from app.schemas.common import SwitchDomainRequest
from app.services.domain_service import get_domain_status, switch_domain
from app.auth.dependencies import get_current_user
from app.auth.tokens import Principal

router = APIRouter(prefix="/api/domain", tags=["Domain"])


@router.post("/switch")
def switch_active_domain(request: SwitchDomainRequest, principal: Principal = Depends(get_current_user)) -> dict[str, object]:
    return switch_domain(request.domain)


@router.get("/status")
def domain_status() -> dict[str, object]:
    return get_domain_status()
