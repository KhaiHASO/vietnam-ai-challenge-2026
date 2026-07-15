from fastapi import APIRouter, Depends

from app.services.dashboard_list_service import DashboardListService

router = APIRouter(prefix="/api/cooperative", tags=["Cooperative"])


def get_dashboard_list_service() -> DashboardListService:
    return DashboardListService()


@router.get("/disease-map")
async def disease_map(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.cooperative_disease_map()


@router.get("/outbreaks")
async def cooperative_outbreaks(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.get_outbreak_alerts()
