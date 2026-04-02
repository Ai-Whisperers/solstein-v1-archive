"""OpenTelemetry distributed tracing configuration.

STORY-050: Configures the OTel SDK, exporter, and provides span helpers
for instrumenting the research pipeline, LLM calls, and database queries.

Tracing is disabled gracefully when OTLP_ENDPOINT is not set.
"""

from __future__ import annotations

import os
from contextvars import ContextVar
from typing import Any

from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import StatusCode

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor as _FastAPIInstrumentor
except ImportError:
    _FastAPIInstrumentor = None  # type: ignore[assignment,misc]

# Module-level state
_tracer: trace.Tracer | None = None
_initialized: bool = False
_enabled: bool = False

# Context var for passing company_id into span attributes
SPAN_COMPANY_ID: ContextVar[str | None] = ContextVar("span_company_id", default=None)


def init_tracing(
    service_name: str = "solstein",
    otlp_endpoint: str | None = None,
) -> bool:
    """Initialize OpenTelemetry tracing.

    If OTLP_ENDPOINT env var (or otlp_endpoint param) is not set,
    tracing is disabled silently — no error, no overhead.

    Args:
        service_name: Service name for the resource.
        otlp_endpoint: OTLP exporter endpoint. Falls back to OTLP_ENDPOINT env var.

    Returns:
        True if tracing was enabled, False if disabled.
    """
    global _tracer, _initialized, _enabled  # noqa: PLW0603

    if _initialized:
        return _enabled

    endpoint = otlp_endpoint or os.environ.get("OTLP_ENDPOINT")

    if not endpoint:
        logger.info("OTLP_ENDPOINT not set — tracing disabled")
        _initialized = True
        _enabled = False
        # Set a no-op tracer so span creation calls are safe
        _tracer = trace.get_tracer(service_name)
        return False

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        _initialized = True
        _enabled = True

        logger.info(
            "OpenTelemetry tracing initialized",
            endpoint=endpoint,
            service=service_name,
        )
        return True

    except Exception as e:  # noqa: BLE001 — graceful degradation
        logger.warning(f"Failed to initialize tracing: {e}")
        _tracer = trace.get_tracer(service_name)
        _initialized = True
        _enabled = False
        return False


def get_tracer() -> trace.Tracer:
    """Get the configured tracer. Safe to call before init (returns no-op)."""
    global _tracer  # noqa: PLW0603
    if _tracer is None:
        _tracer = trace.get_tracer("solstein")
    return _tracer


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled."""
    return _enabled


def create_span(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> trace.Span:
    """Create a new span with standard Solstein attributes.

    Automatically includes correlation_id and company_id if available.

    Args:
        name: Span operation name (e.g., "llm.call", "db.query", "agent.github").
        attributes: Additional span attributes.

    Returns:
        A context manager span.
    """
    tracer = get_tracer()
    span = tracer.start_span(name)

    # Add standard attributes
    all_attrs: dict[str, Any] = {}

    # Include correlation_id from contextvars
    try:
        from ..utils.context import CORRELATION_ID

        cid = CORRELATION_ID.get()
        if cid:
            all_attrs["correlation_id"] = cid
    except LookupError:
        pass

    # Include company_id if set
    company_id = SPAN_COMPANY_ID.get()
    if company_id:
        all_attrs["company_id"] = company_id

    if attributes:
        all_attrs.update(attributes)

    for key, value in all_attrs.items():
        span.set_attribute(key, str(value))

    return span


def instrument_fastapi(app: Any) -> None:
    """Instrument a FastAPI app with OpenTelemetry auto-instrumentation.

    Only instruments if tracing is enabled. No-op otherwise.

    Args:
        app: FastAPI application instance.
    """
    if not _enabled:
        logger.debug("Tracing disabled — skipping FastAPI instrumentation")
        return

    if _FastAPIInstrumentor is None:
        logger.warning("opentelemetry-instrumentation-fastapi not installed")
        return

    try:
        _FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumented with OpenTelemetry")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to instrument FastAPI: {e}")


def record_span_error(span: trace.Span, error: Exception) -> None:
    """Record an error on a span and set status to ERROR.

    Args:
        span: The active span.
        error: The exception that occurred.
    """
    span.set_status(StatusCode.ERROR, str(error))
    span.record_exception(error)


def record_span_success(span: trace.Span) -> None:
    """Mark a span as successful.

    Args:
        span: The active span.
    """
    span.set_status(StatusCode.OK)
