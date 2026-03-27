"""Tenant isolation enforcement for Celery background tasks.

STORY-066: Ensures every background job carries and validates a tenant_id,
preventing cross-tenant data access in async operations.

Usage:
    @celery_app.task(bind=True)
    def my_task(self, tenant_id: str, company_id: str):
        validate_task_tenant_id(tenant_id)
        with task_tenant_context(tenant_id):
            # All operations scoped to tenant
            ...
"""

from __future__ import annotations

import functools
from contextlib import contextmanager
from typing import Any, Callable, TypeVar

from loguru import logger

from solstein.utils.context import set_context, reset_context

F = TypeVar("F", bound=Callable[..., Any])


class TenantIsolationError(Exception):
    """Raised when a background task violates tenant isolation rules."""

    def __init__(self, message: str, *, task_name: str | None = None, tenant_id: str | None = None):
        super().__init__(message)
        self.task_name = task_name
        self.tenant_id = tenant_id


def validate_task_tenant_id(tenant_id: str | None, *, task_name: str = "unknown") -> str:
    """Validate that a tenant_id is present and well-formed for a background task.

    Args:
        tenant_id: The tenant identifier to validate.
        task_name: Name of the task for error context.

    Returns:
        The validated tenant_id.

    Raises:
        TenantIsolationError: If tenant_id is missing or invalid.
    """
    if tenant_id is None:
        logger.error(
            f"[TenantIsolation] Task '{task_name}' called without tenant_id"
        )
        raise TenantIsolationError(
            f"Task '{task_name}' requires tenant_id but received None",
            task_name=task_name,
            tenant_id=None,
        )

    if not isinstance(tenant_id, str):  # type: ignore[redundant-isinstance]
        logger.error(
            f"[TenantIsolation] Task '{task_name}' received non-string tenant_id: {type(tenant_id)}"
        )
        raise TenantIsolationError(
            f"Task '{task_name}' requires string tenant_id, got {type(tenant_id).__name__}",
            task_name=task_name,
            tenant_id=str(tenant_id),
        )

    stripped = tenant_id.strip()
    if not stripped:
        logger.error(
            f"[TenantIsolation] Task '{task_name}' received empty tenant_id"
        )
        raise TenantIsolationError(
            f"Task '{task_name}' requires non-empty tenant_id",
            task_name=task_name,
            tenant_id=tenant_id,
        )

    return stripped


@contextmanager
def task_tenant_context(tenant_id: str):
    """Set the tenant context for the duration of a task execution.

    This sets the TENANT_ID context variable so that downstream code
    (repositories, queries) can access it without explicit parameter passing.

    Args:
        tenant_id: Validated tenant identifier.

    Yields:
        The tenant_id for convenience.
    """
    tokens = set_context(tenant_id=tenant_id)
    logger.debug(f"[TenantIsolation] Entered task tenant context: {tenant_id[:8]}...")
    try:
        yield tenant_id
    finally:
        reset_context(tokens)
        logger.debug(f"[TenantIsolation] Exited task tenant context: {tenant_id[:8]}...")


def require_tenant_id(func: F) -> F:
    """Decorator that enforces tenant_id as the first positional arg after self.

    For use with Celery tasks (bind=True). The decorated function must accept
    tenant_id as its first argument after self.

    Validates tenant_id at entry and sets the tenant context for the
    duration of the task.

    Example:
        @celery_app.task(bind=True)
        @require_tenant_id
        def my_task(self, tenant_id: str, company_id: str):
            # tenant_id is validated and context is set
            ...
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # For bind=True tasks, args[0] is self (the Task instance)
        # args[1] is tenant_id
        if len(args) >= 2:
            tenant_id = args[1]
        elif "tenant_id" in kwargs:
            tenant_id = kwargs["tenant_id"]
        else:
            task_name = getattr(func, "__name__", "unknown")
            raise TenantIsolationError(
                f"Task '{task_name}' called without tenant_id argument",
                task_name=task_name,
            )

        task_name = getattr(func, "__name__", "unknown")
        validated_id = validate_task_tenant_id(tenant_id, task_name=task_name)

        # Replace tenant_id with validated version in args
        if len(args) >= 2:
            args = (args[0], validated_id, *args[2:])
        else:
            kwargs["tenant_id"] = validated_id

        with task_tenant_context(validated_id):
            return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
