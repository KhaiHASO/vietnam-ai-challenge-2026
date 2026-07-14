from enum import StrEnum
from typing import Any, Protocol
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from ai_layer.rag.contracts.answer import (
    Abstention,
    AbstentionCode,
    AnswerStatus,
    Approval,
    CopilotAnswer,
    RecoveryAction,
)
from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.contracts.request import CopilotRequest


class AssuranceAction(StrEnum):
    PASS = "pass"
    RETRIEVAL_REWRITE = "retrieval_rewrite"
    REPAIR = "repair"
    APPROVAL = "approval"
    ABSTAIN = "abstain"


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    code: str
    message: str
    action: AssuranceAction = AssuranceAction.PASS
    retryable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssuranceOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: AssuranceAction
    result: ValidationResult
    answer: CopilotAnswer | None = None


class OptionalGrader(Protocol):
    def validate(
        self,
        *,
        request: CopilotRequest,
        evidence: list[Evidence],
        answer: CopilotAnswer,
    ) -> ValidationResult: ...


class AssurancePipeline:
    def __init__(
        self,
        input_val,
        evidence_val,
        citation_val,
        *,
        tier1_grader: OptionalGrader | None = None,
        tier2_grader: OptionalGrader | None = None,
    ) -> None:
        self.input_val = input_val
        self.evidence_val = evidence_val
        self.citation_val = citation_val
        self.tier1_grader = tier1_grader
        self.tier2_grader = tier2_grader

    def run(
        self,
        *,
        request: CopilotRequest,
        evidence: list[Evidence],
        answer: CopilotAnswer | None = None,
        memory_facts: list[Any] | None = None,
        evidence_policy=None,
        retrieval_attempt: int = 0,
        max_retrieval_attempts: int = 1,
        repair_attempt: int = 0,
        max_repair_attempts: int = 1,
        ambiguous: bool = False,
        high_risk: bool = False,
        action_requires_approval: bool = False,
    ) -> AssuranceOutcome:
        input_result = self.input_val.validate(request)
        if not input_result.passed:
            return self._abstain(
                request,
                input_result,
                AbstentionCode.POLICY_BLOCKED,
                attempted_sources=0,
            )

        evidence_result = self.evidence_val.validate(
            request=request,
            evidence=evidence,
            memory_facts=memory_facts,
            policy=evidence_policy,
        )
        if not evidence_result.passed:
            if evidence_result.code == "CONFLICTING_EVIDENCE":
                return self._abstain(
                    request,
                    evidence_result,
                    AbstentionCode.CONFLICTING_EVIDENCE,
                    attempted_sources=len(evidence),
                )
            if evidence_result.code == "EVIDENCE_SCOPE_MISMATCH":
                return self._abstain(
                    request,
                    evidence_result,
                    AbstentionCode.POLICY_BLOCKED,
                    attempted_sources=len(evidence),
                )
            if retrieval_attempt < max_retrieval_attempts:
                retry = evidence_result.model_copy(
                    update={
                        "action": AssuranceAction.RETRIEVAL_REWRITE,
                        "retryable": True,
                    }
                )
                return AssuranceOutcome(
                    action=AssuranceAction.RETRIEVAL_REWRITE, result=retry
                )
            return self._abstain(
                request,
                evidence_result,
                AbstentionCode.INSUFFICIENT_EVIDENCE,
                attempted_sources=len(evidence),
            )

        if answer is None:
            return AssuranceOutcome(
                action=AssuranceAction.PASS,
                result=evidence_result,
            )

        citation_result = self.citation_val.validate(
            answer,
            evidence,
            tenant_id=request.tenant_id,
            domain_id=request.domain_id,
            active_index_revision=getattr(evidence_policy, "active_index_revision", None),
        )
        if not citation_result.passed:
            return self._repair_or_abstain(
                request,
                citation_result,
                repair_attempt,
                max_repair_attempts,
                attempted_sources=len(evidence),
            )

        grader = self.tier2_grader if high_risk else self.tier1_grader if ambiguous else None
        if grader is not None:
            graded = grader.validate(request=request, evidence=evidence, answer=answer)
            if not graded.passed:
                return self._repair_or_abstain(
                    request,
                    graded,
                    repair_attempt,
                    max_repair_attempts,
                    attempted_sources=len(evidence),
                )

        if action_requires_approval or high_risk:
            approval_answer = CopilotAnswer.model_validate(
                {
                    **answer.model_dump(),
                    "status": AnswerStatus.APPROVAL_REQUIRED,
                    "approval": Approval(
                        required=True,
                        approval_id=str(uuid4()),
                        action_type="high_risk_recommendation",
                    ),
                }
            )
            return AssuranceOutcome(
                action=AssuranceAction.APPROVAL,
                result=ValidationResult(
                    passed=True,
                    code="APPROVAL_REQUIRED",
                    message="High-risk action requires human approval",
                    action=AssuranceAction.APPROVAL,
                ),
                answer=approval_answer,
            )

        answer.validators_passed = True
        return AssuranceOutcome(
            action=AssuranceAction.PASS,
            result=ValidationResult(
                passed=True,
                code="OK",
                message="All assurance gates passed",
            ),
            answer=answer,
        )

    def _repair_or_abstain(
        self,
        request: CopilotRequest,
        result: ValidationResult,
        repair_attempt: int,
        max_repair_attempts: int,
        *,
        attempted_sources: int,
    ) -> AssuranceOutcome:
        if repair_attempt < max_repair_attempts:
            retry = result.model_copy(
                update={"action": AssuranceAction.REPAIR, "retryable": True}
            )
            return AssuranceOutcome(action=AssuranceAction.REPAIR, result=retry)
        return self._abstain(
            request,
            result,
            AbstentionCode.VALIDATION_FAILED,
            attempted_sources=attempted_sources,
        )

    @staticmethod
    def _abstain(
        request: CopilotRequest,
        result: ValidationResult,
        code: AbstentionCode,
        *,
        attempted_sources: int,
    ) -> AssuranceOutcome:
        user_messages = {
            AbstentionCode.INSUFFICIENT_EVIDENCE: "Tôi chưa có đủ nguồn đáng tin cậy để kết luận.",
            AbstentionCode.CONFLICTING_EVIDENCE: "Các nguồn hiện có đang mâu thuẫn nên tôi chưa thể kết luận.",
            AbstentionCode.POLICY_BLOCKED: "Yêu cầu này không thể được xử lý theo chính sách an toàn hiện tại.",
            AbstentionCode.VALIDATION_FAILED: "Câu trả lời chưa vượt qua bước kiểm chứng nguồn.",
        }
        abstention = Abstention(
            code=code,
            user_message=user_messages.get(
                code, "Tôi chưa thể đưa ra kết luận đáng tin cậy lúc này."
            ),
            attempted_sources=attempted_sources,
            recovery_actions=[
                RecoveryAction.REFINE_QUESTION,
                RecoveryAction.UPLOAD_DOCUMENT,
                RecoveryAction.ASK_EXPERT,
            ],
            expert_handoff_available=True,
        )
        abstained_answer = CopilotAnswer(
            status=AnswerStatus.ABSTAINED,
            abstention=abstention,
            trace_id=request.idempotency_key,
        )
        return AssuranceOutcome(
            action=AssuranceAction.ABSTAIN,
            result=result.model_copy(
                update={"action": AssuranceAction.ABSTAIN, "retryable": False}
            ),
            answer=abstained_answer,
        )
