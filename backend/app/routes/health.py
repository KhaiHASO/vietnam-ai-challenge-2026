from typing import Callable

import httpx
from fastapi import APIRouter, Response

from ai_layer.rag.registries.catalog import RegistryCatalog

from app.core.config import settings
from app.db.mongo import mongo_status
from app.services.status_service import get_health

router = APIRouter(tags=["Health"])

@router.get("/health/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}

@router.get("/health/ready")
def readiness(response: Response) -> dict[str, object]:
    dependencies = get_readiness_dependencies()
    if not all(dependencies.values()):
        response.status_code = 503
        return {"status": "unavailable", "dependencies": dependencies}
    return {"status": "ready", "dependencies": dependencies}


def _safe_probe(probe: Callable[[], bool]) -> bool:
    try:
        return bool(probe())
    except Exception:
        return False


def _mongo_ready() -> bool:
    status = mongo_status()
    return bool(status.get("connected", False)) if isinstance(status, dict) else False


def _redis_ready() -> bool:
    from redis import Redis

    client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=0.25,
        socket_timeout=0.25,
    )
    try:
        return bool(client.ping())
    finally:
        client.close()


def _chroma_ready() -> bool:
    base_url = settings.chroma_url.rstrip("/")
    for path in ("/api/v2/heartbeat", "/api/v1/heartbeat"):
        try:
            if httpx.get(f"{base_url}{path}", timeout=0.25).is_success:
                return True
        except httpx.HTTPError:
            continue
    return False


def _registry_ready() -> bool:
    return RegistryCatalog().resolve_request_context("agriculture", "single") is not None


def _primary_provider_ready() -> bool:
    if settings.primary_ai_provider == "deepseek":
        return bool(
            settings.deepseek_api_key
            and settings.deepseek_api_key.get_secret_value().strip()
        )
    return True


def get_readiness_dependencies() -> dict[str, bool]:
    return {
        "mongo": _safe_probe(_mongo_ready),
        "redis": _safe_probe(_redis_ready),
        "chroma": _safe_probe(_chroma_ready),
        "registry": _safe_probe(_registry_ready),
        "primary_provider": _safe_probe(_primary_provider_ready),
    }

@router.get("/health")
def health() -> dict[str, object]:
    return get_health()
