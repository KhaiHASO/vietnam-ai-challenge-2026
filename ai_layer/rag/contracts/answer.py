from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .events import ConfidenceBand, ModelSignal
from .memory import Citation


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    ABSTAINED = "abstained"
    APPROVAL_REQUIRED = "approval_required"
    ERROR = "error"


class AbstentionCode(StrEnum):
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    POLICY_BLOCKED = "POLICY_BLOCKED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class RecoveryAction(StrEnum):
    REFINE_QUESTION = "refine_question"
    UPLOAD_DOCUMENT = "upload_document"
    ASK_EXPERT = "ask_expert"


class SafetyStatus(StrEnum):
    SAFE = "safe"
    REDACTED = "redacted"
    BLOCKED = "blocked"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required: bool
    approval_id: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    action_type: str | None = None


class Abstention(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: AbstentionCode
    user_message: str = Field(min_length=1, max_length=500)
    attempted_sources: int = Field(default=0, ge=0)
    recovery_actions: list[RecoveryAction] = Field(default_factory=list, max_length=3)
    expert_handoff_available: bool = False


class VersionSet(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    domain_pack: str
    knowledge_index: str
    prompt: str
    policy: str
    provider_model: str
    validator_bundle: str


class CopilotAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    status: AnswerStatus
    answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    confidence_band: ConfidenceBand = ConfidenceBand.LOW
    safety_status: SafetyStatus = SafetyStatus.SAFE
    suggested_actions: list[str] = Field(default_factory=list, max_length=3)
    approval: Approval | None = None
    abstention: Abstention | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    versions: VersionSet | None = None
    model_signals: list[ModelSignal] = Field(default_factory=list)

    validators_passed: bool = Field(default=False, exclude=True)

    @model_validator(mode="after")
    def validate_answer_invariants(self) -> "CopilotAnswer":
        if self.status == AnswerStatus.ABSTAINED:
            if self.answer is not None:
                raise ValueError("Abstained answers must not contain answer text")
            if self.abstention is None:
                raise ValueError("Abstained answers must provide an abstention object")
            if self.citations:
                raise ValueError("Abstained answers cannot expose citations as conclusions")
        elif self.status == AnswerStatus.ANSWERED:
            if not self.answer or not self.answer.strip():
                raise ValueError("Answered status requires answer text")
            if self.abstention is not None:
                raise ValueError("Answered status cannot include abstention")
        elif self.status == AnswerStatus.APPROVAL_REQUIRED:
            if self.approval is None or not self.approval.required:
                raise ValueError("Approval-required status needs a required approval")
        return self
