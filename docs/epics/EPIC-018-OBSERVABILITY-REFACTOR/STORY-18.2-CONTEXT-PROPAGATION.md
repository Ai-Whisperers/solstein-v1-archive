# Story 18.2: Implement Context Propagation

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P0
> **Effort**: 3 story points
> **Dependencies**: Story 18.1 (Unify Logging)
> **Related**: Story 18.3, Story 18.6

---

## Description

Implement request-scoped context propagation using `contextvars` to ensure `request_id`, `correlation_id`, `tenant_id`, and `user_id` are automatically included in all logs throughout a request's lifecycle, including async task boundaries (Celery).

### Current Broken State

```python
# api/middleware/logging.py
class RequestIDMiddleware:
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.scope["request_id"] = request_id  # Only in scope, not logs!
        # ...

# api/middleware/tracing.py
class RequestTracingMiddleware:
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        with logger.contextualize(correlation_id=correlation_id):
            # Only THIS block has context
            response = await call_next(request)
        # Context lost after this block!
```

**Problems:**
- Context lost when exiting `contextualize` block
- Celery tasks have no access to request context
- No automatic inclusion in all log calls
- Tenant/user info not propagated
- Context doesn't survive async boundaries properly

---

## Acceptance Criteria

- [ ] `contextvars` used for request-scoped context (request_id, correlation_id, tenant_id, user_id)
- [ ] Context automatically included in ALL log entries without manual `.bind()`
- [ ] Context propagates to Celery tasks via task headers
- [ ] Context extracted from headers on task execution
- [ ] Context cleared properly after request/task completion (prevent leaks)
- [ ] `X-Request-ID` and `X-Correlation-ID` headers work consistently
- [ ] Helper functions provided: `get_current_context()`, `set_context()`, `clear_context()`

---

## Implementation

### Step 1: Create `utils/context.py`

```python
"""Request-scoped context propagation using contextvars."""

import contextvars
from typing import Any
from functools import wraps
from uuid import uuid4

# Context variables for request-scoped data
REQUEST_ID: contextvars.ContextVar[str] = contextvars.ContextVar('request_id')
CORRELATION_ID: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id')
TENANT_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar('tenant_id', default=None)
USER_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar('user_id', default=None)
OPERATION: contextvars.ContextVar[str | None] = contextvars.ContextVar('operation', default=None)

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
```

### Step 2: Update `utils/logging.py` to Auto-Include Context

```python
import sys
import logging
from typing import Any
from loguru import logger
from .context import get_current_context

# ... InterceptHandler stays the same ...

def format_record(record: dict[str, Any]) -> str:
    """Format log record with automatic context inclusion."""
    base_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    )

    # Auto-include contextvars context
    context = get_current_context()
    if context:
        context_str = " | ".join(f"<magenta>{k}</magenta>=<yellow>{v}</yellow>"
                                 for k, v in context.items())
        base_format += " | " + context_str

    # Add any explicit extra fields (excluding context keys)
    extra = record.get("extra", {})
    extra_fields = {k: v for k, v in extra.items()
                   if k not in context and k not in ("correlation_id", "request_id")}
    if extra_fields:
        extra_str = " | ".join(f"<magenta>{k}</magenta>=<yellow>{v}</yellow>"
                               for k, v in extra_fields.items())
        base_format += " | " + extra_str

    base_format += " - <level>{message}</level>\n{exception}"
    return base_format


def format_record_json(record: dict[str, Any]) -> dict[str, Any]:
    """Format record for JSON output with context."""
    # Start with standard fields
    output = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "source": {
            "file": record["file"].path,
            "function": record["function"],
            "line": record["line"],
        },
    }

    # Add automatic context
    context = get_current_context()
    if context:
        output["context"] = context

    # Add extra fields
    extra = record.get("extra", {})
    if extra:
        output["extra"] = {k: v for k, v in extra.items()
                          if k not in context}

    # Add exception info
    if record["exception"]:
        output["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback,
        }

    return output
```

### Step 3: Update Middleware to Use Contextvars

```python
# api/middleware/context.py (new file)
"""Middleware for setting request context."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from ...utils.context import (
    set_context, reset_context, generate_request_id, generate_correlation_id
)


class ContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request-scoped context for logging."""

    async def dispatch(self, request: Request, call_next):
        # Extract or generate IDs
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()

        # Extract tenant/user from request (customize based on your auth)
        tenant_id = getattr(request.state, "tenant_id", None)
        user_id = getattr(request.state, "user_id", None)

        # Set context
        tokens = set_context(
            request_id=request_id,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            operation=f"{request.method}_{request.url.path}",
        )

        # Store in request for handlers
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        try:
            logger.debug("Request started", method=request.method, path=request.url.path)
            response = await call_next(request)

            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            logger.debug("Request completed", status_code=response.status_code)
            return response

        except Exception as e:
            logger.exception("Request failed")
            raise
        finally:
            # ALWAYS reset context to prevent leaks
            reset_context(tokens)


# Update api/middleware/__init__.py to export
from .context import ContextMiddleware
```

### Step 4: Celery Context Propagation

```python
# celery_context.py (new file in src/solstein/)
"""Celery task context propagation."""

from celery import Task
from celery.signals import before_task_publish, task_prerun, task_postrun
from .utils.context import set_context, reset_context, get_current_context


@before_task_publish.connect
def add_context_to_task_headers(headers=None, body=None, **kwargs):
    """Add current context to task headers before publishing."""
    context = get_current_context()
    if context:
        headers["_context"] = context


@task_prerun.connect
def restore_context_from_headers(task_id=None, task=None, kwargs=None, **other):
    """Restore context from task headers when task starts."""
    # Access request context from task request
    request = task.request
    context = getattr(request, "headers", {}).get("_context", {})

    if context:
        # Store tokens on task instance for cleanup
        task._context_tokens = set_context(**context)


@task_postrun.connect
def clear_task_context(task=None, **kwargs):
    """Clear context after task completes."""
    tokens = getattr(task, "_context_tokens", [])
    if tokens:
        reset_context(tokens)
        task._context_tokens = []
```

### Step 5: Update Celery Config

```python
# celery_config.py
from celery import Celery
from .celery_context import add_context_to_task_headers, restore_context_from_headers, clear_task_context

# Import signals to register them
from . import celery_context  # noqa

app = Celery('solstein')
# ... existing config ...
```

---

## Testing

```python
# tests/unit/test_context.py
import pytest
import asyncio
from solstein.utils.context import (
    set_context, reset_context, get_current_context,
    REQUEST_ID, CORRELATION_ID, clear_context
)

@pytest.fixture
def clean_context():
    """Ensure clean context for each test."""
    clear_context()
    yield
    clear_context()


def test_set_and_get_context(clean_context):
    """Test setting and retrieving context."""
    tokens = set_context(
        request_id="req-123",
        correlation_id="corr-456",
        tenant_id="tenant-abc",
    )

    context = get_current_context()
    assert context["request_id"] == "req-123"
    assert context["correlation_id"] == "corr-456"
    assert context["tenant_id"] == "tenant-abc"

    reset_context(tokens)


def test_context_isolation(clean_context):
    """Test that context is isolated between scopes."""
    import contextvars

    async def task1():
        set_context(request_id="task1")
        await asyncio.sleep(0.01)
        return get_current_context()["request_id"]

    async def task2():
        set_context(request_id="task2")
        await asyncio.sleep(0.01)
        return get_current_context()["request_id"]

    async def main():
        result1, result2 = await asyncio.gather(task1(), task2())
        assert result1 == "task1"
        assert result2 == "task2"

    asyncio.run(main())


def test_reset_clears_context(clean_context):
    """Test that reset properly clears context."""
    tokens = set_context(request_id="test-123")
    assert "request_id" in get_current_context()

    reset_context(tokens)
    assert "request_id" not in get_current_context()
```

---

## Integration Example

```python
# In a FastAPI handler
from fastapi import Request
from loguru import logger

@app.get("/companies/{company_id}")
async def get_company(company_id: str, request: Request):
    # Context is automatically set by middleware
    # No need for manual .bind() - request_id, correlation_id already in logs

    logger.info("Fetching company", company_id=company_id)
    # Log output: 2024-... | INFO | api.routers.companies:get_company:42 |
    #             request_id=abc123 | correlation_id=xyz789 | tenant_id=org1 |
    #             - Fetching company | company_id=COMP-123

    company = await fetch_company(company_id)

    # In async service calls, context is preserved
    await some_service.process(company)  # Logs still have context!

    return company
```

---

## Verification Steps

1. **Test context isolation:**
   ```python
   # Concurrent requests should have independent context
   async def test_concurrent():
       await asyncio.gather(
           make_request(headers={"X-Request-ID": "req1"}),
           make_request(headers={"X-Request-ID": "req2"}),
       )
   # Verify logs show correct request_id for each
   ```

2. **Test Celery propagation:**
   ```python
   # In request handler
   logger.info("Before celery", request_id="abc")
   my_task.delay()

   # In task
   @app.task
   def my_task():
       logger.info("In task")
       # Should show same request_id from parent
   ```

3. **Test context cleanup:**
   ```python
   # Make request
   # Check that context is cleared (no leak to next request)
   ```

---

## Related Files

- `src/solstein/utils/context.py` (new)
- `src/solstein/utils/logging.py` - Update format_record
- `src/solstein/api/middleware/context.py` (new)
- `src/solstein/celery_context.py` (new)
- `src/solstein/celery_config.py` - Import signals
