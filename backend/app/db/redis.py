"""Process-wide Redis connection used by durable RAG state and rate limits."""

from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass
class RedisState:
    client: Any | None = None
    connected: bool = False
    last_error: str | None = None


redis_state = RedisState()


async def connect_to_redis() -> Any | None:
    try:
        from redis.asyncio import Redis
    except ModuleNotFoundError:
        redis_state.client = None
        redis_state.connected = False
        redis_state.last_error = "RedisDependencyMissing"
        return None
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.ping()
    except Exception as exc:
        await client.aclose()
        redis_state.client = None
        redis_state.connected = False
        redis_state.last_error = exc.__class__.__name__
        return None
    redis_state.client = client
    redis_state.connected = True
    redis_state.last_error = None
    return client


async def close_redis_connection() -> None:
    if redis_state.client is not None:
        await redis_state.client.aclose()
    redis_state.client = None
    redis_state.connected = False
