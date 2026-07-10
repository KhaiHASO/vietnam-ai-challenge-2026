import time
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """
    A very simple in-memory rate limiter middleware.
    In production, this should be replaced with Redis-based rate limiting (like slowapi + Redis).
    """
    def __init__(self, app, max_requests: int = 15, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate limit API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "127.0.0.1"
        # Can also use X-Forwarded-For if behind a proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]
            
        now = time.time()
        
        # Clean up old timestamps
        self.ip_records[client_ip] = [t for t in self.ip_records[client_ip] if now - t < self.window_seconds]
        
        if len(self.ip_records[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests. Quota exceeded."}
            )
            
        self.ip_records[client_ip].append(now)
        response = await call_next(request)
        return response
