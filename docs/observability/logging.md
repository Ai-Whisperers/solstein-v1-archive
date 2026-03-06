# Observability Logging Guide

This guide explains how to use the unified logging system in Solstein.

## Overview

Solstein uses **Loguru** as its unified logging framework. All logs automatically include:
- Timestamp
- Log level
- Source file, function, and line number
- Request context (request_id, correlation_id, tenant_id, user_id)

## Quick Start

### Basic Logging

```python
from loguru import logger

# Simple logging
logger.info("Processing company", company_id="COMP-123")
logger.debug("Debug info", detail="some value")
logger.warning("Something might be wrong")
logger.error("Something went wrong")
logger.exception("Critical error with stack trace")
```

### Logging with Context

```python
# Bind context that appears in all subsequent logs
logger.bind(company_id="COMP-123", user_id="user-456").info("Starting process")

# The context persists for this logger instance
logger.info("Step 1")  # Will include company_id and user_id
logger.info("Step 2")  # Will include company_id and user_id
```

### Request-Scoped Context (Automatic)

When processing HTTP requests, context is automatically set:

```python
# In your API handler
@app.get("/companies/{company_id}")
async def get_company(company_id: str, request: Request):
    # Context is automatically set by ContextMiddleware:
    # - request_id
    # - correlation_id
    # - tenant_id (if authenticated)
    # - user_id (if authenticated)

    # All logs automatically include this context:
    logger.info("Fetching company")  # Includes request_id, etc.

    # You can add more context:
    logger.bind(company_id=company_id).debug("Querying database")
```

## Configuration

### Development (Pretty Format)

```python
from solstein.utils.logging import setup_logging

setup_logging(
    level="DEBUG",
    json_format=False,  # Pretty, colored output
)
```

Output:
```
2024-03-05 10:23:45.123 | INFO     | api.routers.companies:get_company:42 | request_id=abc123 | correlation_id=xyz789 | - Fetching company
```

### Production (JSON Format)

```python
setup_logging(
    level="INFO",
    json_format=True,   # Structured JSON for log aggregation
    log_file="/var/log/solstein/app.log",
    rotation="500 MB",
    retention="30 days",
)
```

Output:
```json
{
  "timestamp": "2024-03-05T10:23:45.123456",
  "level": "INFO",
  "message": "Fetching company",
  "source": {"file": "...", "function": "get_company", "line": 42},
  "context": {
    "request_id": "abc123",
    "correlation_id": "xyz789",
    "tenant_id": "tenant-1"
  }
}
```

## Best Practices

### 1. Use Structured Logging

❌ **Don't:**
```python
logger.info(f"Processing company {company_id} for user {user_id}")
```

✅ **Do:**
```python
logger.info("Processing company", company_id=company_id, user_id=user_id)
```

### 2. Log at Appropriate Levels

| Level | Use When |
|-------|----------|
| DEBUG | Detailed information for debugging |
| INFO | General operational information |
| WARNING | Something unexpected but handled |
| ERROR | Something failed, action needed |
| CRITICAL | System-wide failure |

### 3. Include Context

```python
# Good: Context helps trace the request
logger.bind(
    company_id=company.id,
    operation="enrichment",
    source="companies_house"
).info("Enriching company data")
```

### 4. Handle Exceptions Properly

❌ **Don't:**
```python
try:
    process_data()
except Exception:
    pass  # Silent failure!
```

✅ **Do:**
```python
try:
    process_data()
except Exception as e:
    logger.exception("Failed to process data", company_id=company.id)
    raise  # Re-raise or handle appropriately
```

### 5. Use exception() for Errors

```python
try:
    risky_operation()
except Exception as e:
    # Automatically includes stack trace
    logger.exception("Operation failed", error=str(e))
```

## Context Propagation

### HTTP Requests

Context is automatically set by `ContextMiddleware`:

```python
# All logs in request handlers automatically include:
# - request_id: Short unique ID for the request
# - correlation_id: For distributed tracing
# - tenant_id: From X-API-Key (if authenticated)
# - user_id: From authentication (if available)
```

### Celery Tasks

Context automatically propagates from web request to Celery task:

```python
# In API handler
@app.post("/companies/{id}/enrich")
async def enrich_company(id: str):
    logger.info("Queueing enrichment")  # Has request_id
    enrich_task.delay(company_id=id)    # Context propagates!

# In Celery task
@celery_app.task
def enrich_task(company_id: str):
    logger.info("Starting enrichment")  # Same request_id!
    # Context from original request is preserved
```

## Environment Variables

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# JSON format for production
LOG_JSON_FORMAT=true

# Log file path (optional)
LOG_FILE=/var/log/solstein/app.log

# Log rotation size
LOG_ROTATION=500 MB

# Log retention period
LOG_RETENTION=30 days
```

## Troubleshooting

### Logs Missing Context

If request context (request_id, etc.) is missing:

1. Ensure `ContextMiddleware` is registered in `main.py`:
   ```python
   from solstein.api.middleware import ContextMiddleware
   app.add_middleware(ContextMiddleware)
   ```

2. For non-request contexts (background jobs), set context manually:
   ```python
   from solstein.utils.context import set_context, reset_context

   tokens = set_context(request_id="manual-123")
   try:
       do_work()
   finally:
       reset_context(tokens)
   ```

### Stdlib Logging Not Working

If you see `import logging` code that isn't logging:

1. Ensure `setup_logging()` was called
2. Stdlib logs are intercepted and routed to Loguru automatically

### Too Much Log Output

In production, set appropriate level:

```bash
LOG_LEVEL=INFO  # Only INFO and above
```

Or use JSON filtering:

```bash
# Filter with jq
cat app.log | jq 'select(.level == "ERROR")'
```

## Migration from Stdlib Logging

If you have old code using stdlib logging:

```python
# BEFORE
import logging
logger = logging.getLogger(__name__)
logger.info("Message", extra={"key": "value"})

# AFTER
from loguru import logger
logger.bind(key="value").info("Message")
```

## Related Documentation

- [Error Handling](./error-handling.md) - Exception taxonomy and handling
- [Tracing](./tracing.md) - Dependency tracing and metrics
- [Debugging Runbook](../runbooks/debugging.md) - Troubleshooting guide
