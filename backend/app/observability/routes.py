from fastapi import APIRouter, Depends, Response

from app.auth.contracts import Role
from app.auth.dependencies import require_roles

from .metrics import metrics

router = APIRouter(prefix="/api/v1/observability", tags=["Observability"])


@router.get("/metrics", dependencies=[Depends(require_roles([Role.ADMIN, Role.EXPERT]))])
async def get_metrics() -> Response:
    return Response(metrics.render(), media_type="text/plain; version=0.0.4")
