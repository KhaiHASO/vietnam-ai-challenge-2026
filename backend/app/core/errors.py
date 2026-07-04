import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("backend.errors")


def _status_phrase(status_code: int) -> str:
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return "Error"


def _safe_detail(detail: Any, status_code: int) -> str:
    if status_code >= 500:
        return "Internal server error"
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail")
        if isinstance(message, str):
            return message
    return _status_phrase(status_code)


def error_payload(status_code: int, code: str, message: str) -> dict[str, Any]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        message = _safe_detail(exc.detail, exc.status_code)
        code = f"HTTP_{exc.status_code}"
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.status_code, code, message),
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
