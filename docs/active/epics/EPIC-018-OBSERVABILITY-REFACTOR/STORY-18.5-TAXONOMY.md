# Story 18.5: Standardize Exception Taxonomy

> **Epic**: EPIC-018 Observability and Error Handling Refactor
> **Priority**: P1
> **Effort**: 2 story points
> **Dependencies**: Story 18.4 (Secure Responses)

---

## Description

Consolidate the fragmented exception hierarchy into a clean, minimal taxonomy (6-10 exception types) that maps clearly to HTTP status codes and provides actionable error context. Currently, exceptions are scattered across modules with inconsistent inheritance and HTTP mapping.

### Current Broken State

```python
# exceptions.py - Base exceptions (mostly empty)
class SolsteinError(Exception):
    """Base exception for Solstein."""
    pass

class DataLoadError(SolsteinError):
    """Error loading data."""
    pass

class ValidationError(SolsteinError):
    """Validation error."""
    pass

# llm/structured_client.py - Custom exception
class StructuredOutputError(Exception):
    def __init__(self, message: str, raw_output: str = None):
        super().__init__(message)
        self.raw_output = raw_output

# llm/enhanced_client.py - Different custom exception
class LLMGenerationError(Exception):
    pass

# data/enrichment_config.py - Yet another
class ConfigError(Exception):
    pass

# config.py - Same name, different module
class ConfigurationError(SolsteinError):
    pass

# infrastructure/research_dual_write.py
class ContradictionLifecycleError(Exception):
    def __init__(self, code: str, message: str, allowed_transitions: list = None):
        self.code = code
        self.message = message
        self.allowed_transitions = allowed_transitions
```

**Problems:**
- Same conceptual errors have different exception types
- HTTP mapping inconsistent (some have it, some don't)
- Error codes scattered (some use strings, some don't)
- No clear hierarchy: domain vs infrastructure vs presentation
- New developers don't know which exception to raise

---

## Acceptance Criteria

- [ ] Exception taxonomy reduced to 6-10 well-defined types
- [ ] All exceptions inherit from single base with consistent interface
- [ ] Each exception type maps to specific HTTP status code
- [ ] Each exception includes `code`, `message`, and optional `details`
- [ ] All scattered custom exceptions migrated to taxonomy
- [ ] Documentation of when to use each exception type
- [ ] Migration guide for updating existing code

---

## Proposed Taxonomy

```
SolsteinError (base)
├── DomainError (400)          # Business logic violations
│   └── ValidationError (400)  # Input validation failures
├── StateError (409)           # Invalid state transitions
├── NotFoundError (404)        # Resource not found
├── ConflictError (409)        # Resource conflicts
├── PermissionError (403)      # Authorization failures
├── AuthenticationError (401)  # Authentication failures
├── InfrastructureError (500)  # Internal service failures
│   ├── DatabaseError (500)    # Database failures
│   ├── LLMError (502)         # LLM provider failures
│   └── ExternalServiceError (502)  # Third-party service failures
└── ConfigurationError (500)   # Invalid configuration
```

### Exception Interface

```python
class SolsteinError(Exception):
    """Base exception with structured error information.

    Attributes:
        code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code for API responses
        details: Additional structured error context
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }
```

---

## Implementation

### Step 1: Create New Exception Hierarchy

```python
# exceptions.py (completely rewritten)
"""Standardized exception taxonomy for Solstein.

This module defines a minimal, consistent exception hierarchy
that maps cleanly to HTTP status codes and provides structured
error information for logging and API responses.

Usage:
    # Raise with just message
    raise NotFoundError("Company not found")

    # Raise with additional context
    raise ValidationError(
        "Invalid revenue value",
        details={"field": "revenue", "value": -100, "constraint": "must be positive"}
    )

    # Catch and convert to HTTP response
    try:
        process_data(data)
    except SolsteinError as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.to_dict()}
        )
"""

from typing import Any


class SolsteinError(Exception):
    """Base exception for all Solstein errors.

    Provides structured error information for:
    - Machine-readable error codes
    - HTTP status code mapping
    - Structured details for debugging
    - Conversion to API response format

    Attributes:
        code: Machine-readable error code (e.g., "NOT_FOUND")
        message: Human-readable error description
        status_code: HTTP status code (e.g., 404)
        details: Optional structured error context
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or {}

    def __str__(self) -> str:
        base = f"[{self.code}] {self.message}"
        if self.details:
            base += f" | details={self.details}"
        return base

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code='{self.code}', "
            f"message='{self.message}', "
            f"status_code={self.status_code}"
            f")"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result

    def with_details(self, **kwargs) -> "SolsteinError":
        """Return new exception with additional details."""
        new_details = {**self.details, **kwargs}
        return self.__class__(
            self.message,
            code=self.code,
            status_code=self.status_code,
            details=new_details,
        )


# ===== Domain Errors (4xx client errors) =====

class DomainError(SolsteinError):
    """Business logic violation.

    Use when: Input violates business rules (not just format).
    Example: Cannot classify company with insufficient data.
    HTTP: 400 Bad Request
    """
    code = "DOMAIN_ERROR"
    status_code = 400


class ValidationError(DomainError):
    """Input validation failure.

    Use when: Input format, type, or constraint violation.
    Example: Negative revenue, invalid date format.
    HTTP: 400 Bad Request
    """
    code = "VALIDATION_ERROR"
    status_code = 400


class NotFoundError(SolsteinError):
    """Resource not found.

    Use when: Requested resource doesn't exist.
    Example: Company ID not in database.
    HTTP: 404 Not Found
    """
    code = "NOT_FOUND"
    status_code = 404

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        *,
        details: dict[str, Any] | None = None,
    ):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, details=details)
        self.details["resource_type"] = resource_type
        self.details["resource_id"] = resource_id


class StateError(SolsteinError):
    """Invalid state for operation.

    Use when: Operation not allowed in current state.
    Example: Cannot transition from COMPLETED to PENDING.
    HTTP: 409 Conflict
    """
    code = "STATE_ERROR"
    status_code = 409


class ConflictError(SolsteinError):
    """Resource conflict.

    Use when: Resource already exists or conflicts with another.
    Example: Duplicate company ID, concurrent modification.
    HTTP: 409 Conflict
    """
    code = "CONFLICT"
    status_code = 409


class PermissionError(SolsteinError):
    """Permission denied.

    Use when: User lacks permission for action.
    Example: Cannot access another tenant's data.
    HTTP: 403 Forbidden
    """
    code = "PERMISSION_DENIED"
    status_code = 403


class AuthenticationError(SolsteinError):
    """Authentication failure.

    Use when: Invalid or missing credentials.
    Example: Invalid API key, expired token.
    HTTP: 401 Unauthorized
    """
    code = "AUTHENTICATION_FAILED"
    status_code = 401


class RateLimitError(SolsteinError):
    """Rate limit exceeded.

    Use when: Too many requests from client.
    HTTP: 429 Too Many Requests
    """
    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if retry_after:
            self.details["retry_after"] = retry_after


# ===== Infrastructure Errors (5xx server errors) =====

class InfrastructureError(SolsteinError):
    """Internal infrastructure failure.

    Use when: Service cannot fulfill request due to internal issue.
    Example: Database unavailable, service timeout.
    HTTP: 500 Internal Server Error
    """
    code = "INFRASTRUCTURE_ERROR"
    status_code = 500


class DatabaseError(InfrastructureError):
    """Database operation failure.

    Use when: Database query/connection fails.
    HTTP: 500 Internal Server Error
    """
    code = "DATABASE_ERROR"
    status_code = 500


class LLMError(InfrastructureError):
    """LLM provider failure.

    Use when: LLM call fails or returns invalid response.
    HTTP: 502 Bad Gateway (external service failure)
    """
    code = "LLM_ERROR"
    status_code = 502

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if provider:
            self.details["provider"] = provider
        if model:
            self.details["model"] = model


class ExternalServiceError(InfrastructureError):
    """External service failure.

    Use when: Third-party API call fails.
    HTTP: 502 Bad Gateway
    """
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502

    def __init__(
        self,
        message: str,
        *,
        service: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, details=details)
        if service:
            self.details["service"] = service


class ConfigurationError(InfrastructureError):
    """Invalid configuration.

    Use when: Service configuration is invalid or missing.
    HTTP: 500 Internal Server Error
    """
    code = "CONFIGURATION_ERROR"
    status_code = 500
```

### Step 2: Migration Guide

```python
# MIGRATION_GUIDE.md

## Migrating to New Exception Taxonomy

### Old → New Mapping

```python
# BEFORE (exceptions.py)
raise DataLoadError("Failed to load company data")

# AFTER
raise InfrastructureError(
    "Failed to load company data",
    details={"operation": "load_company", "company_id": company_id}
)


# BEFORE (llm/structured_client.py)
raise StructuredOutputError("Invalid JSON from LLM", raw_output=text)

# AFTER
raise LLMError(
    "Invalid JSON from LLM",
    provider="openai",
    model="gpt-4",
    details={"raw_output": text[:500]}  # Truncate for safety
)


# BEFORE (llm/enhanced_client.py)
raise LLMGenerationError("LLM call failed")

# AFTER
raise LLMError(
    "LLM call failed",
    provider=provider_name,
    details={"error_type": "timeout"}
)


# BEFORE (data/enrichment_config.py)
raise ConfigError("Missing API key")

# AFTER
raise ConfigurationError(
    "Missing API key",
    details={"config_key": "ENRICHMENT_API_KEY"}
)


# BEFORE (infrastructure/research_dual_write.py)
raise ContradictionLifecycleError(
    code="INVALID_TRANSITION",
    message=f"Cannot transition from {from_state} to {to_state}",
    allowed_transitions=valid
)

# AFTER
raise StateError(
    f"Cannot transition from {from_state} to {to_state}",
    details={
        "from_state": from_state,
        "to_state": to_state,
        "allowed_transitions": valid,
    }
)
```

### Module-by-Module Migration

1. **exceptions.py**: Replace entire file with new taxonomy
2. **llm/**: Replace StructuredOutputError, LLMGenerationError with LLMError
3. **data/**: Replace ConfigError with ConfigurationError
4. **infrastructure/**: Replace ContradictionLifecycleError with StateError
5. **config.py**: Keep ConfigurationError, ensure it extends new base
6. **database_config.py**: Replace DatabaseURLError with ConfigurationError

### HTTP Handler Updates

```python
# api/exceptions.py
from ..exceptions import SolsteinError, ValidationError, NotFoundError, ...

async def solstein_error_handler(request: Request, exc: SolsteinError):
    """Handle all Solstein exceptions uniformly."""
    request_id = _get_request_id(request)

    logger.error(
        "Request failed",
        request_id=request_id,
        error_code=exc.code,
        error_message=exc.message,
        details=exc.details,
    )

    return _create_error_response(
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        status_code=exc.status_code,
        details=exc.details,
    )

# Register single handler for all SolsteinError subclasses
def setup_exception_handlers(app):
    app.add_exception_handler(SolsteinError, solstein_error_handler)
    # ... other handlers for non-Solstein exceptions
```
```

---

## Testing

```python
# tests/unit/test_exceptions.py
import pytest
from solstein.exceptions import (
    SolsteinError,
    ValidationError,
    NotFoundError,
    StateError,
    LLMError,
)


def test_base_exception_interface():
    """Test SolsteinError base interface."""
    exc = SolsteinError("Test message", code="TEST_CODE", status_code=418)

    assert exc.message == "Test message"
    assert exc.code == "TEST_CODE"
    assert exc.status_code == 418
    assert str(exc) == "[TEST_CODE] Test message"
    assert "TEST_CODE" in repr(exc)


def test_exception_to_dict():
    """Test to_dict method."""
    exc = ValidationError(
        "Invalid field",
        details={"field": "revenue", "constraint": "positive"}
    )

    data = exc.to_dict()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid field"
    assert data["details"]["field"] == "revenue"


def test_not_found_error_constructor():
    """Test NotFoundError convenience constructor."""
    exc = NotFoundError("Company", "COMP-123")

    assert "Company not found: COMP-123" in exc.message
    assert exc.details["resource_type"] == "Company"
    assert exc.details["resource_id"] == "COMP-123"
    assert exc.status_code == 404


def test_exception_with_details():
    """Test with_details helper."""
    exc = ValidationError("Invalid input", details={"field": "name"})
    enhanced = exc.with_details(reason="too_short", min_length=3)

    assert enhanced.details["field"] == "name"  # Original preserved
    assert enhanced.details["reason"] == "too_short"
    assert enhanced.details["min_length"] == 3


def test_llm_error_with_provider():
    """Test LLMError with provider info."""
    exc = LLMError("API timeout", provider="openai", model="gpt-4")

    assert exc.details["provider"] == "openai"
    assert exc.details["model"] == "gpt-4"
    assert exc.status_code == 502


def test_exception_inheritance():
    """Test exception hierarchy."""
    assert issubclass(ValidationError, SolsteinError)
    assert issubclass(ValidationError, SolsteinError)
    assert issubclass(NotFoundError, SolsteinError)
    assert issubclass(LLMError, InfrastructureError)
    assert issubclass(InfrastructureError, SolsteinError)
```

---

## Verification Steps

1. **Check all exceptions inherit from SolsteinError:**
   ```bash
   grep -rn "class.*Error" src/solstein --include="*.py" | grep -v test
   # Verify all extend SolsteinError
   ```

2. **Verify HTTP mapping:**
   ```python
   for exc_class in [ValidationError, NotFoundError, StateError, ...]:
       print(f"{exc_class.__name__}: {exc_class.status_code}")
   ```

3. **Test exception handler:**
   ```python
   # Raise each exception type
   # Verify correct HTTP status returned
   ```

4. **Check no old exceptions remain:**
   ```bash
   grep -rn "StructuredOutputError\|LLMGenerationError\|ContradictionLifecycleError" src/solstein
   # Should return no results after migration
   ```

---

## Related Files

- `src/solstein/exceptions.py` - New exception hierarchy
- `src/solstein/api/exceptions.py` - HTTP handler integration
- `src/solstein/llm/*` - LLM exceptions to migrate
- `src/solstein/data/*` - Data exceptions to migrate
- `src/solstein/infrastructure/*` - Infrastructure exceptions to migrate
