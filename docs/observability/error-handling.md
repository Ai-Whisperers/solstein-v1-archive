# Error Handling Guide

This guide explains Solstein's standardized exception taxonomy and error handling patterns.

## Overview

Solstein uses a **unified exception taxonomy** that provides:
- Consistent HTTP status code mapping
- Structured error information
- Backwards compatibility
- Clear semantic meaning

## Exception Hierarchy

```
SolsteinError (base)
├── DomainError (400)          # Business logic violations
│   └── ValidationError (400)  # Input validation failures
├── NotFoundError (404)        # Resource not found
├── StateError (409)           # Invalid state transitions
├── ConflictError (409)        # Resource conflicts
├── PermissionError (403)      # Authorization failures
├── AuthenticationError (401)  # Authentication failures
├── RateLimitError (429)       # Rate limit exceeded
└── InfrastructureError (500)  # Internal service failures
    ├── DatabaseError (500)    # Database failures
    ├── LLMError (502)         # LLM provider failures
    └── ExternalServiceError (502)  # Third-party service failures
```

## When to Use Each Exception

### DomainError (400 Bad Request)

Use when input violates business rules (not just format).

```python
from solstein.exceptions import DomainError

if not has_sufficient_data(company):
    raise DomainError(
        "Cannot classify company: insufficient data",
        details={
            "required_fields": ["revenue", "employees"],
            "missing_fields": missing,
        }
    )
```

### ValidationError (400 Bad Request)

Use for input format, type, or constraint violations.

```python
from solstein.exceptions import ValidationError

if revenue < 0:
    raise ValidationError(
        "Revenue must be positive",
        details={"field": "revenue", "value": revenue, "constraint": ">= 0"}
    )
```

### NotFoundError (404 Not Found)

Use when requested resource doesn't exist.

```python
from solstein.exceptions import NotFoundError

company = await get_company(company_id)
if not company:
    raise NotFoundError("Company", company_id)
# Automatically sets message: "Company not found: COMP-123"
```

### StateError (409 Conflict)

Use when operation not allowed in current state.

```python
from solstein.exceptions import StateError

if current_state == "COMPLETED" and new_state == "PENDING":
    raise StateError(
        f"Cannot transition from {current_state} to {new_state}",
        details={
            "from_state": current_state,
            "to_state": new_state,
            "allowed_transitions": ["ARCHIVED"],
        }
    )
```

### LLMError (502 Bad Gateway)

Use when LLM call fails or returns invalid response.

```python
from solstein.exceptions import LLMError

try:
    response = await openai.generate(prompt)
except TimeoutError as e:
    raise LLMError(
        "LLM request timeout",
        provider="openai",
        model="gpt-4",
        details={"timeout_seconds": 30}
    ) from e
```

## Exception Interface

All exceptions provide:

```python
exc.code          # Machine-readable error code (e.g., "NOT_FOUND")
exc.message       # Human-readable description
exc.status_code   # HTTP status code (e.g., 404)
exc.details       # Optional structured context

# Convert to API response
exc.to_dict()
# Returns: {"code": "...", "message": "...", "details": {...}}

# Add more details
new_exc = exc.with_details(additional_key="value")
```

## Error Handling Patterns

### Pattern 1: Catch Specific Exceptions

```python
from solstein.exceptions import NotFoundError, ValidationError

@app.get("/companies/{company_id}")
async def get_company(company_id: str):
    try:
        return await fetch_company(company_id)
    except NotFoundError:
        # Let the exception handler convert to 404 response
        raise
    except ValidationError as e:
        # Log and re-raise
        logger.warning("Invalid company ID format", error=str(e))
        raise
```

### Pattern 2: Catch Base Exception

```python
from solstein.exceptions import SolsteinError

@app.get("/companies/{company_id}")
async def get_company(company_id: str):
    try:
        return await fetch_company(company_id)
    except SolsteinError:
        # Our exceptions - let handlers deal with them
        raise
    except Exception as e:
        # Unexpected error - wrap it
        logger.exception("Unexpected error fetching company")
        raise InfrastructureError("Failed to fetch company") from e
```

### Pattern 3: Service Layer Error Translation

```python
# In service layer
async def enrich_company(company_id: str):
    try:
        data = await external_api.fetch(company_id)
    except httpx.TimeoutError as e:
        # Translate to our taxonomy
        raise ExternalServiceError(
            "External API timeout",
            service="enrichment_api",
        ) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise NotFoundError("Company", company_id) from e
        raise ExternalServiceError(
            "External API error",
            service="enrichment_api",
            details={"status_code": e.response.status_code}
        ) from e
```

## HTTP Response Format

All errors return consistent JSON:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Company not found: COMP-123",
    "details": {
      "resource_type": "Company",
      "resource_id": "COMP-123"
    }
  },
  "request_id": "abc123"
}
```

## Security

### Never Expose Internals

❌ **Don't:**
```python
raise Exception(f"Database query failed: {sql_query}")
# Exposes SQL in error message!
```

✅ **Do:**
```python
raise DatabaseError("Database query failed")
# Log SQL server-side only
```

### Stack Traces

Stack traces are **never** exposed in production error responses.

- Production: Generic error message
- Development: Debug info only when `DEBUG_ERRORS=true`

See [API Exceptions](../../src/solstein/api/exceptions.py) for implementation.

## Backwards Compatibility

Old exception names are aliased to new taxonomy:

| Old Name | New Name |
|----------|----------|
| `DataLoadError` | `InfrastructureError` |
| `ScoringError` | `DomainError` |
| `ExportError` | `InfrastructureError` |
| `LLMAvailabilityError` | `LLMError` |

Code using old names continues to work.

## Testing

### Testing Exception Responses

```python
async def test_not_found_returns_404(client):
    response = await client.get("/companies/INVALID")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data
```

### Testing Exception Details

```python
def test_validation_error_details():
    exc = ValidationError(
        "Invalid input",
        details={"field": "email", "constraint": "valid email"}
    )
    data = exc.to_dict()
    assert data["details"]["field"] == "email"
```

## Troubleshooting

### Exception Not Converting to HTTP Response

Ensure exception handler is registered in `main.py`:

```python
from solstein.api.exceptions import setup_exception_handlers

app = FastAPI()
setup_exception_handlers(app)  # Must be called!
```

### Wrong HTTP Status Code

Check exception class:

```python
exc = MyException("test")
print(exc.status_code)  # Should be correct HTTP code
```

### Details Not in Response

Ensure details are serializable:

```python
# Good - JSON serializable
raise ValidationError("Error", details={"count": 42, "name": "test"})

# Bad - includes non-serializable objects
raise ValidationError("Error", details={"obj": some_custom_object})
```

## Related Documentation

- [Logging](./logging.md) - Structured logging with context
- [Tracing](./tracing.md) - Dependency tracing and metrics
- [Debugging Runbook](../runbooks/debugging.md) - Troubleshooting errors
