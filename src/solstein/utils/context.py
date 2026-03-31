"""Request-scoped context propagation using contextvars.

This module provides request-scoped context variables for tracking
request_id, correlation_id, tenant_id, and user_id across async boundaries.
"""

import asyncio
import contextvars
from functools import wraps
from typing import Any
from uuid import uuid4

# Context variables for request-scoped data
REQUEST_ID: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")
CORRELATION_ID: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id")
TENANT_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("tenant_id", default=None)
USER_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
OPERATION: contextvars.ContextVar[str | None] = contextvars.ContextVar("operation", default=None)

# All context variables for iteration
CONTEXT_VARS = [REQUEST_ID, CORRELATION_ID, TENANT_ID, USER_ID, OPERATION]


def get_current_context() -> dict[str, Any]:
    """Get current context as dictionary.

    Returns:
        Dictionary with all context values that are set.
    """
    context = {}
    for var in CONTEXT_VARS:
        try:
            value = var.get()
            if value is not None:
                context[var.name] = value
        except LookupError:
            pass  # Variable not set
    return context


def set_context(
    request_id: str | None = None,
    correlation_id: str | None = None,
    tenant_id: str | None = None,
    user_id: str | None = None,
    operation: str | None = None,
) -> list[contextvars.Token]:
    """Set context variables. Returns tokens for reset.

    Args:
        request_id: Unique request identifier
        correlation_id: Correlation ID (for distributed tracing)
        tenant_id: Tenant/organization identifier
        user_id: User identifier
        operation: Operation name for grouping

    Returns:
        List of tokens to reset context later
    """
    tokens = []

    if request_id:
        tokens.append(REQUEST_ID.set(request_id))
    if correlation_id:
        tokens.append(CORRELATION_ID.set(correlation_id))
    if tenant_id:
        tokens.append(TENANT_ID.set(tenant_id))
    if user_id:
        tokens.append(USER_ID.set(user_id))
    if operation:
        tokens.append(OPERATION.set(operation))

    return tokens


def reset_context(tokens: list[contextvars.Token]) -> None:
    """Reset context variables using tokens from set_context."""
    for token in tokens:
        token.var.reset(token)


def clear_context() -> None:
    """Clear all context variables. Use with caution - prefer reset_context."""
    for var in CONTEXT_VARS:
        try:
            var.set(None)  # type: ignore
        except LookupError:
            pass


def generate_request_id() -> str:
    """Generate a short unique request ID."""
    return str(uuid4())[:8]


def generate_correlation_id() -> str:
    """Generate a full UUID for correlation."""
    return str(uuid4())


# Decorator for setting context
def with_context(operation: str | None = None):
    """Decorator to set operation context for a function."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                tokens = []
                if operation:
                    tokens = set_context(operation=operation)
                try:
                    return await func(*args, **kwargs)
                finally:
                    if tokens:
                        reset_context(tokens)
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                tokens = []
                if operation:
                    tokens = set_context(operation=operation)
                try:
                    return func(*args, **kwargs)
                finally:
                    if tokens:
                        reset_context(tokens)
            return wrapper

    return decorator
