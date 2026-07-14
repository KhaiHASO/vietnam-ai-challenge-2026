from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryScope(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: str
    domain_id: str
    session_id: str
    user_id: str
    conversation_revision: int = Field(ge=0)


class Turn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    role: Literal["user", "assistant", "tool", "system"]
    content: str = Field(min_length=1)
    sequence: int = Field(default=0, ge=0)
    trace_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FactStatus(StrEnum):
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    FORGOTTEN = "forgotten"


class TrustLevel(StrEnum):
    UNTRUSTED = "untrusted"
    USER_ASSERTED = "user_asserted"
    USER_CONFIRMED = "user_confirmed"


class Fact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_id: str = Field(default_factory=lambda: str(uuid4()))
    key: str
    value: Any
    source_type: Literal["user_message"]
    source_message_id: str
    status: FactStatus = FactStatus.PENDING_CONFIRMATION
    trust_level: TrustLevel = TrustLevel.USER_ASSERTED
    consent: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    supersedes_fact_id: str | None = None


class FactProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: FactStatus
    fact: Fact | None = None
    reason: str | None = None


class MemoryContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conversation_revision: int
    facts: list[Fact]
    recent_turns: list[Turn]
    rolling_summary: str | None = None
