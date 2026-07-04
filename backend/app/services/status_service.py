from ai_layer.config import settings as ai_settings

from app.core.config import settings
from app.db.mongo import mongo_status


def get_health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.demo_mode,
    }


def get_status() -> dict[str, object]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "demo_mode": settings.demo_mode,
        "ai_service_url": settings.ai_service_url,
        "active_domain": ai_settings.ACTIVE_DOMAIN,
        "database": mongo_status(),
    }
