from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConfidenceBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelSignal(BaseModel):
    """A model decision signal. It is never evidence and cannot be cited."""

    model_config = ConfigDict(extra="forbid")

    risk_level: RiskLevel
    priority: float = Field(ge=0, le=1)
    requires_review: bool
    confidence: float = Field(ge=0, le=1)
    model_version: str
    latency_ms: float = Field(ge=0)
    engine_status: str


class CopilotEventType(StrEnum):
    MESSAGE_STARTED = "message.started"
    ROUTE_SELECTED = "route.selected"
    MEMORY_LOADED = "memory.loaded"
    RETRIEVAL_COMPLETED = "retrieval.completed"
    TOKEN_DELTA = "token.delta"
    CITATION_ADDED = "citation.added"
    APPROVAL_REQUIRED = "approval.required"
    MESSAGE_ABSTAINED = "message.abstained"
    MESSAGE_COMPLETED = "message.completed"
    ERROR = "error"


class CopilotEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    sequence: int = Field(ge=0)
    session_id: str
    message_id: str
    occurred_at: datetime
    trace_id: str
    event_type: CopilotEventType
    payload: dict[str, Any]
