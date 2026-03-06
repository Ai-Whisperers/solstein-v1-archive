# Dependency Tracing Guide

This guide explains how to use dependency tracing to monitor outbound calls to databases, LLMs, and external APIs.

## Overview

Solstein provides **automatic dependency tracing** that tracks:
- Call latency (timing)
- Success/failure rates
- Error types
- Request context propagation

## Quick Start

### Tracing a Dependency Call

```python
from solstein.utils.tracing import get_tracer

tracer = get_tracer()

async with tracer.trace("postgresql", "query", table="companies"):
    result = await db.execute(query)
```

This automatically:
- Logs the call start
- Measures duration
- Logs completion (or failure)
- Records metrics

### Adding Metadata

```python
async with tracer.trace("openai", "generate", model="gpt-4") as span:
    span["prompt_tokens"] = 100
    response = await openai.generate(prompt)
    span["completion_tokens"] = response["usage"]["completion_tokens"]
```

## Supported Dependencies

### Database Queries

```python
from solstein.utils.tracing import get_tracer

tracer = get_tracer()

async with tracer.trace("postgresql", "select", table="companies"):
    company = await db.get_company(company_id)
```

### LLM Calls

```python
async with tracer.trace("openai", "chat_completion", model="gpt-4"):
    response = await client.chat.completions.create(...)
```

### External APIs

```python
async with tracer.trace("crunchbase", "get_company", company_id=company_id):
    data = await crunchbase_client.get_company(company_id)
```

## Viewing Metrics

### All Dependencies

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://api.solstein.com/metrics/dependencies
```

Response:
```json
{
  "postgresql": {
    "total_calls": 1523,
    "error_count": 12,
    "error_rate": 0.0079,
    "latency_ms": {
      "p50": 15.2,
      "p95": 45.8,
      "p99": 89.3,
      "avg": 18.5,
      "max": 120.4
    }
  },
  "openai": {
    "total_calls": 456,
    "error_count": 3,
    "error_rate": 0.0066,
    "latency_ms": {
      "p50": 850.3,
      "p95": 2340.1,
      "p99": 4120.5,
      "avg": 923.7,
      "max": 5234.2
    }
  }
}
```

### Specific Service

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://api.solstein.com/metrics/dependencies/openai
```

## Log Output

### Successful Call

```json
{
  "timestamp": "2024-03-05T10:23:45.123456",
  "level": "DEBUG",
  "message": "Dependency call started: openai.generate",
  "service": "openai",
  "operation": "generate",
  "context": {
    "request_id": "abc123",
    "correlation_id": "xyz789"
  }
}
```

### Failed Call

```json
{
  "timestamp": "2024-03-05T10:23:46.456789",
  "level": "ERROR",
  "message": "Dependency call completed: openai.generate",
  "service": "openai",
  "operation": "generate",
  "duration_ms": 1333.33,
  "success": false,
  "error_type": "TimeoutError",
  "context": {
    "request_id": "abc123",
    "correlation_id": "xyz789"
  }
}
```

## Alerting

### High Error Rate

Alert when error rate exceeds threshold:

```yaml
alert: HighDependencyErrorRate
expr: |
  solstein_dependency_error_rate > 0.05  # 5% error rate
for: 5m
labels:
  severity: warning
annotations:
  summary: "High error rate for {{ $labels.service }}"
```

### High Latency

Alert when latency exceeds threshold:

```yaml
alert: HighDependencyLatency
expr: |
  solstein_dependency_latency_p95 > 2000  # 2 seconds
for: 5m
labels:
  severity: warning
annotations:
  summary: "High latency for {{ $labels.service }}"
```

## Best Practices

### 1. Use Descriptive Names

```python
# Good - clear what we're tracing
async with tracer.trace("postgresql", "select", table="companies"):
    ...

# Bad - vague
async with tracer.trace("db", "op"):
    ...
```

### 2. Include Relevant Metadata

```python
async with tracer.trace("openai", "generate") as span:
    span["model"] = "gpt-4"
    span["prompt_tokens"] = len(prompt.split())
    # ... call LLM ...
    span["completion_tokens"] = response.usage.completion_tokens
```

### 3. Handle Errors Properly

```python
try:
    async with tracer.trace("api", "call"):
        result = await api.call()
except Exception:
    # Tracer automatically records failure
    # Re-raise for upstream handling
    raise
```

### 4. Don't Trace Everything

Trace:
- External API calls
- Database queries
- LLM calls
- Expensive operations

Don't trace:
- Fast in-memory operations
- Simple data transformations
- Cached lookups (if logged elsewhere)

## Troubleshooting

### Metrics Not Appearing

Check if tracing is configured:

```python
from solstein.utils.tracing import get_tracer
tracer = get_tracer()
print(len(tracer._calls))  # Should increase after traced calls
```

### Context Missing in Logs

Ensure context is set before tracing:

```python
from solstein.utils.context import set_context, reset_context

tokens = set_context(request_id="test-123")
try:
    async with tracer.trace("db", "query"):
        # Context will be in logs
        ...
finally:
    reset_context(tokens)
```

### Metrics Endpoint Returns Empty

- Ensure admin authentication
- Check that traced calls have been made
- Metrics are stored in memory (not persistent)

## Performance Considerations

### Overhead

Tracing adds minimal overhead:
- ~0.5µs per context operation
- ~1-2µs for logging
- Negligible for I/O-bound operations (DB, API calls)

### Memory Usage

Metrics stored in memory with a limit:
- Default: 10,000 recent calls
- Oldest calls dropped when limit reached
- ~1KB per call (metadata + timing)

### Resetting Metrics

Clear metrics (useful for testing):

```bash
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://api.solstein.com/metrics/dependencies/reset
```

## Related Documentation

- [Logging](./logging.md) - Structured logging
- [Error Handling](./error-handling.md) - Exception taxonomy
- [Debugging Runbook](../runbooks/debugging.md) - Troubleshooting
