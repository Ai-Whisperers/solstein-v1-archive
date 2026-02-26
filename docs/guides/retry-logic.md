# 🔄 Retry Logic & Exponential Backoff Guide

**Phase**: 13.4  
**Status**: Production-Ready  
**Last Updated**: February 2026

This guide explains Solstein's exponential backoff retry logic and Dead Letter Queue tracking for async tasks.

---

## Overview

When async tasks fail due to transient errors (network timeouts, rate limits), they're automatically retried with exponential backoff:

```
Attempt 1 fails → wait 5s → Attempt 2
Attempt 2 fails → wait 10s → Attempt 3
Attempt 3 fails → wait 20s → Give up, record in DLQ
```

---

## The Exponential Backoff Formula

### Mathematical Definition

```
wait_time = base * (2 ^ (attempt - 1))

Where:
  base = 5 seconds
  attempt = retry attempt number (1, 2, 3, ...)
```

### Calculation Table

| Attempt | Formula | Wait Time | Cumulative |
|---------|---------|-----------|------------|
| 1 | 5 * 2^0 | 5s | 5s |
| 2 | 5 * 2^1 | 10s | 15s |
| 3 | 5 * 2^2 | 20s | 35s |

### Why Exponential?

1. **Avoids Overwhelming Service**: Longer waits for failed services
2. **Resolves Transient Issues**: Gives time for network/service to recover
3. **Reduces Thundering Herd**: Multiple tasks don't retry simultaneously

---

## Implementation

### Task Definition with Retry

```python
# src/solstein/worker_tasks.py
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger

@shared_task(
    name="solstein.worker_tasks.refresh_sec_edgar",
    bind=True,           # Receive self (context)
    max_retries=3        # Maximum 3 attempts
)
def refresh_sec_edgar(self):
    """Refresh SEC EDGAR data with exponential backoff.
    
    Retries:
    - Attempt 1: wait 5s
    - Attempt 2: wait 10s
    - Attempt 3: wait 20s
    - Failure: recorded in Dead Letter Queue
    """
    logger.info("Starting SEC EDGAR refresh task")
    
    try:
        # Attempt work
        result = asyncio.run(_refresh_sec_edgar_async())
        logger.info(f"SEC EDGAR refresh succeeded: {result}")
        return result
        
    except (ConnectionError, TimeoutError, IOError) as e:
        # Transient error - retry with backoff
        countdown = 5 * (2 ** self.request.retries)
        
        logger.warning(
            f"[RETRY-ATTEMPT-{self.request.retries + 1}] "
            f"SEC EDGAR refresh will retry in {countdown}s: {e}"
        )
        
        # Schedule retry
        raise self.retry(exc=e, countdown=countdown)
        
    except MaxRetriesExceededError as e:
        # All retries exhausted
        logger.error(f"[RETRY-FAILED] SEC EDGAR refresh failed after {self.max_retries} attempts")
        
        # Record in Dead Letter Queue for analysis
        dead_letter_queue.record_failure(
            task_name="refresh_sec_edgar",
            task_id=self.request.id,
            error=str(e),
            attempt=self.request.retries
        )
        
    except Exception as e:
        # Permanent error - don't retry
        logger.error(f"[PERMANENT-FAILURE] SEC EDGAR refresh failed permanently: {e}")
        raise
```

### Key Components

```python
@shared_task(bind=True, max_retries=3)
def my_task(self):
    #          ↓
    #    Receive self (task context)
    #                  ↓
    #            3 maximum attempts
    
    try:
        # Do work
        pass
    except TransientError as e:
        # Calculate backoff
        countdown = 5 * (2 ** self.request.retries)
        #                    ↑
        #            Current attempt number (0-based)
        #            0 = first attempt, 1 = first retry, etc.
        
        # Retry with backoff
        raise self.retry(exc=e, countdown=countdown)
```

---

## Logging Pattern

### Standard Log Format

Every retry is logged with a clear, parseable format:

```
[RETRY-ATTEMPT-N] message
[RETRY-FAILED] message
[PERMANENT-FAILURE] message
```

### Example Logs

```bash
# First attempt fails
[2026-02-26 10:00:05] [RETRY-ATTEMPT-1] SEC EDGAR refresh will retry in 5s: Connection timeout

# Second attempt fails
[2026-02-26 10:00:10] [RETRY-ATTEMPT-2] SEC EDGAR refresh will retry in 10s: Rate limit exceeded

# Third attempt fails (permanent)
[2026-02-26 10:00:20] [RETRY-FAILED] SEC EDGAR refresh failed after 3 attempts: Service unavailable
```

### Log Parsing

```bash
# Watch for retry attempts
tail -f application.log | grep RETRY-ATTEMPT

# Count retries by task
grep RETRY-ATTEMPT application.log | cut -d' ' -f2 | sort | uniq -c

# Find permanently failed tasks
grep RETRY-FAILED application.log
```

---

## Dead Letter Queue (DLQ)

### Purpose

Records tasks that permanently failed after all retries, for:
- Monitoring and alerting
- Post-mortem analysis
- Manual recovery

### Implementation

```python
# src/solstein/worker_tasks.py - Lines 103-125
class DeadLetterQueue:
    """Track permanently failed jobs after max retries exceeded."""
    
    def __init__(self):
        self.failed_jobs = []
    
    def record_failure(
        self,
        task_name: str,
        task_id: str,
        error: str,
        attempt: int
    ):
        """Record a permanently failed job."""
        self.failed_jobs.append({
            "task_name": task_name,
            "task_id": task_id,
            "error": error,
            "final_attempt": attempt,
            "timestamp": datetime.now(timezone.utc),
        })
        
        logger.error(
            f"[RETRY-FAILED] {task_name} (task_id={task_id}): "
            f"{error} after {attempt} attempts"
        )

# Global instance
dead_letter_queue = DeadLetterQueue()
```

### Usage

```python
# When a task's retries are exhausted:
dead_letter_queue.record_failure(
    task_name="refresh_sec_edgar",
    task_id=self.request.id,
    error="API returned 500 Server Error",
    attempt=3
)
```

### Monitoring DLQ

```python
# Get failed jobs
failed_jobs = dead_letter_queue.failed_jobs

# Find failures by task
sec_failures = [j for j in failed_jobs if j["task_name"] == "refresh_sec_edgar"]

# Find recent failures
recent = [j for j in failed_jobs if (datetime.now(timezone.utc) - j["timestamp"]).days < 1]

# Alert if DLQ growing
if len(dead_letter_queue.failed_jobs) > 100:
    logger.critical("DLQ has 100+ failed jobs - investigate!")
```

---

## Task Timeout Configuration

### Hard vs Soft Limits

| Limit | Behavior | Purpose |
|-------|----------|---------|
| **Soft Limit** | Signal task to shutdown gracefully | Clean shutdown (close DB, etc.) |
| **Hard Limit** | Kill task immediately | Prevent zombie processes |

### Configuration

```python
# src/solstein/celery_config.py
celery_app.conf.update(
    task_time_limit=30,      # Hard limit: kill after 30 seconds
    task_soft_time_limit=25, # Soft limit: graceful shutdown at 25s
)
```

### Task-Specific Limits

```python
@shared_task(time_limit=60, soft_time_limit=55)  # 60s hard, 55s soft
def slow_task():
    pass
```

### Handling Soft Timeout

```python
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(time_limit=30, soft_time_limit=25)
def my_task():
    try:
        do_work()
    except SoftTimeLimitExceeded:
        # Graceful cleanup
        logger.warning("Task exceeded soft time limit, shutting down gracefully")
        cleanup_resources()
        raise
```

---

## Error Handling Strategy

### Transient vs Permanent Errors

```python
from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True, max_retries=3)
def refresh_data(self):
    try:
        result = fetch_data_from_api()
        return result
        
    except ConnectionError as e:
        # ✅ TRANSIENT - Network issue, retry
        countdown = 5 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
        
    except TimeoutError as e:
        # ✅ TRANSIENT - API slow, retry
        countdown = 5 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
        
    except ValueError as e:
        # ❌ PERMANENT - Bad input, don't retry
        logger.error(f"Permanent error: {e}")
        raise  # Will not retry
        
    except MaxRetriesExceededError:
        # ❌ All retries exhausted
        logger.error("All retries failed")
        dead_letter_queue.record_failure(...)
        raise
```

### Retry Decision Tree

```
Does error indicate service issue?
├─ YES → Transient → Retry with backoff
├─ NO → Permanent → Fail immediately
```

### Common Transient Errors

- `ConnectionError` — Network disconnected
- `TimeoutError` — API not responding
- `HTTPError(503)` — Service Unavailable
- `HTTPError(429)` — Rate Limited
- `IOError` — File/disk I/O issue

### Common Permanent Errors

- `ValueError` — Invalid input
- `KeyError` — Missing required key
- `HTTPError(400)` — Bad Request
- `HTTPError(401)` — Unauthorized
- `HTTPError(404)` — Not Found

---

## Monitoring & Alerts

### Key Metrics

```python
# Monitor retry rate
retry_count = len([j for j in logs if "[RETRY-ATTEMPT" in j])
total_attempts = len([j for j in logs if "refresh_" in j])
retry_rate = retry_count / total_attempts  # Should be < 5%

# Monitor failure rate
failed_count = len(dead_letter_queue.failed_jobs)
failure_rate = failed_count / total_attempts  # Should be < 1%

# Monitor by task
sec_failures = len([j for j in dead_letter_queue.failed_jobs 
                    if "sec_edgar" in j["task_name"]])
```

### Alerting Rules

```yaml
# Alert if any task fails > 2 times in same hour
alert:
  - name: repeated_task_failures
    condition: |
      count(logs[task_name == "refresh_sec_edgar" AND "[RETRY-FAILED]" in message]) > 2
      in last(1h)
    severity: warning

# Alert if DLQ grows > 50 items
alert:
  - name: large_dead_letter_queue
    condition: len(dead_letter_queue.failed_jobs) > 50
    severity: critical
```

---

## Testing Retry Logic

### Unit Test

```python
# tests/unit/test_retry_logic.py
import pytest
from unittest.mock import Mock, patch
from solstein.worker_tasks import refresh_sec_edgar

def test_retry_backoff_calculation():
    """Test exponential backoff formula."""
    for attempt in range(3):
        wait_time = 5 * (2 ** attempt)
        assert wait_time == [5, 10, 20][attempt]

def test_retry_on_connection_error(celery_app):
    """Test retry behavior on transient error."""
    # Setup: task will fail on first 2 attempts
    call_count = [0]
    
    def mock_refresh():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ConnectionError("Network down")
        return {"stored_count": 42}
    
    # Run task synchronously
    celery_app.conf.task_always_eager = True
    
    # Mock the refresh function
    with patch("solstein.worker_tasks._refresh_sec_edgar_async", mock_refresh):
        result = refresh_sec_edgar.apply()
        
        # Task should succeed on 3rd attempt
        assert result.successful()
        assert result.result["stored_count"] == 42

def test_no_retry_on_permanent_error(celery_app):
    """Test no retry on permanent error."""
    def mock_refresh():
        raise ValueError("Invalid data")
    
    celery_app.conf.task_always_eager = True
    
    with patch("solstein.worker_tasks._refresh_sec_edgar_async", mock_refresh):
        result = refresh_sec_edgar.apply()
        
        # Task should fail immediately
        assert not result.successful()
        assert isinstance(result.result, ValueError)
```

### Integration Test

```python
# tests/integration/test_dlq.py
import pytest
from solstein.worker_tasks import dead_letter_queue

def test_dlq_records_permanent_failures(celery_app):
    """Test Dead Letter Queue tracking."""
    # Clear DLQ
    dead_letter_queue.failed_jobs.clear()
    
    # Run task that will fail
    # ... task setup ...
    
    # Verify DLQ recorded failure
    assert len(dead_letter_queue.failed_jobs) == 1
    failure = dead_letter_queue.failed_jobs[0]
    assert failure["task_name"] == "refresh_sec_edgar"
    assert failure["final_attempt"] == 3
```

---

## Best Practices

### 1. Choose Correct Error Type

```python
# ✅ GOOD - Distinguishes error types
try:
    result = api.fetch()
except ConnectionError:
    # Retry transient
    raise self.retry(...)
except ValueError:
    # Don't retry permanent
    raise

# ❌ BAD - Retries everything
try:
    result = api.fetch()
except Exception:
    raise self.retry(...)  # Retries even permanent errors!
```

### 2. Log Retries Consistently

```python
# ✅ GOOD - Clear, parseable logging
countdown = 5 * (2 ** self.request.retries)
logger.warning(
    f"[RETRY-ATTEMPT-{self.request.retries + 1}] "
    f"Task will retry in {countdown}s: {error}"
)

# ❌ BAD - Inconsistent format
logger.warning(f"Retry in {countdown}s")  # Hard to parse logs
```

### 3. Monitor DLQ Growth

```python
# ✅ GOOD - Regular monitoring
if len(dead_letter_queue.failed_jobs) > THRESHOLD:
    logger.critical("DLQ threshold exceeded!")
    send_alert()

# ❌ BAD - Ignore permanent failures
# DLQ grows unbounded, no visibility
```

### 4. Set Reasonable Timeouts

```python
# ✅ GOOD - Task-specific timeouts
@shared_task(time_limit=30)  # Most tasks
def quick_task():
    pass

@shared_task(time_limit=300)  # Batch operations
def batch_task():
    pass

# ❌ BAD - One size fits all
@shared_task(time_limit=5)  # Too short, tasks fail
def my_task():
    pass
```

### 5. Test Without Celery

```python
# ✅ GOOD - Test async logic directly
@pytest.mark.asyncio
async def test_refresh_logic():
    result = await _refresh_async()
    assert result is not None

# ❌ BAD - Celery integration test for simple logic
def test_with_celery():
    result = refresh_task.apply().result
    # Slower, harder to debug
```

---

## Troubleshooting

### Task Not Retrying

**Symptom**: Task fails once and doesn't retry

**Check**:
1. Task has `@shared_task(bind=True, max_retries=3)`?
2. Error is caught and `self.retry()` is called?
3. Celery worker is running?

```bash
# Verify worker is running
ps aux | grep celery | grep worker
```

### Too Many Retries

**Symptom**: Task retries many times unnecessarily

**Solution**: Reduce max_retries or change error classification

```python
@shared_task(bind=True, max_retries=1)  # Only 1 retry (wait 5s)
def quick_fail_task(self):
    pass
```

### DLQ Not Growing But Tasks Failing

**Symptom**: See [RETRY-FAILED] in logs but DLQ empty

**Cause**: MaxRetriesExceededError not caught

**Fix**:
```python
except MaxRetriesExceededError as e:
    dead_letter_queue.record_failure(...)
```

---

## Performance Implications

### Retry Wait Times

```
Total wait for 3 attempts: 5 + 10 + 20 = 35 seconds
Average task processing: ~5-10 seconds
Total time: 40-45 seconds
```

### Throughput Impact

```
Without retries:
- 100 tasks/hour
- 10% fail immediately = 10 failed tasks/hour

With retries (5s base, 3 max):
- Same 100 tasks/hour
- 10% eventually succeed = 1 failed task/hour
- 35 seconds added latency for failed tasks
```

---

## References

- [Celery Retry Documentation](https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying)
- [Phase 13.4 Implementation](../phases/phase-13.md#134-async-retry-logic-with-exponential-backoff)
- [Async Patterns Guide](./async-patterns.md)

---

**Last Updated**: February 26, 2026  
**Status**: Production-Ready ✅
