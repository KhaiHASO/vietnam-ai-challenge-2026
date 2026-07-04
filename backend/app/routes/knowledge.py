from fastapi import APIRouter, Depends

from app.services.dashboard_list_service import DashboardListService

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


def get_dashboard_list_service() -> DashboardListService:
    return DashboardListService()


@router.get("/diseases")
def diseases(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return service.knowledge_diseases()


@router.get("/ipm")
def ipm(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return service.knowledge_ipm()
