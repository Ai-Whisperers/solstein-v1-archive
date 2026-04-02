"""STORY-130: Tests for structured adapter logging.

Verifies that log_adapter_error emits structured fields required by
exception-handling.md: component, operation, error_type, message, entity_id.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from solstein.adapters.logging import log_adapter_error


class TestLogAdapterError:
    """Verify structured logging fields are emitted correctly."""

    @patch("solstein.adapters.logging.logger")
    def test_error_level_default(self, mock_logger: MagicMock) -> None:
        """Default level is error."""
        exc = ValueError("bad input")
        log_adapter_error(
            component="TestAdapter",
            operation="enrich",
            error=exc,
            entity_id="comp-123",
            entity_name="Acme Corp",
        )
        mock_logger.error.assert_called_once()
        call_kwargs = mock_logger.error.call_args
        assert call_kwargs.kwargs["component"] == "TestAdapter"
        assert call_kwargs.kwargs["operation"] == "enrich"
        assert call_kwargs.kwargs["error_type"] == "ValueError"
        assert call_kwargs.kwargs["message"] == "bad input"
        assert call_kwargs.kwargs["entity_id"] == "comp-123"
        assert call_kwargs.kwargs["entity_name"] == "Acme Corp"

    @patch("solstein.adapters.logging.logger")
    def test_warning_level(self, mock_logger: MagicMock) -> None:
        """Level=warning uses logger.warning."""
        exc = RuntimeError("timeout")
        log_adapter_error(
            component="FundingAdapter",
            operation="fetch_facts",
            error=exc,
            level="warning",
        )
        mock_logger.warning.assert_called_once()
        call_kwargs = mock_logger.warning.call_args
        assert call_kwargs.kwargs["error_type"] == "RuntimeError"

    @patch("solstein.adapters.logging.logger")
    def test_missing_entity_defaults_to_unknown(self, mock_logger: MagicMock) -> None:
        """Entity fields default to 'unknown' when not provided."""
        log_adapter_error(
            component="WebSearch",
            operation="discover",
            error=Exception("fail"),
        )
        call_kwargs = mock_logger.error.call_args
        assert call_kwargs.kwargs["entity_id"] == "unknown"
        assert call_kwargs.kwargs["entity_name"] == "unknown"

    @patch("solstein.adapters.logging.logger")
    def test_error_type_from_exception_class(self, mock_logger: MagicMock) -> None:
        """error_type reflects the actual exception class name."""
        log_adapter_error(
            component="Test",
            operation="test",
            error=ConnectionError("refused"),
        )
        assert mock_logger.error.call_args.kwargs["error_type"] == "ConnectionError"

    @patch("solstein.adapters.logging.logger")
    def test_message_includes_component_and_operation(self, mock_logger: MagicMock) -> None:
        """Log message includes [component] operation failed."""
        log_adapter_error(
            component="PatentsAdapter",
            operation="fetch_facts",
            error=TimeoutError("slow"),
        )
        msg = mock_logger.error.call_args[0][0]
        assert "[PatentsAdapter]" in msg
        assert "fetch_facts failed" in msg
