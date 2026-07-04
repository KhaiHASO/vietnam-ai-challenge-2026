from fastapi import APIRouter, Depends

from app.services.dashboard_list_service import DashboardListService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def get_dashboard_list_service() -> DashboardListService:
    return DashboardListService()


@router.get("/overview")
async def dashboard_overview(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.dashboard_overview()
