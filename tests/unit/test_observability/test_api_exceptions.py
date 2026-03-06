"""Tests for secure error response handling.

This module tests that:
- Stack traces are NEVER exposed in production error responses
- Sensitive data is redacted from error responses
- Full error details are logged server-side
- Debug info only appears when explicitly enabled in non-prod
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from solstein.api.exceptions import (
    APIError,
    setup_exception_handlers,
    _should_expose_debug_info,
    _filter_safe_details,
    _create_error_response,
)
from solstein.exceptions import ValidationError, NotFoundError


class TestShouldExposeDebugInfo:
    """Test debug info exposure logic."""

    def test_production_never_exposes_debug(self):
        """Test that production never exposes debug info."""
        with patch("solstein.api.exceptions.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                debug_errors=True,
                environment="production",
            )
            assert _should_expose_debug_info() is False

    def test_staging_never_exposes_debug(self):
        """Test that staging never exposes debug info."""
        with patch("solstein.api.exceptions.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                debug_errors=True,
                environment="staging",
            )
            assert _should_expose_debug_info() is False

    def test_development_can_expose_debug(self):
        """Test that development can expose debug when enabled."""
        with patch("solstein.api.exceptions.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                debug_errors=True,
                environment="development",
            )
            assert _should_expose_debug_info() is True

    def test_development_respects_flag(self):
        """Test that development respects debug_errors flag."""
        with patch("solstein.api.exceptions.get_settings") as mock_settings:
            mock_settings.return_value = Mock(
                debug_errors=False,
                environment="development",
            )
            assert _should_expose_debug_info() is False


class TestFilterSafeDetails:
    """Test sensitive detail redaction."""

    def test_password_redacted(self):
        """Test passwords are redacted."""
        details = {"username": "john", "password": "secret123"}
        safe = _filter_safe_details(details)
        assert safe["username"] == "john"
        assert safe["password"] == "[REDACTED]"

    def test_sql_query_redacted(self):
        """Test SQL queries are redacted."""
        details = {"table": "users", "query": "SELECT * FROM passwords"}
        safe = _filter_safe_details(details)
        assert safe["table"] == "users"
        assert safe["query"] == "[REDACTED]"

    def test_file_path_redacted(self):
        """Test file paths are redacted."""
        details = {"filename": "/etc/passwd", "config": "value"}
        safe = _filter_safe_details(details)
        assert safe["filename"] == "[REDACTED]"
        assert safe["config"] == "value"

    def test_nested_dict_redaction(self):
        """Test nested dicts are recursively filtered."""
        details = {
            "user": {"name": "john", "password": "secret"},
            "safe_field": "visible",
        }
        safe = _filter_safe_details(details)
        assert safe["user"]["name"] == "john"
        assert safe["user"]["password"] == "[REDACTED]"
        assert safe["safe_field"] == "visible"

    def test_none_details(self):
        """Test None details returns empty dict."""
        assert _filter_safe_details(None) == {}


class TestCreateErrorResponse:
    """Test error response creation."""

    def test_basic_error_response(self):
        """Test basic error response structure."""
        response = _create_error_response(
            code="TEST_ERROR",
            message="Test message",
            request_id="req-123",
        )

        assert response.status_code == 500
        data = response.body
        assert b'"code":"TEST_ERROR"' in data
        assert b'"message":"Test message"' in data
        assert b'"request_id":"req-123"' in data

    def test_no_debug_in_production(self):
        """Test debug info absent in production."""
        with patch("solstein.api.exceptions._should_expose_debug_info") as mock:
            mock.return_value = False

            response = _create_error_response(
                code="ERROR",
                message="Error",
                request_id="req-123",
                exc=Exception("secret"),
            )

            data = response.body.decode()
            assert "debug" not in data
            assert "traceback" not in data

    def test_debug_in_development(self):
        """Test debug info present in development."""
        with patch("solstein.api.exceptions._should_expose_debug_info") as mock:
            mock.return_value = True

            response = _create_error_response(
                code="ERROR",
                message="Error",
                request_id="req-123",
                exc=Exception("test error"),
            )

            data = response.body.decode()
            assert "debug" in data
            assert "traceback" in data


class TestAPIError:
    """Test APIError custom exception."""

    def test_api_error_creation(self):
        """Test APIError creation."""
        exc = APIError("NOT_FOUND", "Resource not found", 404)
        assert exc.code == "NOT_FOUND"
        assert exc.message == "Resource not found"
        assert exc.status_code == 404


class TestSolsteinErrorHandler:
    """Test SolsteinError exception handler."""

    @pytest.mark.asyncio
    async def test_solstein_error_response(self):
        """Test SolsteinError handler returns proper response."""
        from solstein.api.exceptions import solstein_error_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        exc = NotFoundError("Company", "COMP-123")

        response = await solstein_error_handler(mock_request, exc)

        assert response.status_code == 404
        data = response.body.decode()
        assert "NOT_FOUND" in data
        assert "req-123" in data

    @pytest.mark.asyncio
    async def test_solstein_error_no_traceback(self):
        """Test SolsteinError response never has traceback."""
        from solstein.api.exceptions import solstein_error_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        exc = ValidationError("Invalid input")

        with patch("solstein.api.exceptions._should_expose_debug_info") as mock:
            mock.return_value = False

            response = await solstein_error_handler(mock_request, exc)
            data = response.body.decode()
            assert "traceback" not in data.lower()


class TestValidationExceptionHandler:
    """Test Pydantic validation error handler."""

    @pytest.mark.asyncio
    async def test_validation_error_formatting(self):
        """Test validation errors are formatted properly."""
        from solstein.api.exceptions import validation_exception_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"

        # Create validation error
        errors = [
            {"loc": ["body", "email"], "msg": "Invalid email", "type": "value_error"},
            {"loc": ["body", "age"], "msg": "Must be positive", "type": "type_error"},
        ]
        exc = RequestValidationError(errors=errors)

        response = await validation_exception_handler(mock_request, exc)

        assert response.status_code == 422
        data = response.body.decode()
        assert "VALIDATION_ERROR" in data
        assert "email" in data
        assert "age" in data


class TestHTTPExceptionHandler:
    """Test Starlette HTTP exception handler."""

    @pytest.mark.asyncio
    async def test_404_error(self):
        """Test 404 error handling."""
        from solstein.api.exceptions import http_exception_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"

        exc = StarletteHTTPException(status_code=404, detail="Not found")

        response = await http_exception_handler(mock_request, exc)

        assert response.status_code == 404
        data = response.body.decode()
        assert "NOT_FOUND" in data

    @pytest.mark.asyncio
    async def test_401_error(self):
        """Test 401 error handling."""
        from solstein.api.exceptions import http_exception_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"

        exc = StarletteHTTPException(status_code=401, detail="Unauthorized")

        response = await http_exception_handler(mock_request, exc)

        assert response.status_code == 401
        data = response.body.decode()
        assert "UNAUTHORIZED" in data


class TestGlobalExceptionHandler:
    """Test global exception handler."""

    @pytest.mark.asyncio
    async def test_internal_error_response(self):
        """Test internal error returns safe response."""
        from solstein.api.exceptions import global_exception_handler

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        exc = ValueError("Something went wrong")

        with patch("solstein.api.exceptions._should_expose_debug_info") as mock:
            mock.return_value = False

            response = await global_exception_handler(mock_request, exc)

            assert response.status_code == 500
            data = response.body.decode()
            assert "INTERNAL_ERROR" in data
            assert "req-123" in data
            # Should have generic message
            assert "internal error occurred" in data.lower()
            # Should NOT have internal details
            assert "ValueError" not in data
            assert "Something went wrong" not in data

    @pytest.mark.asyncio
    async def test_global_handler_logs_server_side(self):
        """Test global handler logs full details server-side."""
        from solstein.api.exceptions import global_exception_handler
        from solstein.api.exceptions import logger as exc_logger

        mock_request = Mock(spec=Request)
        mock_request.state.request_id = "req-123"
        mock_request.url.path = "/test"
        mock_request.method = "GET"
        mock_request.state.correlation_id = "corr-456"

        exc = ValueError("Secret error details")

        with patch.object(exc_logger, "error") as mock_log:
            with patch("solstein.api.exceptions._should_expose_debug_info") as mock:
                mock.return_value = False

                await global_exception_handler(mock_request, exc)

                # Verify server-side logging
                mock_log.assert_called_once()
                call_kwargs = mock_log.call_args.kwargs
                assert call_kwargs["error_type"] == "ValueError"
                assert "Secret error details" in call_kwargs["error_message"]
                assert "traceback" in call_kwargs
