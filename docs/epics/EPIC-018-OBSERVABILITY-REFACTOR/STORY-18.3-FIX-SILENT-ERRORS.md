# Story 18.3: Fix Silent Error Handling

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P0
> **Effort**: 2 story points
> **Dependencies**: Story 18.1 (Unify Logging), Story 18.2 (Context Propagation)

---

## Description

Eliminate all silent exception swallowing in the codebase. Every exception must be logged with full context before any recovery or fallback action. This story specifically targets the `ErrorLoggingMiddleware` and any other locations with `except Exception: pass` patterns.

### Current Broken State

```python
# api/middleware/logging.py - ErrorLoggingMiddleware
class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if response.status_code >= 400:
            try:
                # Attempt to read error details from response
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk

                # Parse error details
                error_data = json.loads(body)
                error_message = error_data.get("error", "Unknown error")

                # Log the error
                logger.warning(
                    f"Error response: {response.status_code}",
                    error=error_message,
                    path=request.url.path,
                )

                # Rebuild response (this is problematic but separate issue)
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )

            except Exception:
                pass  # ← SILENT FAILURE! Error details lost forever

        return response
```

**Problems:**
- Response body parsing errors are completely silent
- No indication that error logging failed
- Cannot debug why error details are missing
- Original exception context lost

Other locations with similar issues:
- `api/middleware/tenant.py`: `_lookup_tenant` catches Exception and returns None
- Various data pipeline locations with broad `except Exception` blocks

---

## Acceptance Criteria

- [ ] Zero `except Exception: pass` or `except: pass` patterns in production code
- [ ] All exception handlers log at minimum a warning with error details
- [ ] `ErrorLoggingMiddleware` logs parsing failures with context
- [ ] Response body consumption failures are visible in logs
- [ ] All broad `except Exception` blocks reviewed and either:
  - Changed to specific exception types
  - Logged with `logger.exception()` or `logger.error(..., exc_info=True)`
  - Documented with `# noqa: E722` and justification comment
- [ ] Audit complete codebase for silent error handling

---

## Implementation

### Step 1: Fix ErrorLoggingMiddleware

```python
# api/middleware/logging.py
class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log error responses with details."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if response.status_code >= 400:
            await self._log_error_response(request, response)

        return response

    async def _log_error_response(self, request: Request, response: Response):
        """Log error response details. All failures are logged, never silent."""
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            # Attempt to read error details from response
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            error_data = None
            error_message = "Unknown error"

            try:
                error_data = json.loads(body)
                error_message = error_data.get("error", error_data.get("message", "Unknown error"))
            except json.JSONDecodeError as e:
                # Log JSON parsing failure but don't fail the whole handler
                logger.warning(
                    "Error response body is not valid JSON",
                    request_id=request_id,
                    status_code=response.status_code,
                    body_preview=body[:200].decode('utf-8', errors='replace'),
                    json_error=str(e),
                )
                error_message = body.decode('utf-8', errors='replace')[:200]

            # Log the actual error
            log_level = logging.ERROR if response.status_code >= 500 else logging.WARNING
            logger.log(
                log_level,
                f"Error response: {response.status_code}",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                error=error_message,
                error_details=error_data,
            )

            # Rebuild response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except Exception as e:
            # CRITICAL: Never silent. Log everything we know.
            logger.exception(
                "Failed to log error response details",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                error_type=type(e).__name__,
                error=str(e),
            )
            # Still return original response - don't break the request
            return response
```

### Step 2: Fix Tenant Middleware

```python
# api/middleware/tenant.py
async def _lookup_tenant(self, api_key_hash: str) -> Optional[TenantRecord]:
    """Lookup tenant by API key hash."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(TenantRecord).where(TenantRecord.api_key_hash == api_key_hash)
            )
            return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        # Database errors should be visible
        logger.exception(
            "Database error looking up tenant",
            api_key_prefix=api_key_hash[:8],
            error_type=type(e).__name__,
        )
        raise  # Re-raise to trigger 500, don't silently return None
    except Exception as e:
        # Unexpected errors - log and re-raise
        logger.exception(
            "Unexpected error looking up tenant",
            api_key_prefix=api_key_hash[:8],
            error_type=type(e).__name__,
        )
        raise
```

### Step 3: Create Silent Error Audit Script

```python
# scripts/audit_silent_errors.py
"""Audit codebase for silent exception handling."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class SilentExceptionVisitor(ast.NodeVisitor):
    """Find silent exception handlers."""

    def __init__(self):
        self.silent_handlers: List[Tuple[int, str]] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Check for bare 'except:' or 'except Exception:'
        is_broad = (
            node.type is None  # bare except
            or (
                isinstance(node.type, ast.Name)
                and node.type.id == "Exception"
            )
            or (
                isinstance(node.type, ast.Tuple)
                and any(
                    isinstance(elt, ast.Name) and elt.id == "Exception"
                    for elt in node.type.elts
                )
            )
        )

        if is_broad:
            # Check if body is empty, pass, or just returns None
            body = node.body
            is_silent = (
                len(body) == 0
                or (len(body) == 1 and isinstance(body[0], ast.Pass))
                or (len(body) == 1
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and body[0].value.value is None)
                or (len(body) == 1
                    and isinstance(body[0], ast.Return)
                    and (body[0].value is None
                         or (isinstance(body[0].value, ast.Constant)
                             and body[0].value.value is None)))
            )

            if is_silent:
                self.silent_handlers.append((node.lineno, "silent"))
            else:
                # Check if there's any logging in the handler
                has_logging = any(
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and stmt.value.func.attr in ("debug", "info", "warning", "error", "exception", "critical")
                    for stmt in body
                )
                if not has_logging:
                    self.silent_handlers.append((node.lineno, "no-log"))

        self.generic_visit(node)


def audit_file(filepath: Path) -> List[Tuple[int, str]]:
    """Audit a single file for silent exception handling."""
    try:
        tree = ast.parse(filepath.read_text())
    except SyntaxError:
        return []

    visitor = SilentExceptionVisitor()
    visitor.visit(tree)
    return visitor.silent_handlers


def main():
    """Run audit on src directory."""
    src_dir = Path("src/solstein")
    issues = []

    for py_file in src_dir.rglob("*.py"):
        if "test" in py_file.name:
            continue

        findings = audit_file(py_file)
        for lineno, issue_type in findings:
            issues.append((py_file, lineno, issue_type))

    if issues:
        print(f"Found {len(issues)} potential silent exception handlers:")
        print()
        for filepath, lineno, issue_type in issues:
            print(f"  {filepath}:{lineno} ({issue_type})")
        print()
        print("Fix these by adding proper logging or using specific exceptions.")
        sys.exit(1)
    else:
        print("✓ No silent exception handlers found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

### Step 4: Guidelines for Exception Handling

Create `docs/exception-handling-guide.md`:

```markdown
# Exception Handling Guidelines

## Forbidden Patterns

```python
# ❌ NEVER: Silent exception swallowing
try:
    do_something()
except Exception:
    pass

# ❌ NEVER: Silent return
try:
    do_something()
except Exception:
    return None

# ❌ NEVER: Comment-only handler
try:
    do_something()
except Exception as e:
    # TODO: handle this
    pass
```

## Required Patterns

```python
# ✅ ALWAYS: Log with context before recovery
try:
    do_something()
except SpecificError as e:
    logger.warning(
        "Operation failed, using fallback",
        error=str(e),
        context=value,
    )
    return fallback_value

# ✅ ALWAYS: Use logger.exception for unexpected errors
try:
    do_something()
except Exception as e:
    logger.exception("Unexpected error in operation")
    raise  # Re-raise if you can't handle it

# ✅ ALWAYS: Preserve exception chain
try:
    do_something()
except LowerLevelError as e:
    raise HigherLevelError("Context") from e
```

## Decision Tree

1. **Can you handle this specific exception?**
   - Yes → Catch specific type, log at appropriate level, handle
   - No → Let it propagate

2. **Is this a boundary (API, task, worker)?**
   - Yes → Catch broad exception, log with `logger.exception()`, return error response
   - No → Catch specific exceptions only

3. **Is this a graceful degradation case?**
   - Yes → Log warning with context, return fallback
   - No → Log error and re-raise
```

---

## Testing

```python
# tests/unit/test_middleware/test_error_logging.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from starlette.responses import Response
from solstein.api.middleware.logging import ErrorLoggingMiddleware


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"
    request.state.request_id = "test-req-123"
    return request


@pytest.mark.asyncio
async def test_error_logging_middleware_logs_json_error(mock_request):
    """Test that JSON errors in error responses are logged."""
    middleware = ErrorLoggingMiddleware(app=MagicMock())

    # Create response with JSON error
    error_response = Response(
        content=b'{"error": "Test error", "code": "TEST_001"}',
        status_code=400,
        headers={"content-type": "application/json"},
    )

    with patch("solstein.api.middleware.logging.logger") as mock_logger:
        call_next = AsyncMock(return_value=error_response)

        # Need to mock body_iterator for async iteration
        async def mock_iterator():
            yield b'{"error": "Test error", "code": "TEST_001"}'
        error_response.body_iterator = mock_iterator()

        response = await middleware.dispatch(mock_request, call_next)

        assert response.status_code == 400
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert "Test error" in str(call_args)


@pytest.mark.asyncio
async def test_error_logging_middleware_logs_json_parse_failure(mock_request):
    """Test that JSON parse failures are logged, not silent."""
    middleware = ErrorLoggingMiddleware(app=MagicMock())

    # Create response with invalid JSON
    error_response = Response(
        content=b'not valid json',
        status_code=500,
    )

    with patch("solstein.api.middleware.logging.logger") as mock_logger:
        call_next = AsyncMock(return_value=error_response)

        async def mock_iterator():
            yield b'not valid json'
        error_response.body_iterator = mock_iterator()

        response = await middleware.dispatch(mock_request, call_next)

        # Should log the JSON parse failure
        mock_logger.warning.assert_called()
        log_calls = [str(c) for c in mock_logger.warning.call_args_list]
        assert any("not valid JSON" in c for c in log_calls)


@pytest.mark.asyncio
async def test_error_logging_middleware_logs_handler_failure(mock_request):
    """Test that handler failures are logged, not silent."""
    middleware = ErrorLoggingMiddleware(app=MagicMock())

    error_response = Response(
        content=b'test',
        status_code=400,
    )

    with patch("solstein.api.middleware.logging.logger") as mock_logger:
        call_next = AsyncMock(return_value=error_response)

        # Simulate body iterator raising exception
        async def failing_iterator():
            raise IOError("Stream closed")
            yield b''
        error_response.body_iterator = failing_iterator()

        response = await middleware.dispatch(mock_request, call_next)

        # Should log the handler failure
        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args
        assert "Failed to log error response" in str(call_args)
```

---

## Verification Steps

1. **Run audit script:**
   ```bash
   python scripts/audit_silent_errors.py
   ```
   Expected: "✓ No silent exception handlers found!"

2. **Manual grep check:**
   ```bash
   grep -rn "except.*:" src/solstein --include="*.py" | grep -v "test" | grep -v "logger"
   ```
   Review any matches

3. **Integration test:**
   ```python
   # Trigger an error response with malformed JSON
   # Verify logs show both the error and the parsing failure
   ```

---

## Related Files

- `src/solstein/api/middleware/logging.py` - ErrorLoggingMiddleware
- `src/solstein/api/middleware/tenant.py` - Tenant lookup
- `scripts/audit_silent_errors.py` - Audit script (new)
- `docs/exception-handling-guide.md` - Guidelines (new)
