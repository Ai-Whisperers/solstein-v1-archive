"""Standardized exception taxonomy for Solstein.

This module defines a minimal, consistent exception hierarchy
that maps cleanly to HTTP status codes and provides structured
error information for logging and API responses.

Usage:
    # Raise with just message
    raise NotFoundError("Company not found")

    # Raise with additional context
    raise ValidationError(
        "Invalid revenue value",
        details={"field": "revenue", "value": -100, "constraint": "must be positive"}
    )

    # Catch and convert to HTTP response
    try:
        process_data(data)
    except SolsteinError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.to_dict()}
        )
"""

from typing import Any


class SolsteinError(Exception):
    """Base exception for all Solstein errors.

    Provides structured error information for:
    - Machine-readable error codes
    - HTTP status code mapping
    - Structured details for debugging
    - Conversion to API response format

    Attributes:
        code: Machine-readable error code (e.g., "NOT_FOUND")
        message: Human-readable error description
        status_code: HTTP status code (e.g., 404)
        details: Optional structured error context
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or {}

    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.details:
            base += f" | details={self.details}"
        return base

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(code='{self.code}', message='{self.message}', status_code={self.status_code})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result

    def with_details(self, **kwargs) -> "SolsteinError":
        """Return new exception with additional details."""
        new_details = {**self.details, **kwargs}
        return self.__class__(
            self.message,
            code=self.code,
            status_code=self.status_code,
            details=new_details,
        )


# ===== Domain Errors (4xx client errors) =====


class DomainError(SolsteinError):
    """Business logic violation.

    Use when: Input violates business rules (not just format).
    Example: Cannot classify company with insufficient data.
    HTTP: 400 Bad Request
    """

    code = "DOMAIN_ERROR"
    status_code = 400


class ValidationError(DomainError):
    """Input validation failure.

    Use when: Input format, type, or constraint violation.
    Example: Negative revenue, invalid date format.
    HTTP: 400 Bad Request
    """

    code = "VALIDATION_ERROR"
    status_code = 400


class NotFoundError(SolsteinError):
    """Resource not found.

    Use when: Requested resource doesn't exist.
    Example: Company ID not in database.
    HTTP: 404 Not Found
    """

    code = "NOT_FOUND"
    status_code = 404

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        *,
        details: dict[str, Any] | None = None,
    ):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, details=details)
        self.details["resource_type"] = resource_type
        self.details["resource_id"] = resource_id


class StateError(SolsteinError):
    """Invalid state for operation.

    Use when: Operation not allowed in current state.
    Example: Cannot transition from COMPLETED to PENDING.
    HTTP: 409 Conflict
    """

    code = "STATE_ERROR"
    status_code = 409


class ConflictError(SolsteinError):
    """Resource conflict.

    Use when: Resource already exists or conflicts with another.
    Example: Duplicate company ID, concurrent modification.
    HTTP: 409 Conflict
    """

    code = "CONFLICT"
    status_code = 409


class PermissionError(SolsteinError):
    """Permission denied.

    Use when: User lacks permission for action.
    Example: Cannot access another tenant's data.
    HTTP: 403 Forbidden
    """

    code = "PERMISSION_DENIED"
    status_code = 403


class AuthenticationError(SolsteinError):
    """Authentication failure.

    Use when: Invalid or missing credentials.
    Example: Invalid API key, expired token.
    HTTP: 401 Unauthorized
    """

    code = "AUTHENTICATION_FAILED"
    status_code = 401


class RateLimitError(SolsteinError):
    """Rate limit exceeded.

    Use when: Too many requests from client.
    HTTP: 429 Too Many Requests
    """

    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if retry_after:
            self.details["retry_after"] = retry_after


# ===== Infrastructure Errors (5xx server errors) =====


class InfrastructureError(SolsteinError):
    """Internal infrastructure failure.

    Use when: Service cannot fulfill request due to internal issue.
    Example: Database unavailable, service timeout.
    HTTP: 500 Internal Server Error
    """

    code = "INFRASTRUCTURE_ERROR"
    status_code = 500


class DatabaseError(InfrastructureError):
    """Database operation failure.

    Use when: Database query/connection fails.
    HTTP: 500 Internal Server Error
    """

    code = "DATABASE_ERROR"
    status_code = 500


class LLMError(InfrastructureError):
    """LLM provider failure.

    Use when: LLM call fails or returns invalid response.
    HTTP: 502 Bad Gateway (external service failure)
    """

    code = "LLM_ERROR"
    status_code = 502

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if provider:
            self.details["provider"] = provider
        if model:
            self.details["model"] = model


class ExternalServiceError(InfrastructureError):
    """External service failure.

    Use when: Third-party API call fails.
    HTTP: 502 Bad Gateway
    """

    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502

    def __init__(
        self,
        message: str,
        *,
        service: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if service:
            self.details["service"] = service


class ConfigurationError(InfrastructureError):
    """Invalid configuration.

    Use when: Service configuration is invalid or missing.
    HTTP: 500 Internal Server Error
    """

    code = "CONFIGURATION_ERROR"
    status_code = 500


# Backwards compatibility aliases
DataLoadError = InfrastructureError
ScoringError = DomainError
ExportError = InfrastructureError
SyntheticDataBlockingError = DomainError
LLMAvailabilityError = LLMError
