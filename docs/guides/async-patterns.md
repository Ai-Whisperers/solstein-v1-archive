# ⚡ Async Patterns Guide

**Phase**: 12-13  
**Status**: Production-Ready  
**Last Updated**: February 2026

This guide explains how Solstein implements async/await patterns for background task processing using Celery and asyncio.

---

## Overview

Solstein uses two async patterns:

1. **Celery Tasks** — For scheduled background work (data refresh)
2. **Async/Await** — For concurrent I/O operations within tasks

### When to Use Each

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Celery Tasks** | Scheduled background work | Refresh data from external APIs every 6 hours |
| **Async/Await** | Concurrent I/O in tasks | Fetch from 12 connectors in parallel |
| **Celery Chaining** | Task dependencies | Task A → Task B → Task C |

---

## Celery Task Basics

### Defining a Task

```python
# src/solstein/worker_tasks.py
from celery import shared_task, Task
from loguru import logger

@shared_task(name="solstein.worker_tasks.refresh_sec_edgar", bind=True, max_retries=3)
def refresh_sec_edgar(self):
    """Refresh SEC EDGAR data for all tracked companies.
    
    Args:
        self: Celery task context (provides self.retry(), self.request, etc.)
    
    Returns:
        dict: Result containing stored_count
    """
    logger.info("Starting SEC EDGAR refresh task")
    
    try:
        # Async operation
        result = asyncio.run(_refresh_sec_edgar_async())
        return result
    except Exception as e:
        # Will be handled by Phase 13.4 retry logic
        raise
```

### Key Parameters

```python
@shared_task(
    name="solstein.worker_tasks.refresh_sec_edgar",  # Task name for logging
    bind=True,                                        # Receive self (context)
    max_retries=3,                                    # Max retry attempts
    default_retry_delay=5,                            # Initial backoff (overridden by phase 13.4)
)
def my_task(self):
    pass
```

### Accessing Task Context

```python
@shared_task(bind=True, max_retries=3)
def refresh_github(self):
    """Example: accessing task context."""
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Task name: {self.request.task}")
    logger.info(f"Attempt number: {self.request.retries}")
    
    try:
        # ... task work
        pass
    except Exception as e:
        if self.request.retries < self.max_retries:
            # Will be retried
            raise self.retry(exc=e, countdown=5)
        else:
            # Max retries exceeded
            raise
```

---

## Async/Await Within Tasks

### Pattern: Task Wraps Async Function

```python
# src/solstein/worker_tasks.py
@shared_task(name="solstein.worker_tasks.refresh_sec_edgar")
def refresh_sec_edgar(self):
    """Celery task wrapper."""
    logger.info("Starting SEC EDGAR refresh")
    
    # Run async function in sync context
    result = asyncio.run(_refresh_sec_edgar_async())
    
    return result


async def _refresh_sec_edgar_async():
    """Actual async implementation."""
    # Get database
    db_manager = _get_db_manager()
    
    # Fetch tracked companies
    company_ids = await _get_tracked_company_ids(db_manager)
    
    # Refresh data
    connector = SECEDGARRefreshConnector()
    facts = await connector.refresh_all(company_ids)
    
    # Store facts
    stored_count = await _store_facts(db_manager, facts, "SEC_EDGAR")
    
    logger.info(f"Stored {stored_count} SEC EDGAR facts")
    return {"stored_count": stored_count}
```

### Async Patterns: Sequential

```python
async def refresh_sequential():
    """Refresh sources one at a time."""
    results = []
    
    # First source
    connector1 = SECEDGARRefreshConnector()
    facts1 = await connector1.refresh_all(company_ids)
    results.append(facts1)
    
    # Second source
    connector2 = CompaniesHouseRefreshConnector()
    facts2 = await connector2.refresh_all(company_ids)
    results.append(facts2)
    
    return results
```

**When to use**: Dependencies between sources, or when you need to limit concurrent requests.

### Async Patterns: Concurrent (Parallel)

```python
import asyncio

async def refresh_concurrent():
    """Refresh multiple sources in parallel."""
    
    # Create coroutines for all sources
    connector1 = SECEDGARRefreshConnector()
    connector2 = CompaniesHouseRefreshConnector()
    connector3 = NewsSignalsRefreshConnector()
    
    # Run all concurrently
    results = await asyncio.gather(
        connector1.refresh_all(company_ids),
        connector2.refresh_all(company_ids),
        connector3.refresh_all(company_ids),
    )
    
    return results
```

**When to use**: Independent sources, fast completion of all work.

**Advantage**: If each takes 10s, concurrent takes 10s total (vs 30s sequential).

### Async Patterns: Error Handling

```python
import asyncio

async def refresh_with_error_handling():
    """Refresh with individual error handling."""
    
    sources = [
        SECEDGARRefreshConnector(),
        CompaniesHouseRefreshConnector(),
        NewsSignalsRefreshConnector(),
    ]
    
    # Run with error handling for each
    results = []
    for connector in sources:
        try:
            facts = await connector.refresh_all(company_ids)
            results.append(facts)
        except Exception as e:
            logger.warning(f"Failed to refresh {connector.__class__.__name__}: {e}")
            # Continue with next source instead of failing everything
    
    return results
```

**When to use**: Some sources can fail without affecting others.

---

## Database Operations in Async Context

### Async Database Access

```python
async def _store_facts(db_manager, facts: list[dict], source: str) -> int:
    """Store fetched facts in database asynchronously.
    
    Args:
        db_manager: DatabaseManager instance
        facts: List of fact dictionaries to store
        source: Source identifier (e.g., "SEC_EDGAR")
    
    Returns:
        Number of facts stored
    """
    stored_count = 0
    
    # Async context manager for database session
    async with db_manager.get_session() as session:
        for fact in facts:
            try:
                company_id = fact.get("company_id")
                if not company_id:
                    continue
                
                # Store fact in database
                stored_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to store fact from {source}: {e}")
                continue
        
        # Commit all changes atomically
        await session.commit()
    
    return stored_count
```

### Key Points

1. **Context Manager**: Use `async with` for database sessions
2. **Atomicity**: All changes committed together
3. **Error Handling**: Catch per-fact errors but continue
4. **Async Operations**: All database calls must be awaited

---

## Celery Beat Scheduling

### Schedule Configuration

```python
# src/solstein/celery_config.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "refresh-sec-edgar-daily": {
        "task": "solstein.worker_tasks.refresh_sec_edgar",
        "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM
        "options": {"queue": "default"},
    },
    
    "refresh-news-signals-hourly": {
        "task": "solstein.worker_tasks.refresh_news_signals",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"queue": "default"},
    },
    
    "refresh-github-every-6-hours": {
        "task": "solstein.worker_tasks.refresh_github",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
        "options": {"queue": "default"},
    },
}
```

### Crontab Patterns

| Pattern | Meaning |
|---------|---------|
| `crontab(hour=9, minute=0)` | Daily at 9:00 AM |
| `crontab(minute=0)` | Every hour |
| `crontab(hour="*/6")` | Every 6 hours |
| `crontab(hour="*/12", minute=0)` | Every 12 hours |
| `crontab(day_of_week=0, hour=2, minute=0)` | Sundays at 2 AM |

---

## Running Tasks Manually

### Celery Command Line

```bash
# List all scheduled tasks
celery -A solstein.worker inspect active_queues

# Run a task immediately (not via schedule)
celery -A solstein.worker call solstein.worker_tasks.refresh_sec_edgar

# Monitor task execution
celery -A solstein.worker events

# View task result
celery -A solstein.worker inspect result <task_id>
```

### From Python Code

```python
# Import the task
from solstein.worker_tasks import refresh_sec_edgar

# Run synchronously (only for testing!)
result = refresh_sec_edgar()

# Queue for background execution
refresh_sec_edgar.delay()  # Returns task ID

# Queue with custom countdown
refresh_sec_edgar.apply_async(countdown=60)  # Run in 60 seconds
```

---

## Testing Async Tasks

### Unit Test Without Celery

```python
# tests/unit/test_worker.py
import pytest
from solstein.worker_tasks import _refresh_sec_edgar_async

@pytest.mark.asyncio
async def test_refresh_sec_edgar_async():
    """Test async refresh logic without Celery."""
    # Run the async function directly
    result = await _refresh_sec_edgar_async()
    
    # Assert results
    assert result["stored_count"] >= 0
    assert "stored_count" in result
```

**Key**: Test async functions directly without Celery, which makes tests simpler and faster.

### Integration Test With Celery

```python
# tests/integration/test_worker_tasks.py
import pytest
from solstein.worker_tasks import refresh_sec_edgar

@pytest.fixture
def celery_app():
    """Provide Celery app for testing."""
    from solstein.celery_config import celery_app
    celery_app.conf.task_always_eager = True  # Run tasks synchronously
    return celery_app

def test_refresh_sec_edgar_task(celery_app):
    """Test Celery task execution."""
    # Run task synchronously in test
    result = refresh_sec_edgar.apply()
    
    # Assert task completed successfully
    assert result.successful()
    assert result.result["stored_count"] >= 0
```

---

## Troubleshooting

### Task Not Running

**Symptom**: Task scheduled but not executing

**Solutions**:
1. Check Celery worker is running: `celery -A solstein.worker worker --loglevel=info`
2. Check Beat scheduler is running: `celery -A solstein.worker beat --loglevel=info`
3. Check Redis is running: `redis-cli ping` (should return "PONG")
4. Check task name in schedule matches actual task name

```bash
# Verify scheduler is running
ps aux | grep celery | grep beat

# Check scheduled tasks
celery -A solstein.worker inspect scheduled
```

### Task Timeout

**Symptom**: Task fails with TimeoutError

**Solution**: Configure task timeouts in celery_config.py

```python
# celery_config.py
celery_app.conf.update(
    task_time_limit=30,      # 30 second hard limit
    task_soft_time_limit=25, # 25 second soft limit
)
```

For specific slow tasks:
```python
@shared_task(time_limit=60, soft_time_limit=55)  # 60 second limit for this task
def slow_task():
    pass
```

### Task Memory Leak

**Symptom**: Worker process memory grows over time

**Solution**: Restart worker periodically

```python
# celery_config.py
celery_app.conf.update(
    worker_max_tasks_per_child=100,  # Restart after 100 tasks
)
```

---

## Best Practices

### 1. Make Tasks Idempotent

```python
# ❌ BAD - Multiple runs add duplicate data
@shared_task
def refresh_data():
    for company in get_all_companies():
        facts = fetch_facts(company)
        db.insert(facts)  # Duplicate if run twice

# ✅ GOOD - Idempotent (safe to run multiple times)
@shared_task
def refresh_data():
    for company in get_all_companies():
        facts = fetch_facts(company)
        db.upsert(facts)  # Update if exists, insert if not
```

### 2. Include Comprehensive Logging

```python
@shared_task(bind=True)
def refresh_data(self):
    logger.info(f"Task {self.request.id} started")
    
    try:
        result = do_work()
        logger.info(f"Task {self.request.id} completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {e}")
        raise
```

### 3. Use Timeouts

```python
@shared_task(time_limit=30)  # Kill after 30 seconds
def potentially_slow_task():
    # Task will be terminated if it takes > 30 seconds
    pass
```

### 4. Handle Retries Explicitly

See [Retry Logic Guide](./retry-logic.md) for detailed retry patterns.

### 5. Test Without Celery

```python
# ✅ GOOD - Test async logic directly
async def test_logic():
    result = await _my_async_function()
    assert result is not None

# ❌ BAD - Full Celery integration test for simple logic
def test_with_celery():
    result = my_task.apply().result
    assert result is not None
```

---

## Common Patterns

### Pattern 1: Batch Processing

```python
@shared_task(bind=True, max_retries=3)
def process_batch(self, company_ids: list[str]):
    """Process a batch of companies."""
    result = asyncio.run(_process_batch_async(company_ids))
    return result

async def _process_batch_async(company_ids: list[str]):
    """Async batch processing."""
    results = []
    
    for company_id in company_ids:
        try:
            connector = SECEDGARRefreshConnector()
            facts = await connector.refresh(company_id)
            results.append(facts)
        except Exception as e:
            logger.warning(f"Failed to process {company_id}: {e}")
            continue
    
    return results
```

### Pattern 2: Fan-Out / Fan-In

```python
from celery import group, chain

# Fan-out: Run multiple tasks in parallel
job = group(
    refresh_sec_edgar.s(),
    refresh_github.s(),
    refresh_news_signals.s(),
)

# Fan-in: Wait for all to complete, then process results
pipeline = chain(job, process_all_results.s())

# Execute
pipeline()  # Run all tasks in parallel, then process results
```

### Pattern 3: Task Chaining

```python
from celery import chain

# Run tasks sequentially
pipeline = chain(
    refresh_sec_edgar.s(),           # Run first
    refresh_companies_house.s(),     # Run after first completes
    score_all_companies.s(),         # Run after both complete
)

pipeline()
```

---

## Performance Implications & Tradeoffs

### The Cost of asyncio.run()

When you use `asyncio.run()` in a Celery task, a **new event loop is created for every task execution**:

```python
@shared_task
def my_task():
    # This creates a NEW event loop every time the task runs
    result = asyncio.run(_async_work())
    return result
```

**Performance Impact**:
- Event loop creation: ~1-5ms overhead per task
- With 1000 tasks/minute: 1-5 seconds of wasted overhead
- Connection pooling across tasks is difficult (each task gets fresh connections)

**When This Matters**:
- ✅ Fine for: Long-running tasks (>1 second of work) where 1-5ms is negligible
- ❌ Bad for: High-frequency short tasks where overhead dominates

### Connection Pooling Challenge

With `asyncio.run()`, each task gets a fresh event loop:

```python
# ❌ PROBLEM: New connection pool per task
@shared_task
def refresh_data():
    result = asyncio.run(_refresh_async())  # New event loop
    # Connection pool is destroyed after task completes
    # Next task creates new pool

# ✅ BETTER: Reuse connection pool across tasks
# (Requires async Celery - Celery 5.1+)
@shared_task
async def refresh_data():
    # Same event loop, reused connections
    result = await _refresh_async()
```

### Error Handling Complexity

Async code adds complexity to error handling:

```python
# ❌ HARDER: Nested try/except for async
@shared_task(bind=True, max_retries=3)
def my_task(self):
    try:
        result = asyncio.run(_async_work())
    except SoftTimeLimitExceeded:
        # Celery timeout - need to catch this
        logger.warning("Task timeout")
        return None
    except Exception as e:
        # Async exceptions - need to handle
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=5)
        raise
```

---

## Celery Timeout Strategy

### Soft vs Hard Limits

Celery uses **two timeout thresholds** to balance graceful shutdown with safety:

```python
# src/solstein/celery_config.py (Lines 43-44)
celery_app.conf.update(
    task_soft_time_limit=25,   # Soft limit: exception raised
    task_time_limit=30,        # Hard limit: process killed
)
```

| Limit | Behavior | Use Case |
|-------|----------|----------|
| **Soft (25s)** | `SoftTimeLimitExceeded` exception raised | Graceful cleanup (close connections, log, etc.) |
| **Hard (30s)** | Process killed unconditionally | Absolute maximum, no cleanup |

### Catching Soft Timeout

**ALWAYS catch `SoftTimeLimitExceeded` to clean up gracefully**:

```python
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(bind=True, max_retries=3)
def refresh_sec_edgar(self):
    """Refresh with graceful timeout handling."""
    try:
        # Work that might take up to 25 seconds
        result = asyncio.run(_refresh_sec_edgar_async())
        logger.info(f"Refresh completed: {result}")
        return result
        
    except SoftTimeLimitExceeded:
        # CRITICAL: Catch this and clean up!
        logger.warning("Task approaching timeout, gracefully exiting")
        # Close connections, save state, etc.
        return {"status": "timeout", "partial": True}
        
    except Exception as e:
        # Other errors - retry with backoff
        countdown = 5 * (2 ** self.request.retries)
        logger.error(f"Task failed: {e}, retrying in {countdown}s")
        raise self.retry(exc=e, countdown=countdown)
```

### Timeout Configuration

Current Solstein configuration:

```python
task_soft_time_limit=25,   # 25 seconds: exception raised
task_time_limit=30,        # 30 seconds: process killed
```

This gives tasks **5 seconds to catch the exception and clean up** before hard kill.

### Future: Native Async Celery

Celery 5.1+ supports native async tasks (no `asyncio.run()` needed):

```python
# Celery 5.1+ (not currently used in Solstein)
@shared_task
async def refresh_sec_edgar():
    """Native async task - no asyncio.run() needed."""
    result = await _refresh_sec_edgar_async()
    return result
```

**Benefits**:
- ✅ Single event loop per worker (not per task)
- ✅ Connection pooling across tasks
- ✅ Simpler error handling
- ✅ Better performance for high-frequency tasks

**Current Status**: Solstein uses `asyncio.run()` pattern (Celery 5.0 compatible)

---

## References

- [Celery Documentation](https://docs.celeryq.dev/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Phase 13.4: Retry Logic](./retry-logic.md)
- [Worker Tasks Source](../../src/solstein/worker_tasks.py)

---

**Last Updated**: February 26, 2026  
**Status**: Production-Ready ✅
