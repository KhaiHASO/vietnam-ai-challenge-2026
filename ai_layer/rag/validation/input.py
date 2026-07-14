import re
import unicodedata

from ai_layer.rag.contracts.request import CopilotRequest

from .pipeline import AssuranceAction, ValidationResult


class InputValidator:
    INJECTION_PATTERNS = (
        re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
        re.compile(r"reveal\s+(the\s+)?system\s+prompt", re.IGNORECASE),
        re.compile(r"bỏ\s+qua.+(hướng\s+dẫn|chỉ\s+dẫn)", re.IGNORECASE),
        re.compile(r"developer\s+message|chain[ -]of[ -]thought", re.IGNORECASE),
    )
    PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.-]*\d){9,10}(?!\d)")
    EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")

    def __init__(self, *, max_query_length: int = 1000) -> None:
        self.max_query_length = max_query_length

    def validate(self, request: CopilotRequest) -> ValidationResult:
        normalized = re.sub(
            r"\s+", " ", unicodedata.normalize("NFKC", request.query)
        ).strip()
        if len(normalized) > self.max_query_length:
            return ValidationResult(
                passed=False,
                code="QUERY_TOO_LONG",
                message=f"Query exceeds maximum length of {self.max_query_length}",
                action=AssuranceAction.ABSTAIN,
            )
        if any(pattern.search(normalized) for pattern in self.INJECTION_PATTERNS):
            return ValidationResult(
                passed=False,
                code="PROMPT_INJECTION",
                message="Prompt injection pattern detected",
                action=AssuranceAction.ABSTAIN,
                metadata={"normalized_query": normalized, "contains_pii": False},
            )
        contains_pii = bool(
            self.PHONE_PATTERN.search(normalized) or self.EMAIL_PATTERN.search(normalized)
        )
        return ValidationResult(
            passed=True,
            code="OK",
            message="Input valid",
            metadata={
                "normalized_query": normalized,
                "contains_pii": contains_pii,
            },
        )
