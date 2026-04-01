"""Metrics collection pipeline for Solstein monitoring.

EPIC-026 Story 1: Implements Prometheus metrics collection for:
- HTTP request metrics (count, duration, in-flight)
- Business metrics (companies enriched, reports generated)
- Database metrics (query counts, connection pool)
- LLM metrics (tokens, costs, latency)

Usage:
    from solstein.monitoring.metrics import REQUEST_DURATION, track_request

    @track_request
    async def my_endpoint():
        # Automatically tracked
        pass
"""

import asyncio
import time
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_LATEST

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response


# ============================================================================
# Application Info
# ============================================================================

APP_INFO = Info("solstein_app", "Application information")


def set_app_info(version: str, environment: str) -> None:
    """Set application info metrics.

    Args:
        version: Application version.
        environment: Deployment environment.
    """
    APP_INFO.info({"version": version, "environment": environment})


# ============================================================================
# HTTP Request Metrics
# ============================================================================

# Request counter with labels for method, endpoint, and status code
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

# Request duration histogram with endpoint label
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Current in-flight requests
HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
)

# Response size histogram
HTTP_RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["endpoint"],
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000],
)


# ============================================================================
# Business Metrics
# ============================================================================

# Companies enriched counter
COMPANIES_ENRICHED_TOTAL = Counter(
    "companies_enriched_total",
    "Total companies enriched",
    ["source", "classification"],
)

# Reports generated counter
REPORTS_GENERATED_TOTAL = Counter(
    "reports_generated_total",
    "Total reports generated",
    ["format"],
)

# Research runs counter
RESEARCH_RUNS_TOTAL = Counter(
    "research_runs_total",
    "Total research pipeline runs",
    ["status"],
)

# Pipeline stage duration
PIPELINE_STAGE_DURATION = Histogram(
    "pipeline_stage_duration_seconds",
    "Pipeline stage duration",
    ["stage"],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
)

# Companies in database gauge
COMPANIES_TOTAL = Gauge(
    "companies_total",
    "Total companies in database",
    ["classification", "tier"],
)

# Data quality score histogram
DATA_QUALITY_SCORE = Histogram(
    "data_quality_score",
    "Company data quality score distribution",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)


# ============================================================================
# Database Metrics
# ============================================================================

# Database query counter
DB_QUERIES_TOTAL = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"],
)

# Query duration histogram
DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

# Connection pool metrics
DB_POOL_CONNECTIONS = Gauge(
    "db_pool_connections",
    "Database pool connections",
    ["state"],  # in_use, idle, overflow
)

# Connection pool wait time
DB_POOL_WAIT_DURATION = Histogram(
    "db_pool_wait_duration_seconds",
    "Time waiting for database connection",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
)


# ============================================================================
# LLM Metrics
# ============================================================================

# Token usage counter
LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "LLM tokens consumed",
    ["provider", "model", "token_type"],  # token_type: input/output
)

# Cost counter
LLM_COST_DOLLARS = Counter(
    "llm_cost_dollars_total",
    "Estimated LLM cost in USD",
    ["provider", "model"],
)

# Request latency
LLM_REQUEST_DURATION = Histogram(
    "llm_request_duration_seconds",
    "LLM request duration",
    ["provider", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

# STORY-129: Request and error counters with classification labels
LLM_REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total LLM requests by provider, model, and outcome",
    ["provider", "model", "status"],  # status: success/error
)

LLM_ERRORS_TOTAL = Counter(
    "llm_errors_total",
    "Total LLM errors by provider and classified error type",
    ["provider", "error_type"],  # error_type: from ProviderErrorType enum
)

# Provider availability gauge
LLM_PROVIDER_AVAILABLE = Gauge(
    "llm_provider_available",
    "Provider availability (1=up, 0=down)",
    ["provider"],
)

# Cache hit rate
LLM_CACHE_HIT_RATE = Gauge(
    "llm_cache_hit_rate",
    "LLM response cache hit rate",
    ["provider"],
)


# ============================================================================
# System Metrics
# ============================================================================

# Active connections
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
    ["type"],
)

# Memory usage
MEMORY_USAGE_BYTES = Gauge(
    "memory_usage_bytes",
    "Memory usage in bytes",
    ["type"],  # rss, vms
)

# CPU usage percentage
CPU_USAGE_PERCENT = Gauge(
    "cpu_usage_percent",
    "CPU usage percentage",
)


# ============================================================================
# Decorators and Utilities
# ============================================================================


def track_request_duration(endpoint: str | None = None) -> Callable:
    """Decorator to track request duration.

    Args:
        endpoint: Endpoint name (defaults to function name).

    Returns:
        Decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            method = kwargs.get("method", "GET")
            name = endpoint or func.__name__

            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=name).inc()
            start = time.time()

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                HTTP_REQUEST_DURATION.labels(method=method, endpoint=name).observe(duration)
                HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=name).dec()

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            method = kwargs.get("method", "GET")
            name = endpoint or func.__name__

            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=name).inc()
            start = time.time()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                HTTP_REQUEST_DURATION.labels(method=method, endpoint=name).observe(duration)
                HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=name).dec()

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def track_llm_call(provider: str, model: str, tokens_in: int, tokens_out: int, cost: float, duration: float) -> None:
    """Track an LLM call with metrics.

    Args:
        provider: LLM provider name.
        model: Model name.
        tokens_in: Input token count.
        tokens_out: Output token count.
        cost: Estimated cost in USD.
        duration: Request duration in seconds.
    """
    LLM_TOKENS_TOTAL.labels(provider=provider, model=model, token_type="input").inc(tokens_in)
    LLM_TOKENS_TOTAL.labels(provider=provider, model=model, token_type="output").inc(tokens_out)
    LLM_COST_DOLLARS.labels(provider=provider, model=model).inc(cost)
    LLM_REQUEST_DURATION.labels(provider=provider, model=model).observe(duration)


def track_db_query(operation: str, table: str, duration: float) -> None:
    """Track a database query.

    Args:
        operation: Query operation (select, insert, update, delete).
        table: Table name.
        duration: Query duration in seconds.
    """
    DB_QUERIES_TOTAL.labels(operation=operation, table=table).inc()
    DB_QUERY_DURATION.labels(operation=operation).observe(duration)


def track_pipeline_stage(stage: str, duration: float) -> None:
    """Track pipeline stage execution.

    Args:
        stage: Stage name (discovery, enrichment, scoring, etc.).
        duration: Stage duration in seconds.
    """
    PIPELINE_STAGE_DURATION.labels(stage=stage).observe(duration)


def set_company_metrics(total: int, by_classification: dict[str, int], by_tier: dict[str, int]) -> None:
    """Set company count metrics.

    Args:
        total: Total company count.
        by_classification: Counts by classification (Phoenix, Salt, Lead).
        by_tier: Counts by tier.
    """
    for classification, count in by_classification.items():
        COMPANIES_TOTAL.labels(classification=classification, tier="all").set(count)

    for tier, count in by_tier.items():
        COMPANIES_TOTAL.labels(classification="all", tier=tier).set(count)


def record_http_request(method: str, endpoint: str, status_code: int, duration: float, response_size: int = 0) -> None:
    """Record HTTP request metrics.

    Args:
        method: HTTP method.
        endpoint: Endpoint path or name.
        status_code: HTTP status code.
        duration: Request duration in seconds.
        response_size: Response size in bytes.
    """
    HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
    HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    if response_size > 0:
        HTTP_RESPONSE_SIZE.labels(endpoint=endpoint).observe(response_size)


# ============================================================================
# FastAPI Middleware
# ============================================================================

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class PrometheusMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware to collect Prometheus metrics."""

    def __init__(self, app: ASGIApp, app_name: str = "solstein"):
        """Initialize middleware.

        Args:
            app: ASGI application.
            app_name: Application name for metrics.
        """
        super().__init__(app)
        self.app_name = app_name

    async def dispatch(self, request: "Request", call_next: Callable) -> "Response":
        """Process request and collect metrics.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response.
        """
        method = request.method
        endpoint = request.url.path

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        start = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.time() - start
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
            ).inc()
            HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        return response


# ============================================================================
# Metrics Endpoint
# ============================================================================

from fastapi import Response


class MetricsResponse(Response):
    """Response class for Prometheus metrics endpoint."""

    media_type = CONTENT_TYPE_LATEST


def get_metrics_response() -> MetricsResponse:
    """Get Prometheus metrics as HTTP response.

    Returns:
        MetricsResponse with Prometheus format.
    """
    return MetricsResponse(content=generate_latest())
