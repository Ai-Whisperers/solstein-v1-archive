"""Standardized error envelope for API and worker logs.

F3: Add standardized error envelope
Provides uniform error structure across API, workers, and logs.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from solstein.core.error_taxonomy import ErrorCategory, RetryPolicy, classify_error


class ErrorLevel(Enum):
    """Error severity levels for operational response."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error tracking."""

    request_id: str | None = None
    user_id: str | None = None
    company_id: str | None = None
    operation: str | None = None
    source: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            k: v
            for k, v in {
                "request_id": self.request_id,
                "user_id": self.user_id,
                "company_id": self.company_id,
                "operation": self.operation,
                "source": self.source,
                **self.extra,
            }.items()
            if v is not None
        }


@dataclass
class ErrorEnvelope:
    """Standardized error envelope for all error responses.

    F3: Uniform structure for API responses, worker logs, and error tracking.
    """

    # Core error information
    code: str
    message: str
    level: ErrorLevel = ErrorLevel.ERROR

    # Categorization
    category: ErrorCategory | None = None
    retryable: bool = False

    # Context
    context: ErrorContext = field(default_factory=ErrorContext)

    # Technical details
    details: dict[str, Any] = field(default_factory=dict)
    stack_trace: str | None = None
    cause: "ErrorEnvelope | None" = None

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"

    def __post_init__(self) -> None:
        """Auto-populate category and retryable from error code if not set."""
        if self.category is None:
            classification = classify_error(self.code)
            self.category = classification["category"]
            self.retryable = classification["retry"] != RetryPolicy.NEVER

    def to_dict(self, include_stack_trace: bool = False) -> dict[str, Any]:
        """Convert envelope to dictionary for serialization.

        Args:
            include_stack_trace: Whether to include stack trace in output

        Returns:
            Dictionary representation of the error
        """
        result: dict[str, Any] = {
            "error": {
                "code": self.code,
                "message": self.message,
                "level": self.level.value,
                "category": self.category.name if self.category else None,
                "retryable": self.retryable,
                "timestamp": self.timestamp.isoformat(),
                "version": self.version,
            },
            "context": self.context.to_dict(),
            "details": self.details,
        }

        if include_stack_trace and self.stack_trace:
            result["error"]["stack_trace"] = self.stack_trace

        if self.cause:
            result["error"]["cause"] = self.cause.to_dict(include_stack_trace)

        return result

    def to_log_dict(self) -> dict[str, Any]:
        """Convert to dictionary optimized for logging."""
        return {
            "error_code": self.code,
            "error_message": self.message,
            "error_level": self.level.value,
            "error_category": self.category.name if self.category else None,
            "error_retryable": self.retryable,
            "error_context": self.context.to_dict(),
            "error_details": self.details,
            "error_timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        code: str | None = None,
        message: str | None = None,
        context: ErrorContext | None = None,
        include_stack_trace: bool = True,
    ) -> "ErrorEnvelope":
        """Create an error envelope from an exception.

        Args:
            exc: The exception to wrap
            code: Error code (defaults to exception class name)
            message: Error message (defaults to str(exception))
            context: Error context
            include_stack_trace: Whether to capture stack trace

        Returns:
            ErrorEnvelope instance
        """
        error_code = code or type(exc).__name__
        error_message = message or str(exc) or "Unknown error"

        stack_trace = None
        if include_stack_trace:
            stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

        # Determine level from category
        classification = classify_error(error_code)
        level_map = {
            "DEBUG": ErrorLevel.DEBUG,
            "INFO": ErrorLevel.INFO,
            "WARNING": ErrorLevel.WARNING,
            "ERROR": ErrorLevel.ERROR,
            "CRITICAL": ErrorLevel.CRITICAL,
        }
        level = level_map.get(classification["severity"].name, ErrorLevel.ERROR)

        return cls(
            code=error_code,
            message=error_message,
            level=level,
            context=context or ErrorContext(),
            stack_trace=stack_trace,
        )

    @classmethod
    def validation_error(
        cls,
        message: str,
        field: str | None = None,
        value: Any = None,
        context: ErrorContext | None = None,
    ) -> "ErrorEnvelope":
        """Create a validation error envelope."""
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        return cls(
            code="VALIDATION_ERROR",
            message=message,
            level=ErrorLevel.WARNING,
            context=context or ErrorContext(),
            details=details,
        )

    @classmethod
    def not_found_error(
        cls,
        resource_type: str,
        resource_id: str,
        context: ErrorContext | None = None,
    ) -> "ErrorEnvelope":
        """Create a not found error envelope."""
        return cls(
            code="NOT_FOUND",
            message=f"{resource_type} not found: {resource_id}",
            level=ErrorLevel.INFO,
            context=context or ErrorContext(),
            details={"resource_type": resource_type, "resource_id": resource_id},
        )

    @classmethod
    def external_service_error(
        cls,
        service: str,
        message: str,
        context: ErrorContext | None = None,
    ) -> "ErrorEnvelope":
        """Create an external service error envelope."""
        return cls(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service} error: {message}",
            level=ErrorLevel.ERROR,
            context=context or ErrorContext(),
            details={"service": service},
        )


class ErrorEnvelopeBuilder:
    """Builder for constructing error envelopes fluently."""

    def __init__(self) -> None:
        self._code: str = "UNKNOWN_ERROR"
        self._message: str = "Unknown error"
        self._level: ErrorLevel = ErrorLevel.ERROR
        self._context: ErrorContext = ErrorContext()
        self._details: dict[str, Any] = {}
        self._stack_trace: str | None = None
        self._cause: ErrorEnvelope | None = None

    def code(self, code: str) -> "ErrorEnvelopeBuilder":
        """Set error code."""
        self._code = code
        return self

    def message(self, message: str) -> "ErrorEnvelopeBuilder":
        """Set error message."""
        self._message = message
        return self

    def level(self, level: ErrorLevel) -> "ErrorEnvelopeBuilder":
        """Set error level."""
        self._level = level
        return self

    def request_id(self, request_id: str) -> "ErrorEnvelopeBuilder":
        """Set request ID."""
        self._context.request_id = request_id
        return self

    def user_id(self, user_id: str) -> "ErrorEnvelopeBuilder":
        """Set user ID."""
        self._context.user_id = user_id
        return self

    def company_id(self, company_id: str) -> "ErrorEnvelopeBuilder":
        """Set company ID."""
        self._context.company_id = company_id
        return self

    def operation(self, operation: str) -> "ErrorEnvelopeBuilder":
        """Set operation name."""
        self._context.operation = operation
        return self

    def source(self, source: str) -> "ErrorEnvelopeBuilder":
        """Set error source."""
        self._context.source = source
        return self

    def detail(self, key: str, value: Any) -> "ErrorEnvelopeBuilder":
        """Add a detail field."""
        self._details[key] = value
        return self

    def details(self, **kwargs: Any) -> "ErrorEnvelopeBuilder":
        """Add multiple detail fields."""
        self._details.update(kwargs)
        return self

    def caused_by(self, cause: ErrorEnvelope) -> "ErrorEnvelopeBuilder":
        """Set the cause error."""
        self._cause = cause
        return self

    def with_stack_trace(self, exc: Exception) -> "ErrorEnvelopeBuilder":
        """Capture stack trace from exception."""
        self._stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        return self

    def build(self) -> ErrorEnvelope:
        """Build the error envelope."""
        return ErrorEnvelope(
            code=self._code,
            message=self._message,
            level=self._level,
            context=self._context,
            details=self._details,
            stack_trace=self._stack_trace,
            cause=self._cause,
        )


def create_error_response(
    code: str,
    message: str,
    status_code: int = 500,
    **details: Any,
) -> dict[str, Any]:
    """Create a standardized API error response.

    Args:
        code: Error code
        message: Human-readable error message
        status_code: HTTP status code
        **details: Additional error details

    Returns:
        Dictionary suitable for JSON response
    """
    envelope = ErrorEnvelope(
        code=code,
        message=message,
        details=details,
    )

    response = envelope.to_dict()
    response["status_code"] = status_code

    return response
