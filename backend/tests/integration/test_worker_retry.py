import pytest
import asyncio
from pymongo.errors import DuplicateKeyError

from app.workers.main import InMemoryJobRepository, Job, JobWorker, MongoJobRepository, RedisLease
from app.db.schema import REQUIRED_COLLECTION_NAMES


def test_job_queue_has_a_validated_collection() -> None:
    assert "jobs" in REQUIRED_COLLECTION_NAMES


@pytest.mark.asyncio
async def test_transient_job_retries_within_budget_then_completes() -> None:
    attempts = 0

    async def handler(job: Job) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise TimeoutError("provider unavailable")

    repository = InMemoryJobRepository()
    job = Job(job_id="j1", job_type="ingest", idempotency_key="k1", payload={})
    await repository.enqueue(job)
    worker = JobWorker(repository, {"ingest": handler}, max_attempts=2, base_delay_seconds=0)
    assert (await worker.run_once()).status == "retrying"
    assert (await worker.run_once()).status == "completed"
    assert attempts == 2


@pytest.mark.asyncio
async def test_permanent_job_failure_enters_dead_letter_without_retry() -> None:
    async def handler(job: Job) -> None:
        raise ValueError("invalid document")

    repository = InMemoryJobRepository()
    await repository.enqueue(Job(job_id="j2", job_type="ingest", idempotency_key="k2", payload={}))
    result = await JobWorker(repository, {"ingest": handler}).run_once()
    assert result.status == "dead_letter"


class FakeJobsCollection:
    def __init__(self) -> None:
        self.documents: dict[str, dict] = {}

    async def insert_one(self, document):
        if document["idempotency_key"] in self.documents:
            raise DuplicateKeyError("duplicate")
        self.documents[document["idempotency_key"]] = dict(document)

    async def find_one(self, selector):
        document = self.documents.get(selector["idempotency_key"])
        return dict(document) if document else None


@pytest.mark.asyncio
async def test_mongo_job_repository_reuses_the_idempotency_record() -> None:
    repository = MongoJobRepository(FakeJobsCollection())
    first = await repository.enqueue(Job(job_id="j3", job_type="ingest", idempotency_key="same", payload={}))
    second = await repository.enqueue(Job(job_id="j4", job_type="ingest", idempotency_key="same", payload={}))
    assert second.job_id == first.job_id


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def set(self, key, value, nx=False, ex=None):
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    async def eval(self, script, count, key, owner, *args):
        if self.values.get(key) != owner:
            return 0
        if "del" in script:
            del self.values[key]
        return 1


@pytest.mark.asyncio
async def test_redis_lease_prevents_two_workers_from_holding_one_job() -> None:
    redis = FakeRedis()
    first = RedisLease(redis, owner="worker-1", ttl_seconds=30)
    second = RedisLease(redis, owner="worker-2", ttl_seconds=30)
    assert await first.acquire("job-lease")
    assert not await second.acquire("job-lease")
    assert await first.release("job-lease")
    assert await second.acquire("job-lease")


@pytest.mark.asyncio
async def test_worker_does_not_execute_when_another_worker_holds_the_lease() -> None:
    executed = False

    class BusyLease:
        async def acquire(self, job_id: str) -> bool:
            return False

        async def release(self, job_id: str) -> bool:
            return True

    async def handler(job: Job) -> None:
        nonlocal executed
        executed = True

    repository = InMemoryJobRepository()
    await repository.enqueue(Job(job_id="j4", job_type="ingest", idempotency_key="k4", payload={}))
    result = await JobWorker(repository, {"ingest": handler}, lease=BusyLease()).run_once()
    assert result.status == "retrying"
    assert executed is False


@pytest.mark.asyncio
async def test_worker_heartbeats_a_lease_while_a_long_job_is_running() -> None:
    class Lease:
        ttl_seconds = 0.03

        def __init__(self) -> None:
            self.heartbeats = 0

        async def acquire(self, job_id: str) -> bool:
            return True

        async def heartbeat(self, job_id: str) -> bool:
            self.heartbeats += 1
            return True

        async def release(self, job_id: str) -> bool:
            return True

    async def handler(job: Job) -> None:
        await asyncio.sleep(0.08)

    repository = InMemoryJobRepository()
    await repository.enqueue(Job(job_id="j-heartbeat", job_type="ingest", idempotency_key="heartbeat", payload={}))
    lease = Lease()

    result = await JobWorker(repository, {"ingest": handler}, lease=lease).run_once()

    assert result.status == "completed"
    assert lease.heartbeats >= 1


@pytest.mark.asyncio
async def test_worker_adds_bounded_jitter_to_transient_retry_backoff() -> None:
    async def handler(job: Job) -> None:
        raise TimeoutError("temporary")

    repository = InMemoryJobRepository()
    await repository.enqueue(Job(job_id="j-jitter", job_type="ingest", idempotency_key="jitter", payload={}))
    before = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
    result = await JobWorker(
        repository,
        {"ingest": handler},
        base_delay_seconds=10,
        retry_jitter=lambda delay: 0.5,
    ).run_once()

    assert result.status == "retrying"
    assert (result.next_run_at - before).total_seconds() >= 10.5
