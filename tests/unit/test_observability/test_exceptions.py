"""Tests for the standardized exception taxonomy.

This module tests the new exception hierarchy that provides:
- Consistent HTTP status code mapping
- Structured error information
- Backwards compatibility
"""

import pytest
from http import HTTPStatus

from solstein.exceptions import (
    SolsteinError,
    DomainError,
    ValidationError,
    NotFoundError,
    StateError,
    ConflictError,
    PermissionError,
    AuthenticationError,
    RateLimitError,
    InfrastructureError,
    DatabaseError,
    LLMError,
    ExternalServiceError,
    ConfigurationError,
    # Backwards compatibility
    DataLoadError,
    ScoringError,
    ExportError,
    LLMAvailabilityError,
)


class TestBaseException:
    """Test SolsteinError base class."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = SolsteinError("Test message")
        assert exc.message == "Test message"
        assert exc.code == "INTERNAL_ERROR"
        assert exc.status_code == 500

    def test_exception_with_details(self):
        """Test exception with details."""
        exc = SolsteinError(
            "Test message",
            details={"field": "value", "count": 42},
        )
        assert exc.details["field"] == "value"
        assert exc.details["count"] == 42

    def test_exception_str(self):
        """Test string representation."""
        exc = SolsteinError("Test message", code="TEST_CODE")
        assert "[TEST_CODE]" in str(exc)
        assert "Test message" in str(exc)

    def test_exception_repr(self):
        """Test repr representation."""
        exc = SolsteinError("Test message", code="TEST_CODE", status_code=400)
        repr_str = repr(exc)
        assert "SolsteinError" in repr_str
        assert "TEST_CODE" in repr_str
        assert "400" in repr_str

    def test_to_dict(self):
        """Test conversion to dictionary."""
        exc = SolsteinError(
            "Test message",
            code="TEST_CODE",
            details={"key": "value"},
        )
        data = exc.to_dict()
        assert data["code"] == "TEST_CODE"
        assert data["message"] == "Test message"
        assert data["details"] == {"key": "value"}

    def test_to_dict_no_details(self):
        """Test to_dict without details."""
        exc = SolsteinError("Test message")
        data = exc.to_dict()
        assert "details" not in data

    def test_with_details(self):
        """Test with_details helper."""
        exc = SolsteinError("Test", details={"a": 1})
        enhanced = exc.with_details(b=2, c=3)

        assert enhanced.details["a"] == 1
        assert enhanced.details["b"] == 2
        assert enhanced.details["c"] == 3


class TestDomainErrors:
    """Test domain/business logic errors (4xx)."""

    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid input", details={"field": "email"})
        assert exc.code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert isinstance(exc, DomainError)

    def test_not_found_error(self):
        """Test NotFoundError with convenience constructor."""
        exc = NotFoundError("Company", "COMP-123")
        assert exc.code == "NOT_FOUND"
        assert exc.status_code == 404
        assert "Company not found: COMP-123" in exc.message
        assert exc.details["resource_type"] == "Company"
        assert exc.details["resource_id"] == "COMP-123"

    def test_state_error(self):
        """Test StateError."""
        exc = StateError("Cannot transition from PENDING to COMPLETED")
        assert exc.code == "STATE_ERROR"
        assert exc.status_code == 409

    def test_conflict_error(self):
        """Test ConflictError."""
        exc = ConflictError("Resource already exists")
        assert exc.code == "CONFLICT"
        assert exc.status_code == 409

    def test_permission_error(self):
        """Test PermissionError."""
        exc = PermissionError("Access denied")
        assert exc.code == "PERMISSION_DENIED"
        assert exc.status_code == 403

    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError("Invalid credentials")
        assert exc.code == "AUTHENTICATION_FAILED"
        assert exc.status_code == 401

    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after."""
        exc = RateLimitError("Too many requests", retry_after=60)
        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429
        assert exc.details["retry_after"] == 60


class TestInfrastructureErrors:
    """Test infrastructure errors (5xx)."""

    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError("Connection failed")
        assert exc.code == "DATABASE_ERROR"
        assert exc.status_code == 500
        assert isinstance(exc, InfrastructureError)

    def test_llm_error(self):
        """Test LLMError with provider info."""
        exc = LLMError(
            "API timeout",
            provider="openai",
            model="gpt-4",
        )
        assert exc.code == "LLM_ERROR"
        assert exc.status_code == 502
        assert exc.details["provider"] == "openai"
        assert exc.details["model"] == "gpt-4"

    def test_external_service_error(self):
        """Test ExternalServiceError with service name."""
        exc = ExternalServiceError(
            "Service unavailable",
            service="crunchbase",
        )
        assert exc.code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == 502
        assert exc.details["service"] == "crunchbase"

    def test_configuration_error(self):
        """Test ConfigurationError."""
        exc = ConfigurationError("Missing required config")
        assert exc.code == "CONFIGURATION_ERROR"
        assert exc.status_code == 500


class TestBackwardsCompatibility:
    """Test backwards compatibility aliases."""

    def test_data_load_error_alias(self):
        """Test DataLoadError is InfrastructureError."""
        exc = DataLoadError("Failed to load")
        assert isinstance(exc, InfrastructureError)
        assert exc.code == "INFRASTRUCTURE_ERROR"

    def test_scoring_error_alias(self):
        """Test ScoringError is DomainError."""
        exc = ScoringError("Scoring failed")
        assert isinstance(exc, DomainError)
        assert exc.code == "DOMAIN_ERROR"

    def test_export_error_alias(self):
        """Test ExportError is InfrastructureError."""
        exc = ExportError("Export failed")
        assert isinstance(exc, InfrastructureError)

    def test_llm_availability_error_alias(self):
        """Test LLMAvailabilityError is LLMError."""
        exc = LLMAvailabilityError("LLM unavailable")
        assert isinstance(exc, LLMError)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_all_inherit_from_solstein_error(self):
        """Test all exceptions inherit from SolsteinError."""
        exceptions = [
            DomainError("test"),
            ValidationError("test"),
            NotFoundError("Type", "ID"),
            StateError("test"),
            ConflictError("test"),
            PermissionError("test"),
            AuthenticationError("test"),
            RateLimitError("test"),
            InfrastructureError("test"),
            DatabaseError("test"),
            LLMError("test"),
            ExternalServiceError("test"),
            ConfigurationError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, SolsteinError)

    def test_http_status_codes(self):
        """Test all exceptions have valid HTTP status codes."""
        test_cases = [
            (ValidationError("test"), 400),
            (NotFoundError("T", "I"), 404),
            (PermissionError("test"), 403),
            (AuthenticationError("test"), 401),
            (RateLimitError("test"), 429),
            (StateError("test"), 409),
            (ConflictError("test"), 409),
            (DatabaseError("test"), 500),
            (LLMError("test"), 502),
            (ExternalServiceError("test"), 502),
            (ConfigurationError("test"), 500),
        ]

        for exc, expected_status in test_cases:
            assert exc.status_code == expected_status, f"{exc.__class__.__name__} has wrong status code"
