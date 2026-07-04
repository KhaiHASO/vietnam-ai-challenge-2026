import uuid
from datetime import datetime, timezone
from typing import Any

from app.repositories.diagnosis_repository import DiagnosisRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


class AgentLogService:
    def __init__(self, repository: DiagnosisRepository) -> None:
        self.repository = repository

    async def record(
        self,
        case_id: str,
        agent: str,
        status: str,
        trace: dict[str, Any],
        duration_ms: float,
    ) -> dict[str, Any]:
        now = _now()
        document = {
            "log_id": _new_id("log"),
            "case_id": case_id,
            "agent": agent,
            "status": status,
            "trace": trace,
            "duration_ms": duration_ms,
            "created_at": now,
            "updated_at": now,
        }
        return await self.repository.insert_one("agent_logs", document)
