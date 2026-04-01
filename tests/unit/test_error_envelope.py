"""Tests for error envelope module.

F3: Tests for standardized error envelope.
"""

from solstein.core.error_envelope import (
    ErrorCategory,
    ErrorContext,
    ErrorEnvelope,
    ErrorEnvelopeBuilder,
    ErrorLevel,
    create_error_response,
)


class TestErrorContext:
    """Tests for ErrorContext dataclass."""

    def test_default_values(self) -> None:
        ctx = ErrorContext()
        assert ctx.request_id is None
        assert ctx.user_id is None
        assert ctx.extra == {}

    def test_to_dict_filters_none(self) -> None:
        ctx = ErrorContext(request_id="req-123", operation="test")
        result = ctx.to_dict()

        assert result == {"request_id": "req-123", "operation": "test"}
        assert "user_id" not in result

    def test_to_dict_includes_extra(self) -> None:
        ctx = ErrorContext(extra={"custom": "value"})
        result = ctx.to_dict()

        assert result["custom"] == "value"


class TestErrorEnvelope:
    """Tests for ErrorEnvelope dataclass."""

    def test_basic_creation(self) -> None:
        envelope = ErrorEnvelope(
            code="TEST_ERROR",
            message="Test error message",
        )

        assert envelope.code == "TEST_ERROR"
        assert envelope.message == "Test error message"
        assert envelope.level == ErrorLevel.ERROR
        assert envelope.version == "1.0"

    def test_auto_populates_category(self) -> None:
        envelope = ErrorEnvelope(
            code="VALIDATION_ERROR",
            message="Invalid input",
        )

        assert envelope.category == ErrorCategory.VALIDATION
        assert envelope.retryable is False

    def test_auto_populates_retryable(self) -> None:
        envelope = ErrorEnvelope(
            code="DATABASE_ERROR",
            message="DB failed",
        )

        assert envelope.category == ErrorCategory.INFRASTRUCTURE
        assert envelope.retryable is True

    def test_to_dict_basic(self) -> None:
        envelope = ErrorEnvelope(
            code="TEST_ERROR",
            message="Test message",
        )
        result = envelope.to_dict()

        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test message"
        assert "timestamp" in result["error"]
        assert "stack_trace" not in result["error"]

    def test_to_dict_with_stack_trace(self) -> None:
        envelope = ErrorEnvelope(
            code="TEST_ERROR",
            message="Test",
            stack_trace="Traceback...",
        )
        result = envelope.to_dict(include_stack_trace=True)

        assert result["error"]["stack_trace"] == "Traceback..."

    def test_to_log_dict(self) -> None:
        envelope = ErrorEnvelope(
            code="TEST_ERROR",
            message="Test",
            context=ErrorContext(request_id="req-123"),
            details={"field": "value"},
        )
        result = envelope.to_log_dict()

        assert result["error_code"] == "TEST_ERROR"
        assert result["error_context"]["request_id"] == "req-123"
        assert result["error_details"]["field"] == "value"

    def test_from_exception(self) -> None:
        try:
            raise ValueError("Something went wrong")
        except ValueError as e:
            envelope = ErrorEnvelope.from_exception(e)

        assert envelope.code == "ValueError"
        assert envelope.message == "Something went wrong"
        assert envelope.stack_trace is not None
        assert "ValueError" in envelope.stack_trace

    def test_from_exception_with_custom_code(self) -> None:
        try:
            raise RuntimeError("Failed")
        except RuntimeError as e:
            envelope = ErrorEnvelope.from_exception(e, code="CUSTOM_ERROR")

        assert envelope.code == "CUSTOM_ERROR"

    def test_validation_error_factory(self) -> None:
        envelope = ErrorEnvelope.validation_error(
            message="Invalid email",
            field="email",
            value="not-an-email",
        )

        assert envelope.code == "VALIDATION_ERROR"
        assert envelope.level == ErrorLevel.WARNING
        assert envelope.details["field"] == "email"
        assert envelope.details["value"] == "not-an-email"

    def test_not_found_error_factory(self) -> None:
        envelope = ErrorEnvelope.not_found_error(
            resource_type="Company",
            resource_id="comp-123",
        )

        assert envelope.code == "NOT_FOUND"
        assert envelope.level == ErrorLevel.INFO
        assert envelope.details["resource_type"] == "Company"
        assert envelope.details["resource_id"] == "comp-123"

    def test_external_service_error_factory(self) -> None:
        envelope = ErrorEnvelope.external_service_error(
            service="GitHub API",
            message="Rate limit exceeded",
        )

        assert envelope.code == "EXTERNAL_SERVICE_ERROR"
        assert envelope.level == ErrorLevel.ERROR
        assert envelope.details["service"] == "GitHub API"

    def test_chained_causes(self) -> None:
        cause = ErrorEnvelope(
            code="DB_ERROR",
            message="Database connection failed",
        )
        envelope = ErrorEnvelope(
            code="REQUEST_FAILED",
            message="Could not process request",
            cause=cause,
        )

        result = envelope.to_dict()
        assert result["error"]["cause"]["error"]["code"] == "DB_ERROR"


class TestErrorEnvelopeBuilder:
    """Tests for ErrorEnvelopeBuilder."""

    def test_fluent_interface(self) -> None:
        envelope = (
            ErrorEnvelopeBuilder()
            .code("TEST_ERROR")
            .message("Test message")
            .level(ErrorLevel.WARNING)
            .request_id("req-123")
            .user_id("user-456")
            .company_id("comp-789")
            .operation("test_op")
            .source("test_module")
            .detail("custom_field", "custom_value")
            .build()
        )

        assert envelope.code == "TEST_ERROR"
        assert envelope.message == "Test message"
        assert envelope.level == ErrorLevel.WARNING
        assert envelope.context.request_id == "req-123"
        assert envelope.context.user_id == "user-456"
        assert envelope.context.company_id == "comp-789"
        assert envelope.context.operation == "test_op"
        assert envelope.context.source == "test_module"
        assert envelope.details["custom_field"] == "custom_value"

    def test_multiple_details(self) -> None:
        envelope = ErrorEnvelopeBuilder().code("TEST").message("Test").details(a=1, b=2, c=3).build()

        assert envelope.details == {"a": 1, "b": 2, "c": 3}

    def test_caused_by(self) -> None:
        cause = ErrorEnvelope(
            code="CAUSE",
            message="Root cause",
        )

        envelope = ErrorEnvelopeBuilder().code("EFFECT").message("Effect").caused_by(cause).build()

        assert envelope.cause == cause


class TestCreateErrorResponse:
    """Tests for create_error_response function."""

    def test_basic_response(self) -> None:
        response = create_error_response(
            code="TEST_ERROR",
            message="Test message",
            status_code=400,
        )

        assert response["error"]["code"] == "TEST_ERROR"
        assert response["error"]["message"] == "Test message"
        assert response["status_code"] == 400

    def test_with_details(self) -> None:
        response = create_error_response(
            code="VALIDATION_ERROR",
            message="Invalid input",
            status_code=422,
            field="email",
            value="invalid",
        )

        assert response["details"]["field"] == "email"
        assert response["details"]["value"] == "invalid"


class TestErrorLevels:
    """Tests for ErrorLevel enum."""

    def test_all_levels_exist(self) -> None:
        assert ErrorLevel.DEBUG.value == "debug"
        assert ErrorLevel.INFO.value == "info"
        assert ErrorLevel.WARNING.value == "warning"
        assert ErrorLevel.ERROR.value == "error"
        assert ErrorLevel.CRITICAL.value == "critical"
