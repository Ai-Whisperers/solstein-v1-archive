# Story 18.4: Secure Error Responses

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P0
> **Effort**: 2 story points
> **Dependencies**: Story 18.1 (Unify Logging)

---

## Description

Prevent stack traces and internal implementation details from being exposed to API clients. The global exception handler currently returns full tracebacks in all environments. Implement environment-aware error responses that log full details server-side while returning safe, generic messages to clients.

### Current Broken State

```python
# api/exceptions.py
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - CURRENTLY EXPOSES INTERNALS!"""
    import traceback

    request_id = getattr(request.state, "request_id", str(uuid.uuid4())[:8])

    logger.exception(
        "Unhandled exception",
        request_id=request_id,
        path=request.url.path,
        error_type=type(exc).__name__,
    )

    # ← SECURITY ISSUE: Returns traceback to client unconditionally
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
            },
            "request_id": request_id,
            "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),  # ← EXPOSED!
        },
        headers={"X-Request-ID": request_id},
    )
```

**Security Risks:**
- File paths exposed (reveals deployment structure)
- Database queries visible in tracebacks
- Environment variables might leak through exception messages
- Internal library versions revealed
- Attack surface information disclosure

---

## Acceptance Criteria

- [ ] Stack traces NEVER returned to clients in production (`ENVIRONMENT=production`)
- [ ] Stack traces optionally available in development with explicit opt-in
- [ ] All error responses follow consistent schema: `{error: {code, message}, request_id}`
- [ ] Full error details (including traceback) always logged server-side
- [ ] `traceback` field removed from production responses entirely (not just empty)
- [ ] Documentation updated with security guidelines for error handling
- [ ] Security review of all error response paths

---

## Implementation

### Step 1: Update Configuration

```python
# config/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    environment: str = Field(default="development", description="Environment name")
    debug_errors: bool = Field(default=False, description="Include debug info in error responses")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ("production", "prod")

    @property
    def expose_error_details(self) -> bool:
        """Whether to expose error details in responses."""
        return self.debug_errors and not self.is_production


# Usage
from solstein.config import settings

if settings.expose_error_details:
    # Only in development with explicit opt-in
    response["traceback"] = traceback.format_exception(...)
```

### Step 2: Secure Exception Handlers

```python
# api/exceptions.py
import traceback
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from loguru import logger
from ..config import settings


class APIError(StarletteHTTPException):
    """Custom API error with structured response."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


def _get_request_id(request: Request) -> str:
    """Extract request ID from request state or generate new."""
    return getattr(request.state, "request_id", str(uuid.uuid4())[:8])


def _log_error(
    request: Request,
    exc: Exception,
    request_id: str,
    level: str = "error",
) -> None:
    """Log error with full context server-side.

    This is where ALL error details go - never in the response.
    """
    log_data = {
        "request_id": request_id,
        "correlation_id": getattr(request.state, "correlation_id", None),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "user_id": getattr(request.state, "user_id", None),
        "path": request.url.path,
        "method": request.method,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
    }

    if level == "error":
        logger.error("Error processing request", **log_data)
    elif level == "exception":
        logger.exception("Unhandled exception", **log_data)
    elif level == "warning":
        logger.warning("Warning in request", **log_data)


def _create_error_response(
    code: str,
    message: str,
    request_id: str,
    status_code: int = 500,
    details: dict | None = None,
    exc: Exception | None = None,
) -> JSONResponse:
    """Create secure error response.

    Never includes internal details unless explicitly in debug mode.
    """
    response = {
        "error": {
            "code": code,
            "message": message,
        },
        "request_id": request_id,
    }

    # Only include safe details (not internal implementation)
    if details:
        # Filter details to only include safe fields
        safe_details = _filter_safe_details(details)
        if safe_details:
            response["error"]["details"] = safe_details

    # ONLY include debug info in non-production with explicit opt-in
    if settings.expose_error_details and exc:
        response["debug"] = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
        }

    return JSONResponse(
        status_code=status_code,
        content=response,
        headers={"X-Request-ID": request_id},
    )


def _filter_safe_details(details: dict) -> dict:
    """Filter error details to remove potentially sensitive info.

    Safe fields: field names, validation types, general metadata
    Unsafe fields: SQL queries, file paths, internal IDs, tokens
    """
    unsafe_keys = {
        "query", "sql", "statement", "path", "file", "filename",
        "password", "token", "secret", "key", "auth", "credential",
        "connection_string", "host", "port", "internal_id",
    }

    safe = {}
    for key, value in details.items():
        key_lower = key.lower()
        if any(unsafe in key_lower for unsafe in unsafe_keys):
            # Replace unsafe values with placeholder
            safe[key] = "[REDACTED]"
        elif isinstance(value, dict):
            # Recursively filter nested dicts
            nested = _filter_safe_details(value)
            if nested:
                safe[key] = nested
        elif isinstance(value, (str, int, float, bool, list)):
            safe[key] = value

    return safe


# ===== Exception Handlers =====

async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors."""
    request_id = _get_request_id(request)

    level = "error" if exc.status_code >= 500 else "warning"
    _log_error(request, exc, request_id, level)

    return _create_error_response(
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    request_id = _get_request_id(request)

    # Simplify validation errors (remove internal details)
    simplified_errors = []
    for error in exc.errors():
        simplified = {
            "field": ".".join(str(x) for x in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "unknown"),
        }
        simplified_errors.append(simplified)

    logger.warning(
        "Validation error",
        request_id=request_id,
        errors=simplified_errors,
    )

    return _create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        request_id=request_id,
        status_code=422,
        details={"errors": simplified_errors},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    request_id = _get_request_id(request)

    # Map status codes to error codes
    status_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        501: "NOT_IMPLEMENTED",
        503: "SERVICE_UNAVAILABLE",
    }
    code = status_code_map.get(exc.status_code, "HTTP_ERROR")

    level = "error" if exc.status_code >= 500 else "warning"
    _log_error(request, exc, request_id, level)

    return _create_error_response(
        code=code,
        message=exc.detail or "An error occurred",
        request_id=request_id,
        status_code=exc.status_code,
    )


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions - SECURE!"""
    request_id = _get_request_id(request)

    # Log EVERYTHING server-side (this is secure, internal)
    _log_error(request, exc, request_id, "exception")

    # Return SAFE response to client
    return _create_error_response(
        code="INTERNAL_ERROR",
        message="An internal error occurred. Please try again later.",
        request_id=request_id,
        status_code=500,
        # Note: exc is NOT passed - no debug info in production
    )


def setup_exception_handlers(app):
    """Register all exception handlers with the app."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
```

### Step 3: Environment Configuration

```bash
# .env.development
ENVIRONMENT=development
DEBUG_ERRORS=true

# .env.production
ENVIRONMENT=production
DEBUG_ERRORS=false

# .env.staging
ENVIRONMENT=staging
DEBUG_ERRORS=false
```

### Step 4: Security Review Checklist

Create `docs/security/error-response-security.md`:

```markdown
# Error Response Security Checklist

## Pre-Deployment Verification

- [ ] `ENVIRONMENT=production` in production config
- [ ] `DEBUG_ERRORS=false` in production config
- [ ] No `traceback` field in any production error response
- [ ] No file paths in error responses
- [ ] No SQL queries in error responses
- [ ] No internal IDs in error responses
- [ ] All 500 errors logged with full details server-side

## Testing Commands

```bash
# Test production error response (should NOT include traceback)
ENVIRONMENT=production DEBUG_ERRORS=false python -c "
from fastapi.testclient import TestClient
from solstein.api.main import app
client = TestClient(app)
# Trigger a 500 error
response = client.get('/trigger-error')
assert 'traceback' not in response.json()
assert 'debug' not in response.json()
print('✓ Production error responses are secure')
"

# Test development error response (should include debug when enabled)
ENVIRONMENT=development DEBUG_ERRORS=true python -c "
# Same test but assert debug info IS present
"
```

## Response Schema

### Production Response
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal error occurred. Please try again later."
  },
  "request_id": "abc123"
}
```

### Development Response (DEBUG_ERRORS=true)
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal error occurred. Please try again later."
  },
  "request_id": "abc123",
  "debug": {
    "error_type": "ValueError",
    "error_message": "Invalid input",
    "traceback": ["..."]
  }
}
```
```

---

## Testing

```python
# tests/unit/test_exceptions.py
import pytest
from fastapi import Request
from unittest.mock import MagicMock, patch
from starlette.exceptions import HTTPException as StarletteHTTPException
from solstein.api.exceptions import (
    global_exception_handler,
    api_error_handler,
    validation_exception_handler,
    APIError,
)
from solstein.config import settings


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    request.url.path = "/test"
    request.method = "GET"
    request.state.request_id = "test-req-123"
    request.state.correlation_id = "test-corr-456"
    return request


@pytest.mark.asyncio
async def test_global_handler_no_traceback_in_production(mock_request):
    """Test that production responses don't include tracebacks."""
    with patch.object(settings, 'is_production', True):
        with patch.object(settings, 'expose_error_details', False):
            exc = ValueError("Test internal error")

            response = await global_exception_handler(mock_request, exc)

            body = response.body.decode()
            assert "traceback" not in body.lower()
            assert "debug" not in body.lower()
            assert "INTERNAL_ERROR" in body
            assert "test-req-123" in body  # request_id should be present


@pytest.mark.asyncio
async def test_global_handler_includes_debug_when_enabled(mock_request):
    """Test that debug info is included when explicitly enabled."""
    with patch.object(settings, 'is_production', False):
        with patch.object(settings, 'expose_error_details', True):
            exc = ValueError("Test internal error")

            response = await global_exception_handler(mock_request, exc)

            body = response.body.decode()
            assert "debug" in body.lower()
            assert "traceback" in body.lower()
            assert "ValueError" in body


@pytest.mark.asyncio
async def test_sensitive_details_redacted(mock_request):
    """Test that sensitive details are redacted."""
    with patch.object(settings, 'is_production', True):
        exc = APIError(
            code="VALIDATION_ERROR",
            message="Invalid input",
            status_code=400,
            details={
                "field": "username",
                "password": "secret123",  # Should be redacted
                "query": "SELECT * FROM users",  # Should be redacted
                "file": "/app/internal/module.py",  # Should be redacted
            },
        )

        response = await api_error_handler(mock_request, exc)

        body = response.body.decode()
        assert "username" in body  # Safe field present
        assert "secret123" not in body  # Password redacted
        assert "[REDACTED]" in body  # Redaction marker present
        assert "SELECT" not in body  # SQL redacted


@pytest.mark.asyncio
async def test_all_errors_logged_server_side(mock_request):
    """Test that all error details are logged server-side."""
    with patch("solstein.api.exceptions.logger") as mock_logger:
        exc = ValueError("Test error with details")

        await global_exception_handler(mock_request, exc)

        mock_logger.error.assert_called_once()
        call_kwargs = mock_logger.error.call_args.kwargs
        assert "traceback" in call_kwargs
        assert "error_type" in call_kwargs
        assert call_kwargs["error_type"] == "ValueError"
```

---

## Verification Steps

1. **Test production response:**
   ```bash
   ENVIRONMENT=production pytest tests/unit/test_exceptions.py -v
   ```

2. **Manual curl test:**
   ```bash
   # Trigger an error endpoint
   curl -s http://localhost:8000/api/v1/trigger-error | jq .

   # Verify: should have error.code, error.message, request_id
   # Verify: should NOT have traceback, debug, file paths, SQL
   ```

3. **Check server logs:**
   ```bash
   # Should see full traceback in logs
   tail -f logs/app.log | grep "Unhandled exception"
   ```

4. **Security scan:**
   ```bash
   grep -rn "traceback" src/solstein/api --include="*.py" | grep -v test
   # Verify tracebacks are only in exception handlers, never in responses
   ```

---

## Related Files

- `src/solstein/api/exceptions.py` - Main exception handlers
- `src/solstein/config/settings.py` - Environment configuration
- `docs/security/error-response-security.md` - Security guidelines (new)
