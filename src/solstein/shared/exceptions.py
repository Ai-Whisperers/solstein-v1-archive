"""Base exception classes for all Solstein modules.

STORY-117: Shared exception hierarchy with zero application-layer imports.
All domain-specific exceptions should inherit from these base classes.
"""


class SolsteinError(Exception):
    """Base exception for all Solstein errors."""

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


class ConfigurationError(SolsteinError):
    """Invalid or missing configuration."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="CONFIGURATION_ERROR")


class ValidationError(SolsteinError):
    """Input validation failure."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="VALIDATION_ERROR")


class ExternalServiceError(SolsteinError):
    """External service call failure."""

    def __init__(
        self,
        message: str,
        *,
        service: str = "unknown",
        retryable: bool = True,
    ) -> None:
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR")
        self.service = service
        self.retryable = retryable


class DataIntegrityError(SolsteinError):
    """Data integrity violation."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="DATA_INTEGRITY_ERROR")


class NotFoundError(SolsteinError):
    """Resource not found."""

    def __init__(self, message: str, *, resource_type: str = "unknown") -> None:
        super().__init__(message, error_code="NOT_FOUND")
        self.resource_type = resource_type
