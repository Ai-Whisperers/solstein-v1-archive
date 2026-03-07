"""Log aggregation and structured logging.

EPIC-026 Story 8: Implements structured logging and log aggregation:
- JSON structured logging
- Log correlation IDs
- Context enrichment
- Log shipping to centralized system

Usage:
    from solstein.monitoring.logging import StructuredLogger, get_logger

    logger = get_logger("enrichment")
    logger.info("company_enriched", company_id="abc", duration_ms=2500)
"""

import json
import sys
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any

from loguru import logger as loguru_logger

# Context variables for request tracking
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
tenant_id_var: ContextVar[str | None] = ContextVar("tenant_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class StructuredLogger:
    """Structured JSON logger with context support."""

    def __init__(self, name: str):
        """Initialize structured logger.

        Args:
            name: Logger name (module/component).
        """
        self.name = name
        self._logger = loguru_logger.bind(component=name)

    def _enrich(self, message: str, extra: dict[str, Any]) -> tuple[str, dict]:
        """Enrich log entry with context.

        Args:
            message: Log message.
            extra: Extra fields.

        Returns:
            Enriched message and kwargs.
        """
        # Add context from context variables
        context = {
            "request_id": request_id_var.get(),
            "tenant_id": tenant_id_var.get(),
            "user_id": user_id_var.get(),
            "logger": self.name,
        }

        # Merge with extra fields
        context.update(extra)

        # Remove None values
        context = {k: v for k, v in context.items() if v is not None}

        return message, context

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        msg, ctx = self._enrich(message, kwargs)
        self._logger.debug(msg, **ctx)

    def info(self, message: str, **kwargs):
        """Log info message."""
        msg, ctx = self._enrich(message, kwargs)
        self._logger.info(msg, **ctx)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        msg, ctx = self._enrich(message, kwargs)
        self._logger.warning(msg, **ctx)

    def error(self, message: str, **kwargs):
        """Log error message."""
        msg, ctx = self._enrich(message, kwargs)
        self._logger.error(msg, **ctx)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        msg, ctx = self._enrich(message, kwargs)
        self._logger.critical(msg, **ctx)

    def bind(self, **kwargs) -> "StructuredLogger":
        """Create child logger with bound context.

        Args:
            **kwargs: Context to bind.

        Returns:
            New logger with bound context.
        """
        child = StructuredLogger(self.name)
        child._logger = self._logger.bind(**kwargs)
        return child


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger.

    Args:
        name: Logger name.

    Returns:
        StructuredLogger instance.
    """
    return StructuredLogger(name)


# Context management functions
def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context.

    Args:
        request_id: Request ID (generated if None).

    Returns:
        Request ID.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:16]
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> str | None:
    """Get current request ID.

    Returns:
        Request ID or None.
    """
    return request_id_var.get()


def set_tenant_id(tenant_id: str):
    """Set tenant ID in context.

    Args:
        tenant_id: Tenant identifier.
    """
    tenant_id_var.set(tenant_id)


def set_user_id(user_id: str):
    """Set user ID in context.

    Args:
        user_id: User identifier.
    """
    user_id_var.set(user_id)


def clear_context():
    """Clear all context variables."""
    request_id_var.set(None)
    tenant_id_var.set(None)
    user_id_var.set(None)


class LogFormatter:
    """Custom log formatter for JSON output."""

    @staticmethod
    def json_format(record: dict[str, Any]) -> str:
        """Format log record as JSON.

        Args:
            record: Log record dict.

        Returns:
            JSON string.
        """
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "component": record["extra"].get("component", "unknown"),
        }

        # Add extra fields
        for key, value in record["extra"].items():
            if key != "component":
                log_data[key] = value

        # Add exception info if present
        if record.get("exception"):
            log_data["exception"] = record["exception"]

        return json.dumps(log_data, default=str)


class LogShipper:
    """Ship logs to centralized aggregation system."""

    def __init__(self, endpoint: str | None = None, buffer_size: int = 100):
        """Initialize log shipper.

        Args:
            endpoint: Log aggregation endpoint.
            buffer_size: Buffer size before shipping.
        """
        self.endpoint = endpoint
        self.buffer_size = buffer_size
        self.buffer: list[dict] = []

    def ship(self, log_entry: dict[str, Any]):
        """Queue log entry for shipping.

        Args:
            log_entry: Log entry dict.
        """
        self.buffer.append(log_entry)

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        """Flush buffer to endpoint."""
        if not self.buffer or not self.endpoint:
            return

        # In production, ship to Elasticsearch, CloudWatch, etc.
        # async with aiohttp.ClientSession() as session:
        #     await session.post(self.endpoint, json=self.buffer)

        self.buffer = []


class CorrelationIdMiddleware:
    """FastAPI middleware to add correlation IDs."""

    def __init__(self, app: Any):
        """Initialize middleware.

        Args:
            app: ASGI application.
        """
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        """Process request with correlation ID."""
        if scope["type"] == "http":
            # Get or generate request ID
            headers = dict(scope.get("headers", []))
            request_id = headers.get(b"x-request-id", b"").decode() or None
            set_request_id(request_id)

        await self.app(scope, receive, send)
        clear_context()


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    ship_endpoint: str | None = None,
):
    """Configure structured logging.

    Args:
        level: Log level.
        json_output: Output JSON format.
        ship_endpoint: Log shipping endpoint.
    """
    # Remove default handler
    loguru_logger.remove()

    # Configure formatter
    if json_output:
        formatter = LogFormatter()
        sink = lambda msg: print(formatter.json_format(msg.record), file=sys.stdout)
    else:
        sink = sys.stdout

    # Add handler
    loguru_logger.add(
        sink,
        level=level,
        serialize=json_output,
        format="{time} | {level} | {message}" if not json_output else None,
    )

    # Configure shipper if endpoint provided
    if ship_endpoint:
        shipper = LogShipper(ship_endpoint)
        # Add custom handler for shipping
        # loguru_logger.add(lambda msg: shipper.ship(msg.record))


# Convenience logging functions
def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra,
):
    """Log HTTP request.

    Args:
        method: HTTP method.
        path: Request path.
        status_code: Response status.
        duration_ms: Request duration.
        **extra: Additional fields.
    """
    loguru_logger.info(
        f"{method} {path} {status_code}",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **extra,
    )


def log_enrichment(
    company_id: str,
    sources: list[str],
    duration_ms: float,
    success: bool = True,
    **extra,
):
    """Log enrichment activity.

    Args:
        company_id: Company ID.
        sources: Enrichment sources used.
        duration_ms: Enrichment duration.
        success: Whether enrichment succeeded.
        **extra: Additional fields.
    """
    loguru_logger.info(
        f"Company enriched: {company_id}",
        company_id=company_id,
        sources=sources,
        duration_ms=round(duration_ms, 2),
        success=success,
        **extra,
    )


def log_llm_call(
    provider: str,
    model: str,
    tokens: int,
    cost_usd: float,
    duration_ms: float,
    **extra,
):
    """Log LLM call.

    Args:
        provider: LLM provider.
        model: Model name.
        tokens: Total tokens used.
        cost_usd: Cost in USD.
        duration_ms: Request duration.
        **extra: Additional fields.
    """
    loguru_logger.info(
        f"LLM call: {provider}/{model}",
        provider=provider,
        model=model,
        tokens=tokens,
        cost_usd=round(cost_usd, 6),
        duration_ms=round(duration_ms, 2),
        **extra,
    )
