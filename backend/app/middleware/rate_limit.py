"""Redis-backed fixed-window protection with a development-only fallback."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    window_seconds = 60

    def __init__(self, app):
        super().__init__(app)
        self.request_counts: dict[str, dict[str, float]] = {}

    @staticmethod
    def _limit_for(request: Request) -> int | None:
        if request.url.path.endswith("/status"):
            return 5
        if request.url.path.startswith("/api/v1/copilot"):
            return 30
        if request.url.path.startswith("/api/"):
            return 120
        return None

    async def _increment(self, request: Request, limit: int) -> bool:
        client_ip = request.client.host if request.client else "unknown"
        bucket = int(time.time() // self.window_seconds)
        key = f"rate-limit:v1:{request.url.path}:{client_ip}:{bucket}"
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self.window_seconds)
            return count <= limit

        if settings.environment == "production":
            raise RuntimeError("Redis rate limiter is unavailable")
        now = time.time()
        self.request_counts = {
            existing_key: value
            for existing_key, value in self.request_counts.items()
            if now - value["start_time"] < self.window_seconds
        }
        record = self.request_counts.setdefault(key, {"count": 0, "start_time": now})
        record["count"] += 1
        return record["count"] <= limit

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        limit = self._limit_for(request)
        if limit is not None:
            try:
                allowed = await self._increment(request, limit)
            except Exception:
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_UNAVAILABLE",
                            "message": "Request protection is temporarily unavailable",
                            "status_code": 503,
                            "trace_id": getattr(request.state, "trace_id", "unknown"),
                            "retryable": True,
                        },
                    },
                )
            if not allowed:
                trace_id = getattr(request.state, "trace_id", "unknown")
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too Many Requests",
                            "status_code": 429,
                            "trace_id": trace_id,
                            "retryable": True,
                        },
                    },
                    headers={"retry-after": str(self.window_seconds)},
                )
        return await call_next(request)
