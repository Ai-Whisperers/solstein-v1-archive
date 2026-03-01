"""
Standardized error handling for SolStein API.

Provides:
- APIError: Custom exception with code, message, status_code
- Global exception handlers for consistent JSON error responses
- Structured error format: {"error": {"code": "...", "message": "...", "details": ...}}
"""

import sys
import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


class APIError(StarletteHTTPException):
    """Custom API exception with structured error code and message.

    Attributes:
        code: Machine-readable error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Any = None,
    ) -> None:
        """Initialize APIError.

        Args:
            code: Machine-readable error code
            message: Human-readable error message
            status_code: HTTP status code (default: 500)
            details: Optional additional error details
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


def setup_exception_handlers(app: FastAPI) -> None:
    """Register robust, structured global exception handlers.

    Handles:
    - APIError: Custom API exceptions with structured codes
    - RequestValidationError: Pydantic validation errors (422)
    - StarletteHTTPException: Standard HTTP exceptions (404, 401, etc.)
    - Exception: Catch-all for unhandled server errors (500)
    """

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """Handle custom APIError exceptions with structured response."""
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Log based on status code
        if exc.status_code >= 500:
            logger.error(
                f"API Error [{exc.status_code}] | {request.method} {request.url.path} | "
                f"Code: {exc.code} | Message: {exc.message}",
                extra={"request_id": request_id},
            )
        else:
            logger.warning(
                f"API Error [{exc.status_code}] | {request.method} {request.url.path} | "
                f"Code: {exc.code} | Message: {exc.message}",
                extra={"request_id": request_id},
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic validation errors (422)."""
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Format validation errors clearly
        errors = exc.errors()
        modified_details = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in errors]

        logger.warning(
            f"Validation Error [422] | {request.method} {request.url.path} | Details: {modified_details}",
            extra={"request_id": request_id},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": modified_details,
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle standard HTTP exceptions (404, 401, etc.)."""
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Map status codes to error codes
        status_to_code = {
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_409_CONFLICT: "CONFLICT",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
            status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMITED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
            status.HTTP_501_NOT_IMPLEMENTED: "NOT_IMPLEMENTED",
            status.HTTP_503_SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
        }

        error_code = status_to_code.get(exc.status_code, "HTTP_ERROR")

        logger.warning(
            f"HTTP Exception [{exc.status_code}] | {request.method} {request.url.path} | "
            f"Code: {error_code} | Detail: {exc.detail}",
            extra={"request_id": request_id},
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "details": None,
                },
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled server errors (500).

        Captures full traceback for debugging.
        """
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Capture standard traceback for professional debugging
        exc_info = sys.exc_info()
        tb = traceback.format_exception(*exc_info) if exc_info[0] else ["Unknown traceback"]

        # Log with full context
        logger.exception(
            f"Unhandled Server Error [500] | {request.method} {request.url.path}",
            extra={"request_id": request_id},
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": str(exc),
                },
                "request_id": request_id,
                "traceback": tb,  # Exposed for QA/debugging in non-prod
            },
        )
