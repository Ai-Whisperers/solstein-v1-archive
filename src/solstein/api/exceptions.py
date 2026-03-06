"""Standardized error handling for SolStein API with secure responses.

Provides:
- APIError: Custom exception with code, message, status_code
- Global exception handlers for consistent JSON error responses
- Secure error responses (no traceback exposure in production)
- Structured error format: {"error": {"code": "...", "message": "...", "details": ...}}

Security:
- Stack traces only returned when DEBUG_ERRORS=true AND environment != production
- Internal details filtered from error responses
- Full error details always logged server-side
"""

import sys
import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from solstein.config import get_settings
from solstein.exceptions import SolsteinError


class APIError(StarletteHTTPException):
    """Custom API exception with structured error code and message.

    Attributes:
        code: Machine-readable error code (e.g. "NOT_FOUND", "VALIDATION_ERROR")
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
            status_code: HTTP status code
            details: Optional additional error details
        """
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers for the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
        """Handle custom APIError exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.to_dict()},
        )

    @app.exception_handler(SolsteinError)
    async def handle_solstein_error(request: Request, exc: SolsteinError) -> JSONResponse:
        """Handle SolsteinError domain exceptions."""
        settings = get_settings()
        error_response = {
            "error": {
                "code": exc.code if hasattr(exc, "code") else "DOMAIN_ERROR",
                "message": str(exc),
                "details": exc.details if hasattr(exc, "details") else None,
            }
        }

        # Only include stack trace in debug mode and non-production
        if settings.debug and settings.environment != "production":
            error_response["error"]["stack_trace"] = traceback.format_exc()

        return JSONResponse(
            status_code=exc.status_code if hasattr(exc, "status_code") else 500,
            content=error_response,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle FastAPI request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions securely."""
        settings = get_settings()

        # Log full error details server-side
        logger.error(f"Unhandled exception: {exc}")
        logger.error(traceback.format_exc())

        # Return safe error response
        error_response: dict[str, Any] = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        }

        # Only include debug info in development
        if settings.debug and settings.environment != "production":
            error_response["error"]["debug"] = {
                "type": type(exc).__name__,
                "message": str(exc),
                "stack_trace": traceback.format_exc(),
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )
