"""Standardized error response schemas for EPIC-024 Story 4.

Provides consistent error format across all API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Standard API error codes."""

    # Client errors (4xx)
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNPROCESSABLE_ENTITY = "UNPROCESSABLE_ENTITY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"

    # Domain-specific errors
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"
    INVALID_COMPANY_ID = "INVALID_COMPANY_ID"
    ENRICHMENT_FAILED = "ENRICHMENT_FAILED"
    SCORING_ERROR = "SCORING_ERROR"
    EXPORT_ERROR = "EXPORT_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error context")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 timestamp"
    )
    request_id: str | None = Field(None, description="Unique request identifier for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "COMPANY_NOT_FOUND",
                "message": "Company with ID 'eneve' not found",
                "details": {"company_id": "eneve", "suggestion": "Try searching by name"},
                "timestamp": "2026-03-06T12:00:00Z",
                "request_id": "req_abc123",
            }
        }


class ErrorResponse(BaseModel):
    """Standard API error response."""

    error: ErrorDetail

    @classmethod
    def create(
        cls, code: ErrorCode, message: str, details: dict[str, Any] | None = None, request_id: str | None = None
    ) -> ErrorResponse:
        """Create standardized error response."""
        return cls(error=ErrorDetail(code=code, message=message, details=details or {}, request_id=request_id))


# Common error responses for OpenAPI documentation
ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid request parameters",
                        "details": {"field": "company_id", "issue": "required"},
                        "timestamp": "2026-03-06T12:00:00Z",
                    }
                }
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Invalid or missing API key",
                        "timestamp": "2026-03-06T12:00:00Z",
                    }
                }
            }
        },
    },
    404: {
        "description": "Not Found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "COMPANY_NOT_FOUND",
                        "message": "Company not found",
                        "details": {"company_id": "xyz"},
                        "timestamp": "2026-03-06T12:00:00Z",
                    }
                }
            }
        },
    },
    429: {
        "description": "Rate Limit Exceeded",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests",
                        "details": {"retry_after": 60},
                        "timestamp": "2026-03-06T12:00:00Z",
                    }
                }
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "timestamp": "2026-03-06T12:00:00Z",
                    }
                }
            }
        },
    },
}


__all__ = ["ErrorCode", "ErrorDetail", "ErrorResponse", "ERROR_RESPONSES"]
