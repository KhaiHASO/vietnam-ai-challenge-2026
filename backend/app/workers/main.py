"""Small idempotent worker core; transport adapters can drive ``run_once``."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable
import asyncio
import random
from contextlib import suppress

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from app.db.mongo import get_database


@dataclass
class Job:
    job_id: str
    job_type: str
    idempotency_key: str
    payload: dict[str, Any]
    attempts: int = 0
    status: str = "queued"
    next_run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_error: str | None = None


class InMemoryJobRepository:
    def __init__(self) -> None:
        self.jobs: dict[str, Job] = {}
        self.keys: dict[str, str] = {}

    async def enqueue(self, job: Job) -> Job:
        existing = self.keys.get(job.idempotency_key)
        if existing:
            return self.jobs[existing]
        self.jobs[job.job_id] = job
        self.keys[job.idempotency_key] = job.job_id
        return job

    async def claim_next(self, now: datetime) -> Job | None:
        candidates = [job for job in self.jobs.values() if job.status in {"queued", "retrying"} and job.next_run_at <= now]
        if not candidates:
            return None
        job = min(candidates, key=lambda item: item.next_run_at)
        job.status = "running"
        return job

    async def save(self, job: Job) -> None:
        self.jobs[job.job_id] = job


class MongoJobRepository:
    """Mongo job transport with idempotency-key de-duplication."""

    def __init__(self, collection: Any | None = None) -> None:
        self._collection = collection

    @property
    def collection(self) -> Any:
        return self._collection if self._collection is not None else get_database().jobs

    @staticmethod
    def _document(job: Job) -> dict[str, Any]:
        return {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "idempotency_key": job.idempotency_key,
            "payload": job.payload,
            "attempts": job.attempts,
            "status": job.status,
            "next_run_at": job.next_run_at,
            "last_error": job.last_error,
        }

    @staticmethod
    def _job(document: dict[str, Any]) -> Job:
        document.pop("_id", None)
        return Job(**document)

    async def enqueue(self, job: Job) -> Job:
        try:
            await self.collection.insert_one(self._document(job))
            return job
        except DuplicateKeyError:
            existing = await self.collection.find_one({"idempotency_key": job.idempotency_key})
            if existing is None:
                raise
            return self._job(existing)

    async def get_for_tenant(self, job_id: str, tenant_id: str) -> Job | None:
        document = await self.collection.find_one(
            {"job_id": job_id, "payload.tenant_id": tenant_id}
        )
        return self._job(document) if document else None

    async def claim_next(self, now: datetime) -> Job | None:
        document = await self.collection.find_one_and_update(
            {"status": {"$in": ["queued", "retrying"]}, "next_run_at": {"$lte": now}},
            {"$set": {"status": "running"}},
            sort=[("next_run_at", 1)],
            return_document=ReturnDocument.AFTER,
        )
        return self._job(document) if document else None

    async def save(self, job: Job) -> None:
        await self.collection.replace_one({"job_id": job.job_id}, self._document(job), upsert=False)


class RedisLease:
    """Token-owned Redis lease; heartbeat/release are atomic Lua compare-and-set calls."""

    def __init__(self, redis_client: Any, *, owner: str, ttl_seconds: int = 60) -> None:
        if not owner or ttl_seconds <= 0:
            raise ValueError("Lease owner and TTL are required")
        self.redis = redis_client
        self.owner = owner
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _key(job_id: str) -> str:
        return f"rag:jobs:lease:v1:{job_id}"

    async def acquire(self, job_id: str) -> bool:
        return bool(await self.redis.set(self._key(job_id), self.owner, nx=True, ex=self.ttl_seconds))

    async def heartbeat(self, job_id: str) -> bool:
        result = await self.redis.eval(
            "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('expire', KEYS[1], ARGV[2]) else return 0 end",
            1,
            self._key(job_id),
            self.owner,
            str(self.ttl_seconds),
        )
        return bool(result)

    async def release(self, job_id: str) -> bool:
        result = await self.redis.eval(
            "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end",
            1,
            self._key(job_id),
            self.owner,
        )
        return bool(result)


Handler = Callable[[Job], Awaitable[None]]


class JobWorker:
    def __init__(
        self,
        repository: Any,
        handlers: dict[str, Handler],
        *,
        lease: Any | None = None,
        max_attempts: int = 3,
        base_delay_seconds: int = 1,
        retry_jitter: Callable[[float], float] | None = None,
    ) -> None:
        if max_attempts < 1 or base_delay_seconds < 0:
            raise ValueError("Invalid worker retry configuration")
        self.repository = repository
        self.handlers = handlers
        self.lease = lease
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.retry_jitter = retry_jitter or (lambda delay: random.uniform(0, delay * 0.2))

    async def run_once(self) -> Job | None:
        job = await self.repository.claim_next(datetime.now(timezone.utc))
        if job is None:
            return None
        has_lease = False
        if self.lease is not None:
            has_lease = await self.lease.acquire(job.job_id)
            if not has_lease:
                job.status = "retrying"
                job.next_run_at = datetime.now(timezone.utc) + timedelta(seconds=max(1, self.base_delay_seconds))
                await self.repository.save(job)
                return job
        handler = self.handlers.get(job.job_type)
        heartbeat_stop = asyncio.Event()
        lease_lost = False

        async def heartbeat() -> None:
            nonlocal lease_lost
            interval = max(0.01, float(getattr(self.lease, "ttl_seconds", 60)) / 3)
            while True:
                try:
                    await asyncio.wait_for(heartbeat_stop.wait(), timeout=interval)
                    return
                except TimeoutError:
                    if not await self.lease.heartbeat(job.job_id):
                        lease_lost = True
                        return

        heartbeat_task = asyncio.create_task(heartbeat()) if has_lease else None
        try:
            if handler is None:
                job.status, job.last_error = "dead_letter", "unknown_job_type"
            else:
                await handler(job)
                if lease_lost:
                    raise ConnectionError("job lease was lost while processing")
                job.status, job.last_error = "completed", None
        except (TimeoutError, ConnectionError) as error:
            job.attempts += 1
            if job.attempts >= self.max_attempts:
                job.status = "dead_letter"
            else:
                job.status = "retrying"
                delay = self.base_delay_seconds * (2 ** (job.attempts - 1))
                jitter = min(max(0, self.retry_jitter(delay)), delay * 0.2)
                job.next_run_at = datetime.now(timezone.utc) + timedelta(seconds=delay + jitter)
            job.last_error = error.__class__.__name__
        except Exception as error:
            job.status, job.last_error = "dead_letter", error.__class__.__name__
        finally:
            heartbeat_stop.set()
            if heartbeat_task is not None:
                heartbeat_task.cancel()
                with suppress(asyncio.CancelledError):
                    await heartbeat_task
            if has_lease:
                await self.lease.release(job.job_id)
            await self.repository.save(job)
        return job


async def run_forever(worker: JobWorker, *, poll_seconds: float = 0.5) -> None:
    while True:
        job = await worker.run_once()
        await asyncio.sleep(0 if job is not None else poll_seconds)


async def _runtime_main() -> None:
    import os
    import socket
    from redis.asyncio import Redis
    from app.db.mongo import close_mongo_connection, connect_to_mongo
    from app.core.config import settings
    from app.knowledge.service import build_runtime_handlers

    await connect_to_mongo()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await run_forever(JobWorker(
            MongoJobRepository(),
            build_runtime_handlers(),
            lease=RedisLease(redis, owner=f"{socket.gethostname()}:{os.getpid()}"),
        ))
    finally:
        await redis.aclose()
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(_runtime_main())
