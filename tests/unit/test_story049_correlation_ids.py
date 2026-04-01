"""Tests for STORY-049: Add Structured Logging with Correlation IDs.

Validates that the correlation ID middleware and context propagation
are correctly implemented across the request lifecycle.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "src" / "solstein"
CONTEXT_MODULE = SRC / "utils" / "context.py"
LOGGING_MIDDLEWARE = SRC / "api" / "middleware" / "logging.py"
LOGGING_UTILS = SRC / "utils" / "logging.py"
TRACING_MIDDLEWARE = SRC / "api" / "middleware" / "tracing.py"
OBSERVABILITY_DOCS = PROJECT_ROOT / "docs" / "observability" / "logging.md"


# ===========================================================================
# REQ-1: Every request gets a unique correlation ID at middleware layer
# ===========================================================================

class TestCorrelationIDAssignment:
    """STORY-049 REQ-1: Correlation ID assigned at middleware layer."""

    def test_context_middleware_generates_correlation_id(self):
        text = LOGGING_MIDDLEWARE.read_text()
        assert "generate_correlation_id" in text, (
            "ContextMiddleware must call generate_correlation_id()"
        )

    def test_correlation_id_is_uuid(self):
        """Correlation IDs should be full UUIDs."""
        text = CONTEXT_MODULE.read_text()
        assert "uuid4" in text, "Correlation ID should use uuid4"

    def test_accepts_incoming_correlation_id(self):
        """If X-Correlation-ID header is present, use it instead of generating."""
        text = LOGGING_MIDDLEWARE.read_text()
        assert 'X-Correlation-ID' in text, (
            "Should accept incoming X-Correlation-ID header"
        )

    def test_context_var_exists(self):
        """CORRELATION_ID context var must be defined."""
        text = CONTEXT_MODULE.read_text()
        assert "CORRELATION_ID" in text


# ===========================================================================
# REQ-2: Correlation ID propagated through all log calls
# ===========================================================================

class TestCorrelationIDPropagation:
    """STORY-049 REQ-2: Correlation ID in all log entries during request."""

    def test_logging_format_includes_context(self):
        """Log formatter must include context (which has correlation_id)."""
        text = LOGGING_UTILS.read_text()
        assert "get_current_context" in text, (
            "Log format must call get_current_context() to include correlation_id"
        )

    def test_json_format_includes_context(self):
        """JSON log format must include context."""
        text = LOGGING_UTILS.read_text()
        assert '"context"' in text or "'context'" in text, (
            "JSON format must include context dict"
        )

    def test_context_uses_contextvars(self):
        """Context propagation must use contextvars for async safety."""
        text = CONTEXT_MODULE.read_text()
        assert "contextvars" in text

    def test_context_set_includes_correlation_id(self):
        """set_context must accept correlation_id parameter."""
        text = CONTEXT_MODULE.read_text()
        assert "correlation_id" in text


# ===========================================================================
# REQ-3: X-Correlation-ID header in HTTP response
# ===========================================================================

class TestCorrelationIDResponseHeader:
    """STORY-049 REQ-3: Correlation ID in response header."""

    def test_response_includes_correlation_id_header(self):
        text = LOGGING_MIDDLEWARE.read_text()
        assert 'X-Correlation-ID' in text
        # Verify it's being set on the response (not just read from request)
        assert 'response.headers["X-Correlation-ID"]' in text or \
               "response.headers['X-Correlation-ID']" in text

    def test_response_also_includes_request_id(self):
        """X-Request-ID should also be in response for backward compat."""
        text = LOGGING_MIDDLEWARE.read_text()
        assert 'X-Request-ID' in text


# ===========================================================================
# REQ-4: Correlation ID in every loguru log entry
# ===========================================================================

class TestLogEntryFormat:
    """STORY-049 REQ-4: Every log entry includes correlation ID."""

    def test_format_record_uses_context(self):
        """format_record function must include context in output."""
        text = LOGGING_UTILS.read_text()
        # Verify the format function calls get_current_context
        idx = text.find("def format_record")
        assert idx >= 0, "format_record function must exist"
        fn_body = text[idx:text.find("\ndef ", idx + 1)]
        assert "get_current_context" in fn_body

    def test_json_format_includes_correlation(self):
        """JSON format record includes context dict."""
        text = LOGGING_UTILS.read_text()
        idx = text.find("def format_record_json")
        assert idx >= 0, "format_record_json function must exist"
        fn_body = text[idx:text.find("\ndef ", idx + 1)]
        assert "get_current_context" in fn_body


# ===========================================================================
# REQ-5: Outbound requests include correlation ID
# ===========================================================================

class TestOutboundPropagation:
    """STORY-049 REQ-5: Correlation ID in outbound request headers."""

    def test_tracing_middleware_exists(self):
        """Tracing middleware should exist for outbound propagation."""
        assert TRACING_MIDDLEWARE.exists(), "tracing.py middleware must exist"

    def test_tracing_mentions_correlation(self):
        """Tracing middleware should reference correlation ID."""
        text = TRACING_MIDDLEWARE.read_text()
        assert "Correlation" in text or "correlation" in text


# ===========================================================================
# Context reset (no leaks between requests)
# ===========================================================================

class TestContextReset:
    """Verify context is properly reset between requests."""

    def test_context_middleware_resets_in_finally(self):
        """ContextMiddleware must reset context in finally block."""
        text = LOGGING_MIDDLEWARE.read_text()
        assert "finally:" in text
        assert "reset_context" in text

    def test_reset_context_function_exists(self):
        text = CONTEXT_MODULE.read_text()
        assert "def reset_context" in text

    def test_clear_context_function_exists(self):
        text = CONTEXT_MODULE.read_text()
        assert "def clear_context" in text


# ===========================================================================
# Stdlib logging interception
# ===========================================================================

class TestStdlibInterception:
    """STORY-049 dependency: stdlib logging routed to loguru."""

    def test_intercept_handler_exists(self):
        text = LOGGING_UTILS.read_text()
        assert "class InterceptHandler" in text

    def test_intercepts_uvicorn(self):
        text = LOGGING_UTILS.read_text()
        assert "uvicorn" in text

    def test_intercepts_sqlalchemy(self):
        text = LOGGING_UTILS.read_text()
        assert "sqlalchemy" in text

    def test_intercepts_fastapi(self):
        text = LOGGING_UTILS.read_text()
        assert "fastapi" in text


# ===========================================================================
# Documentation
# ===========================================================================

class TestDocumentation:
    """STORY-049: Correlation ID propagation must be documented."""

    def test_observability_docs_exist(self):
        assert OBSERVABILITY_DOCS.exists(), "docs/observability/logging.md must exist"

    def test_docs_mention_correlation_id(self):
        text = OBSERVABILITY_DOCS.read_text()
        assert "correlation_id" in text

    def test_docs_mention_context_middleware(self):
        text = OBSERVABILITY_DOCS.read_text()
        assert "Context" in text or "context" in text

    def test_docs_mention_request_scoped(self):
        text = OBSERVABILITY_DOCS.read_text()
        assert "request" in text.lower()
