import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ai_layer.rag.contracts.memory import Evidence
from ai_layer.rag.contracts.request import CopilotRequest

from .pipeline import AssuranceAction, ValidationResult


class EvidencePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    active_index_revision: str | None = None
    minimum_score: float = Field(default=0.6, ge=0, le=1)
    minimum_source_diversity: int = Field(default=1, gt=0)
    maximum_age_days: int | None = Field(default=None, gt=0)


class EvidenceValidator:
    def validate(
        self,
        request: CopilotRequest,
        evidence: list[Evidence],
        memory_facts: list[Any] | None = None,
        policy: EvidencePolicy | None = None,
    ) -> ValidationResult:
        del memory_facts
        policy = policy or EvidencePolicy()
        if not evidence:
            return self._failure("INSUFFICIENT_EVIDENCE", "No evidence retrieved")

        now = datetime.now(timezone.utc)
        for chunk in evidence:
            if chunk.tenant_id != request.tenant_id or chunk.domain_id != request.domain_id:
                return self._failure(
                    "EVIDENCE_SCOPE_MISMATCH",
                    "Evidence is outside the request tenant or domain",
                )
            if (
                policy.active_index_revision is not None
                and chunk.index_revision != policy.active_index_revision
            ):
                return self._failure(
                    "STALE_INDEX_REVISION", "Evidence is not from the active index"
                )
            if chunk.document_status != "active":
                return self._failure(
                    "INACTIVE_EVIDENCE", "Evidence document is not active"
                )
            expected_checksum = hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()
            if chunk.checksum != expected_checksum:
                return self._failure(
                    "INVALID_EVIDENCE_CHECKSUM", "Evidence checksum does not match content"
                )
            if chunk.score < policy.minimum_score:
                return self._failure("WEAK_EVIDENCE", "Evidence score is below policy")
            if chunk.expires_at is not None and chunk.expires_at <= now:
                return self._failure("STALE_EVIDENCE", "Evidence has expired")
            if (
                policy.maximum_age_days is not None
                and chunk.published_at is not None
                and chunk.published_at
                < now - timedelta(days=policy.maximum_age_days)
            ):
                return self._failure("STALE_EVIDENCE", "Evidence is outside freshness policy")
            if chunk.contradiction:
                return self._failure(
                    "CONFLICTING_EVIDENCE", "Evidence contains a contradiction signal"
                )

        distinct_sources = {(chunk.document_id, chunk.source_uri) for chunk in evidence}
        if len(distinct_sources) < policy.minimum_source_diversity:
            return self._failure(
                "INSUFFICIENT_SOURCE_DIVERSITY",
                "Evidence does not meet source diversity policy",
            )
        return ValidationResult(
            passed=True,
            code="OK",
            message="Evidence valid",
            metadata={
                "source_count": len(distinct_sources),
                "chunk_count": len(evidence),
            },
        )

    @staticmethod
    def _failure(code: str, message: str) -> ValidationResult:
        return ValidationResult(
            passed=False,
            code=code,
            message=message,
            action=AssuranceAction.RETRIEVAL_REWRITE,
            retryable=True,
        )
