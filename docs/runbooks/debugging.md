# Debugging Runbook

This runbook provides step-by-step procedures for debugging issues in Solstein using the observability tools.

## Prerequisites

Ensure you have:
- Access to application logs
- Request ID from error response or logs
- Admin access (for metrics endpoints)

## Quick Reference

### Finding Logs by Request ID

```bash
# JSON logs (production)
cat /var/log/solstein/app.log | jq 'select(.context.request_id == "abc123")'

# Pretty logs (development)
grep "abc123" /var/log/solstein/app.log
```

### Checking Error Rate

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/metrics/dependencies
```

## Common Scenarios

### Scenario 1: API Returns 500 Error

**Symptom**: Client receives `{"error": {"code": "INTERNAL_ERROR", ...}}`

**Steps**:

1. **Get the request_id** from the error response:
   ```json
   {
     "error": {"code": "INTERNAL_ERROR", "message": "..."},
     "request_id": "abc123"  <-- This!
   }
   ```

2. **Find the error in logs**:
   ```bash
   cat app.log | jq 'select(.context.request_id == "abc123")'
   ```

3. **Look for exception details**:
   - Server-side logs will have full traceback
   - Check `error_type` and `error_message` fields
   - Look at preceding log lines for context

4. **Check dependency health**:
   ```bash
   curl http://localhost:8000/metrics/dependencies
   ```
   - High error rate for a service indicates external issue
   - High latency explains timeout errors

5. **Common causes**:
   - Database connection issue → Check `postgresql` metrics
   - LLM timeout → Check `openai` or other LLM metrics
   - External API down → Check `crunchbase`, etc.

---

### Scenario 2: Request is Slow

**Symptom**: API takes >5 seconds to respond

**Steps**:

1. **Get request_id** from response headers:
   ```bash
   curl -v http://api/endpoint 2>&1 | grep X-Request-ID
   # X-Request-ID: abc123
   ```

2. **Find duration in logs**:
   ```bash
   cat app.log | jq 'select(.context.request_id == "abc123" and .message | contains("RESPONSE"))'
   ```
   Look for `duration_ms` field.

3. **Check dependency latencies**:
   ```bash
   curl http://localhost:8000/metrics/dependencies | jq '.[].latency_ms.p95'
   ```

4. **Identify slow dependency**:
   - High `p95` latency indicates slow service
   - Check logs for that service during the request

5. **Optimization options**:
   - Add caching for slow dependencies
   - Increase timeout thresholds
   - Implement circuit breaker

---

### Scenario 3: Missing Data After Enrichment

**Symptom**: Company enrichment appeared to succeed but data is missing

**Steps**:

1. **Find enrichment request**:
   ```bash
   cat app.log | jq 'select(.message | contains("enrichment"))'
   ```

2. **Look for silent failures**:
   ```bash
   cat app.log | jq 'select(.level == "WARNING" and .message | contains("suppressed"))'
   ```

3. **Check individual source errors**:
   - Each enrichment source logs separately
   - Look for source-specific errors

4. **Check dependency metrics**:
   ```bash
   curl http://localhost:8000/metrics/dependencies/crunchbase
   curl http://localhost:8000/metrics/dependencies/linkedin
   ```

5. **Common causes**:
   - External API rate limit (check error rate)
   - API key expired (check authentication errors)
   - Schema change in external API (check validation errors)

---

### Scenario 4: Celery Task Failing Silently

**Symptom**: Task queued but no result, no error visible

**Steps**:

1. **Find task in logs**:
   ```bash
   cat app.log | jq 'select(.message | contains("task"))'
   ```

2. **Check context propagation**:
   - Worker logs should have same `request_id` as web request
   - If missing, Celery context propagation not working

3. **Check worker logs for errors**:
   ```bash
   # On worker host
   journalctl -u solstein-worker -f
   ```

4. **Common causes**:
   - Worker not running → Start worker
   - Redis connection issue → Check Redis health
   - Serialization error → Check task arguments

---

### Scenario 5: Memory Leak

**Symptom**: Memory usage grows over time

**Steps**:

1. **Check for unclosed connections**:
   ```bash
   cat app.log | jq 'select(.message | contains("connection"))'
   ```

2. **Check dependency tracer memory**:
   - Tracer stores last 10,000 calls in memory
   - Normal growth, but shouldn't exceed ~10MB

3. **Profile memory usage**:
   ```python
   # In Python shell
   import tracemalloc
   tracemalloc.start()
   # ... run code ...
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')
   for stat in top_stats[:10]:
       print(stat)
   ```

---

## Log Analysis Tips

### Finding Errors in Time Range

```bash
# Last hour
cat app.log | jq 'select(.timestamp > "2024-03-05T09:00:00") | select(.level == "ERROR")'

# Specific time window
cat app.log | jq 'select(.timestamp >= "2024-03-05T09:00:00" and .timestamp <= "2024-03-05T10:00:00")'
```

### Aggregating Errors by Type

```bash
cat app.log | jq -r 'select(.level == "ERROR") | .error_type' | sort | uniq -c | sort -rn
```

### Finding Slow Requests

```bash
cat app.log | jq 'select(.duration_ms > 5000) | {request_id: .context.request_id, duration: .duration_ms, path: .path}'
```

## Metrics Analysis

### Error Rate by Service

```bash
curl -s http://localhost:8000/metrics/dependencies | jq -r '
  to_entries |
  map("\(.key): \(.value.error_count)/\(.value.total_calls) = \(.value.error_rate * 100)%") |
  .[]
'
```

### Latency Comparison

```bash
curl -s http://localhost:8000/metrics/dependencies | jq '
  to_entries |
  map({service: .key, p50: .value.latency_ms.p50, p95: .value.latency_ms.p95}) |
  sort_by(.p95)
'
```

## Emergency Procedures

### Completely Silent Failures

If errors aren't appearing in logs:

1. Check log level:
   ```bash
   echo $LOG_LEVEL  # Should be INFO or DEBUG
   ```

2. Check log file permissions:
   ```bash
   ls -la /var/log/solstein/
   ```

3. Enable console logging temporarily:
   ```python
   # In main.py
   setup_logging(level="DEBUG", json_format=False)
   ```

### System Unresponsive

1. Check if exception handlers are registered:
   ```python
   # In Python shell
   from main import app
   print(app.exception_handlers)
   ```

2. Restart with debug mode (locally only):
   ```bash
   DEBUG_ERRORS=true python -m solstein.api.main
   ```

## Getting Help

If stuck:

1. Gather context:
   - Request ID
   - Timestamp
   - Endpoint/path
   - Error code

2. Check documentation:
   - [Logging Guide](../observability/logging.md)
   - [Error Handling](../observability/error-handling.md)
   - [Tracing Guide](../observability/tracing.md)

3. Escalate with:
   - Relevant log excerpts
   - Metrics output
   - Steps already tried
