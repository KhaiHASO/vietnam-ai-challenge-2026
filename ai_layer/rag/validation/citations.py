import re
from typing import Iterable

from ai_layer.rag.contracts.answer import AnswerStatus, CopilotAnswer
from ai_layer.rag.contracts.memory import Citation, Evidence

from .pipeline import AssuranceAction, ValidationResult


_WORD = re.compile(r"\w+", re.UNICODE)
_STOP_WORDS = {
    "các", "có", "cho", "của", "được", "gây", "là", "một", "những",
    "the", "and", "for", "this", "that", "with",
}


class CitationValidator:
    def __init__(self, *, minimum_claim_coverage: float = 0.8) -> None:
        self.minimum_claim_coverage = minimum_claim_coverage

    def validate(
        self,
        answer: CopilotAnswer,
        evidence: list[Evidence],
        tenant_id: str,
        domain_id: str,
        active_index_revision: str | None = None,
    ) -> ValidationResult:
        if answer.status not in {
            AnswerStatus.ANSWERED,
            AnswerStatus.APPROVAL_REQUIRED,
        }:
            return ValidationResult(passed=True, code="OK", message="No factual answer")

        evidence_by_chunk = {chunk.chunk_id: chunk for chunk in evidence}
        seen_chunks: set[str] = set()
        for citation in answer.citations:
            chunk = evidence_by_chunk.get(citation.chunk_id)
            if chunk is None:
                return self._failure("UNKNOWN_CITATION", "Citation is not in retrieval set")
            if chunk.tenant_id != tenant_id:
                return self._failure(
                    "CROSS_TENANT_CITATION", "Citation references foreign tenant data"
                )
            if chunk.domain_id != domain_id:
                return self._failure(
                    "CROSS_DOMAIN_CITATION", "Citation references another domain"
                )
            if active_index_revision and chunk.index_revision != active_index_revision:
                return self._failure(
                    "STALE_CITATION", "Citation references an inactive index revision"
                )
            if citation.chunk_id in seen_chunks:
                return self._failure("DUPLICATE_CITATION", "Citation chunk is duplicated")
            seen_chunks.add(citation.chunk_id)
            if citation.inline_reference not in (answer.answer or ""):
                return self._failure(
                    "MISSING_INLINE_REFERENCE", "Citation marker is absent from the answer"
                )
            if not self._span_matches(citation, chunk):
                return self._failure(
                    "INVALID_CITATION_SPAN", "Citation span does not map to source content"
                )

        claims = self._claims(answer.answer or "")
        if claims and not answer.citations:
            return self._failure(
                "UNCITED_FACTUAL_CLAIM", "Factual answer does not contain citations"
            )
        supported_claims = 0
        for claim in claims:
            citations = [
                citation
                for citation in answer.citations
                if citation.inline_reference in claim
            ]
            if not citations:
                continue
            if any(
                self._claim_supported(claim, evidence_by_chunk[citation.chunk_id])
                for citation in citations
            ):
                supported_claims += 1
            else:
                return self._failure(
                    "UNSUPPORTED_CLAIM", "Citation does not support the associated claim"
                )
        coverage = supported_claims / len(claims) if claims else 1.0
        if coverage < self.minimum_claim_coverage:
            return self._failure(
                "INSUFFICIENT_CITATION_COVERAGE",
                "Factual claim coverage is below policy",
            )
        return ValidationResult(
            passed=True,
            code="OK",
            message="Citations valid",
            metadata={"claim_coverage": coverage, "claim_count": len(claims)},
        )

    @staticmethod
    def _claims(answer: str) -> list[str]:
        return [
            claim.strip()
            for claim in re.split(r"(?<=[.!?])\s+|\n+", answer)
            if any(character.isalpha() for character in claim)
        ]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token.casefold()
            for token in _WORD.findall(text)
            if len(token) > 2 and token.casefold() not in _STOP_WORDS
        }

    def _claim_supported(self, claim: str, evidence: Evidence) -> bool:
        claim_without_refs = re.sub(r"\[\d+\]", "", claim)
        claim_tokens = self._tokens(claim_without_refs)
        evidence_tokens = self._tokens(evidence.content)
        if not claim_tokens:
            return True
        overlap = len(claim_tokens & evidence_tokens) / len(claim_tokens)
        return overlap >= 0.3

    @staticmethod
    def _span_matches(citation: Citation, evidence: Evidence) -> bool:
        if citation.start_char is not None and citation.end_char is not None:
            span = evidence.content[citation.start_char : citation.end_char]
            if citation.quoted_text is not None and span != citation.quoted_text:
                return False
        if citation.quoted_text is not None and citation.quoted_text not in evidence.content:
            return False
        return True

    @staticmethod
    def _failure(code: str, message: str) -> ValidationResult:
        return ValidationResult(
            passed=False,
            code=code,
            message=message,
            action=AssuranceAction.REPAIR,
            retryable=True,
        )
