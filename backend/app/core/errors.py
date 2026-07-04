import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("backend.errors")

SENSITIVE_DETAIL_KEYS = {
    "exception",
    "password",
    "secret",
    "stack",
    "stack_trace",
    "token",
    "trace",
    "traceback",
}

PUBLIC_SERVER_ERROR_PREFIXES = ("MONGO_", "UPLOAD_")


def _status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


def _public_details(detail: Any) -> dict[str, Any] | None:
    if not isinstance(detail, dict):
        return None

    details = {
        key: value
        for key, value in detail.items()
        if key not in {"code", "detail", "message"}
        and key.lower() not in SENSITIVE_DETAIL_KEYS
    }
    return details or None


def _safe_error_fields(detail: Any, status_code: int) -> tuple[str, str | None, dict[str, Any] | None]:
    if status_code >= 500:
        if isinstance(detail, dict) and isinstance(detail.get("message"), str):
            code = detail.get("code") if isinstance(detail.get("code"), str) else None
            if not code or not code.startswith(PUBLIC_SERVER_ERROR_PREFIXES):
                return "Internal server error", None, None
            return detail["message"], code, _public_details(detail)
        return "Internal server error", None, None
    if isinstance(detail, str):
        return detail, None, None
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail")
        if isinstance(message, str):
            code = detail.get("code") if isinstance(detail.get("code"), str) else None
            return message, code, _public_details(detail)
    return _status_phrase(status_code), None, None


def error_payload(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
        },
    }
    if details:
        payload["error"]["details"] = details
    return payload


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        message, detail_code, details = _safe_error_fields(exc.detail, exc.status_code)
        code = detail_code or f"HTTP_{exc.status_code}"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.status_code, code, message, details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        fields = []
        for error in exc.errors():
            fields.append(
                {
                    "field": ".".join(str(part) for part in error.get("loc", [])),
                    "message": error.get("msg", "Invalid value"),
                }
            )

        payload = error_payload(422, "VALIDATION_ERROR", "Invalid request")
        payload["error"]["fields"] = fields
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled backend error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=error_payload(500, "INTERNAL_SERVER_ERROR", "Internal server error"),
        )
