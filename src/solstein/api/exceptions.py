"""Standardized error handling for Solstein API with opaque responses.

STORY-069: Migrate Error Handling to Supabase-Compatible Patterns

Provides:
- APIError: Custom exception with code, message, status_code
- Global exception handlers for consistent JSON error responses
- Opaque error responses with error_id for correlation (no tracebacks ever)
- Structured error format: {"error": {"code": "...", "message": "...", "error_id": "uuid"}}

Security (REQ-1, REQ-2):
- Tracebacks NEVER included in HTTP responses, regardless of environment
- Full tracebacks logged server-side with error_id for correlation
- Internal details (file paths, variable names) filtered from all responses
"""

import traceback
import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from solstein.exceptions import SolsteinError


def _generate_error_id() -> str:
    """Generate a unique error ID for log correlation."""
    return str(uuid.uuid4())


class APIError(StarletteHTTPException):
    """Custom API exception with structured error code and message.

    Attributes:
        code: Machine-readable error code (e.g. "NOT_FOUND", "VALIDATION_ERROR")
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details (must not contain internals)
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
            status_code: HTTP status code
            details: Optional additional error details
        """
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details


async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
    """Handle custom APIError exceptions with opaque response."""
    error_id = _generate_error_id()
    logger.warning(
        f"[{error_id}] APIError on {request.url.path}: code={exc.code} status={exc.status_code} message={exc.message}"
    )
    response: dict[str, Any] = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "error_id": error_id,
        }
    }
    if exc.details is not None:
        response["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=response)


async def handle_solstein_error(request: Request, exc: SolsteinError) -> JSONResponse:
    """Handle SolsteinError domain exceptions with opaque response."""
    error_id = _generate_error_id()
    error_code = exc.code if hasattr(exc, "code") else "DOMAIN_ERROR"
    http_status = exc.status_code if hasattr(exc, "status_code") else 500

    # REQ-2: Log full traceback server-side with error_id
    logger.error(
        f"[{error_id}] SolsteinError on {request.url.path}: "
        f"code={error_code} status={http_status}\n{traceback.format_exc()}"
    )

    # REQ-1: Opaque response — no traceback, no file paths
    return JSONResponse(
        status_code=http_status,
        content={
            "error": {
                "code": error_code,
                "message": str(exc),
                "error_id": error_id,
            }
        },
    )


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI request validation errors with sanitized details."""
    error_id = _generate_error_id()
    logger.warning(f"[{error_id}] Validation error on {request.url.path}: {exc.errors()}")

    # Sanitize validation error details — remove 'url' and 'input' fields
    safe_errors = []
    for err in exc.errors():
        safe_errors.append(
            {
                "type": err.get("type", "unknown"),
                "loc": err.get("loc", []),
                "msg": err.get("msg", "Validation failed"),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "error_id": error_id,
                "details": safe_errors,
            }
        },
    )


async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions securely.

    REQ-1: Response contains ONLY error_id and generic message.
    REQ-2: Full traceback logged server-side with error_id.
    """
    error_id = _generate_error_id()

    # Log full error details server-side for debugging
    logger.error(f"[{error_id}] Unhandled {type(exc).__name__} on {request.url.path}: {exc}\n{traceback.format_exc()}")

    # Opaque response — never expose internals
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "error_id": error_id,
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers for the FastAPI application.

    All handlers produce opaque responses with an error_id for log correlation.
    Tracebacks are NEVER included in HTTP responses (REQ-1).

    Args:
        app: FastAPI application instance
    """
    app.exception_handler(APIError)(handle_api_error)
    app.exception_handler(SolsteinError)(handle_solstein_error)
    app.exception_handler(RequestValidationError)(handle_validation_error)
    app.exception_handler(Exception)(handle_generic_exception)
