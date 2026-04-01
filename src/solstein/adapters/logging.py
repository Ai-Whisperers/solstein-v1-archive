"""Structured logging helpers for adapter exception handlers.

STORY-130: Provides a consistent structured logging function for all adapter
exception handlers, emitting the required fields per exception-handling.md:
component, operation, error_type, message, entity_id.
"""

from __future__ import annotations

from loguru import logger


def log_adapter_error(
    *,
    component: str,
    operation: str,
    error: Exception,
    entity_id: str | None = None,
    entity_name: str | None = None,
    level: str = "error",
) -> None:
    """Log an adapter exception with structured fields.

    Args:
        component: Adapter class name (e.g. "WebSearchUnifiedSource").
        operation: Method that failed (e.g. "enrich", "discover", "fetch_facts").
        error: The caught exception.
        entity_id: Company ID or other entity identifier.
        entity_name: Human-readable entity name (company name).
        level: Log level — "error" for unexpected failures, "warning" for
               expected/recoverable ones (e.g. missing API key, empty results).
    """
    error_type = type(error).__name__
    log_fn = getattr(logger, level, logger.error)
    log_fn(
        f"[{component}] {operation} failed: {error}",
        component=component,
        operation=operation,
        error_type=error_type,
        message=str(error),
        entity_id=entity_id or "unknown",
        entity_name=entity_name or "unknown",
    )
