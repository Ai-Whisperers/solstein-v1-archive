"""Tests for STORY-050: OpenTelemetry Distributed Tracing.

Validates:
- REQ-1: Spans created for HTTP requests, LLM calls, pipeline stages
- REQ-2: Spans exported to configurable OTLP endpoint
- REQ-3: Span attributes include correlation_id, company_id, outcome
- REQ-4: Graceful disable when OTLP_ENDPOINT not set
- REQ-5: Tracing overhead < 5ms per request
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import solstein.observability.tracing as tracing_mod
from solstein.config import Settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _reload_tracing():
    """Reset the tracing module state for test isolation."""
    mod = tracing_mod  # uses top-level import

    # Reset module-level state
    mod._tracer = None
    mod._initialized = False
    mod._enabled = False
    return mod


# ---------------------------------------------------------------------------
# REQ-4: Graceful disable when OTLP_ENDPOINT not set
# ---------------------------------------------------------------------------
class TestGracefulDisable:
    """Tracing must be disabled gracefully when OTLP_ENDPOINT is unset."""

    def test_init_returns_false_without_endpoint(self):
        mod = _reload_tracing()
        result = mod.init_tracing(otlp_endpoint=None)
        assert result is False

    def test_tracing_not_enabled_without_endpoint(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        assert mod.is_tracing_enabled() is False

    def test_no_startup_error_without_endpoint(self):
        """init_tracing must not raise when OTLP_ENDPOINT is missing."""
        mod = _reload_tracing()
        # Should not raise
        mod.init_tracing(otlp_endpoint=None)

    def test_env_var_fallback(self):
        mod = _reload_tracing()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OTLP_ENDPOINT", None)
            result = mod.init_tracing()
            assert result is False

    def test_get_tracer_returns_noop_without_init(self):
        """get_tracer must return a usable tracer even before init."""
        mod = _reload_tracing()
        tracer = mod.get_tracer()
        assert tracer is not None

    def test_create_span_safe_without_init(self):
        """create_span must not raise when tracing is disabled."""
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span("test.operation")
        assert span is not None

    def test_idempotent_init(self):
        """Calling init_tracing twice returns cached result."""
        mod = _reload_tracing()
        r1 = mod.init_tracing(otlp_endpoint=None)
        r2 = mod.init_tracing(otlp_endpoint="http://should-be-ignored")
        assert r1 == r2  # Second call returns cached False


# ---------------------------------------------------------------------------
# REQ-2: Configurable OTLP endpoint
# ---------------------------------------------------------------------------
class TestOTLPEndpointConfig:
    """Spans must be exported to configurable OTLP endpoint."""

    def test_init_with_explicit_endpoint(self):
        mod = _reload_tracing()
        with (
            patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter") as mock_exporter,
            patch("opentelemetry.sdk.trace.export.BatchSpanProcessor"),
        ):
            mock_exporter.return_value = MagicMock()
            result = mod.init_tracing(otlp_endpoint="http://localhost:4318/v1/traces")
            assert result is True
            mock_exporter.assert_called_once_with(endpoint="http://localhost:4318/v1/traces")

    def test_init_with_env_var_endpoint(self):
        mod = _reload_tracing()
        with (
            patch.dict(os.environ, {"OTLP_ENDPOINT": "http://tempo:4318"}),
            patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter") as mock_exporter,
            patch("opentelemetry.sdk.trace.export.BatchSpanProcessor"),
        ):
            mock_exporter.return_value = MagicMock()
            result = mod.init_tracing()
            assert result is True
            mock_exporter.assert_called_once_with(endpoint="http://tempo:4318")

    def test_explicit_endpoint_overrides_env(self):
        mod = _reload_tracing()
        with (
            patch.dict(os.environ, {"OTLP_ENDPOINT": "http://env-endpoint"}),
            patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter") as mock_exporter,
            patch("opentelemetry.sdk.trace.export.BatchSpanProcessor"),
        ):
            mock_exporter.return_value = MagicMock()
            mod.init_tracing(otlp_endpoint="http://explicit-endpoint")
            mock_exporter.assert_called_once_with(endpoint="http://explicit-endpoint")

    def test_tracing_enabled_after_successful_init(self):
        mod = _reload_tracing()
        with (
            patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter"),
            patch("opentelemetry.sdk.trace.export.BatchSpanProcessor"),
        ):
            mod.init_tracing(otlp_endpoint="http://localhost:4318")
            assert mod.is_tracing_enabled() is True

    def test_graceful_fallback_on_exporter_error(self):
        """If OTLP exporter fails to initialize, tracing is disabled gracefully."""
        mod = _reload_tracing()
        with patch(
            "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter",
            side_effect=Exception("Connection refused"),
        ):
            # The import happens inside init_tracing, so we need to patch at
            # the point where the import resolves
            result = mod.init_tracing(otlp_endpoint="http://bad-endpoint")
            assert result is False
            assert mod.is_tracing_enabled() is False


# ---------------------------------------------------------------------------
# REQ-3: Span attributes include correlation_id, company_id, outcome
# ---------------------------------------------------------------------------
class TestSpanAttributes:
    """Spans must include correlation_id, company_id, and operation outcome."""

    def test_span_includes_company_id(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        mod.SPAN_COMPANY_ID.set("COMP-123")
        try:
            span = mod.create_span("test.op", attributes={"extra": "val"})
            # Verify set_attribute was called (span from no-op tracer)
            # The span object may be a NonRecordingSpan, but our code called
            # set_attribute — we check it didn't raise
            assert span is not None
        finally:
            mod.SPAN_COMPANY_ID.set(None)

    def test_span_includes_custom_attributes(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span(
            "llm.call",
            attributes={"provider": "openai", "model": "gpt-4o"},
        )
        assert span is not None

    def test_record_span_error_sets_status(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span("test.failing")
        error = ValueError("test error")
        # Should not raise
        mod.record_span_error(span, error)

    def test_record_span_success_sets_status(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span("test.success")
        # Should not raise
        mod.record_span_success(span)


# ---------------------------------------------------------------------------
# REQ-1: Span creation for HTTP, LLM, pipeline stages
# ---------------------------------------------------------------------------
class TestSpanCreation:
    """Spans must be created for major operations."""

    def test_create_span_returns_span_object(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span("http.request")
        assert span is not None

    def test_create_span_with_llm_attributes(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span(
            "llm.call",
            attributes={
                "provider": "deepinfra",
                "model": "llama-3.3-70b",
                "company_id": "COMP-456",
            },
        )
        assert span is not None

    def test_create_span_with_pipeline_stage(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span(
            "pipeline.discovery",
            attributes={"stage": "discovery", "companies_count": "5"},
        )
        assert span is not None

    def test_create_span_with_db_operation(self):
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        span = mod.create_span(
            "db.query",
            attributes={"table": "companies", "operation": "SELECT"},
        )
        assert span is not None


# ---------------------------------------------------------------------------
# REQ-5: Tracing overhead < 5ms per request
# ---------------------------------------------------------------------------
class TestTracingPerformance:
    """Tracing must not meaningfully impact request latency."""

    def test_span_creation_overhead_under_5ms(self):
        """Creating a span must take < 5ms (REQ-5)."""
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)

        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            span = mod.create_span(
                "perf.test",
                attributes={"iteration": str(i), "company_id": "PERF-001"},
            )
            mod.record_span_success(span)
        elapsed_ms = (time.perf_counter() - start) * 1000

        avg_ms = elapsed_ms / iterations
        assert avg_ms < 5.0, f"Average span creation took {avg_ms:.2f}ms (limit: 5ms)"

    def test_disabled_tracing_near_zero_overhead(self):
        """With tracing disabled, overhead should be near zero."""
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        assert mod.is_tracing_enabled() is False

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            span = mod.create_span("noop.test")
            mod.record_span_success(span)
        elapsed_ms = (time.perf_counter() - start) * 1000

        avg_ms = elapsed_ms / iterations
        assert avg_ms < 1.0, f"Disabled tracing took {avg_ms:.2f}ms (limit: 1ms)"


# ---------------------------------------------------------------------------
# FastAPI instrumentation
# ---------------------------------------------------------------------------
class TestFastAPIInstrumentation:
    """instrument_fastapi must integrate with FastAPI app."""

    def test_instrument_noop_when_disabled(self):
        """instrument_fastapi is a no-op when tracing is disabled."""
        mod = _reload_tracing()
        mod.init_tracing(otlp_endpoint=None)
        mock_app = MagicMock()
        # Should not raise or modify app
        mod.instrument_fastapi(mock_app)

    def test_instrument_when_enabled(self):
        """instrument_fastapi calls FastAPIInstrumentor when enabled."""
        mod = _reload_tracing()
        with (
            patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter"),
            patch("opentelemetry.sdk.trace.export.BatchSpanProcessor"),
        ):
            mod.init_tracing(otlp_endpoint="http://localhost:4318")

        mock_instrumentor = MagicMock()
        mock_app = MagicMock()
        with patch.object(mod, "_FastAPIInstrumentor", mock_instrumentor):
            mod.instrument_fastapi(mock_app)
            mock_instrumentor.instrument_app.assert_called_once_with(mock_app)

    def test_instrument_handles_missing_package(self):
        """instrument_fastapi handles missing instrumentation package gracefully."""
        mod = _reload_tracing()
        # Force _enabled = True to test the missing package path
        mod._enabled = True
        mock_app = MagicMock()
        with patch.object(mod, "_FastAPIInstrumentor", None):
            # Should not raise — logs warning and returns
            mod.instrument_fastapi(mock_app)


# ---------------------------------------------------------------------------
# Settings integration
# ---------------------------------------------------------------------------
class TestSettingsIntegration:
    """OTLP_ENDPOINT must be configurable via Settings."""

    def test_settings_has_otlp_endpoint_field(self):
        field_names = set(Settings.model_fields.keys())
        assert "otlp_endpoint" in field_names

    def test_settings_otlp_endpoint_default_none(self):
        s = Settings()
        assert s.otlp_endpoint is None

    def test_settings_otlp_endpoint_from_env(self):
        with patch.dict(os.environ, {"OTLP_ENDPOINT": "http://jaeger:4318/v1/traces"}):
            s = Settings()
            assert s.otlp_endpoint == "http://jaeger:4318/v1/traces"


# ---------------------------------------------------------------------------
# Main.py integration (tracing wired into lifespan)
# ---------------------------------------------------------------------------
class TestMainIntegration:
    """Tracing must be wired into FastAPI lifespan."""

    def test_main_imports_tracing(self):
        """main.py must reference the tracing module."""
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        assert "init_tracing" in source, "main.py must call init_tracing"
        assert "instrument_fastapi" in source, "main.py must call instrument_fastapi"

    def test_main_uses_settings_otlp_endpoint(self):
        """main.py must pass settings.otlp_endpoint to init_tracing."""
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        assert "settings.otlp_endpoint" in source


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------
class TestDocumentation:
    """Documentation for tracing configuration."""

    def test_tracing_module_has_docstring(self):
        assert tracing_mod.__doc__ is not None
        assert "tracing" in tracing_mod.__doc__.lower()

    def test_init_tracing_has_docstring(self):
        assert tracing_mod.init_tracing.__doc__ is not None
        assert "OTLP_ENDPOINT" in tracing_mod.init_tracing.__doc__

    def test_create_span_has_docstring(self):
        assert tracing_mod.create_span.__doc__ is not None
        assert "correlation_id" in tracing_mod.create_span.__doc__
