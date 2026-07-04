from fastapi import APIRouter, Depends

from app.services.dashboard_list_service import DashboardListService

router = APIRouter(prefix="/api", tags=["Lists"])


def get_dashboard_list_service() -> DashboardListService:
    return DashboardListService()


@router.get("/farms")
async def farms(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.list_farms()


@router.get("/season-logs")
async def season_logs(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.season_logs()


@router.get("/reminders")
async def reminders(
    service: DashboardListService = Depends(get_dashboard_list_service),
) -> dict[str, object]:
    return await service.reminders()
