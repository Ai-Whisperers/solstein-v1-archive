# Retry Policy Usage Guide

All retry logic in Solstein MUST use `solstein.core.retry_policy`. Independent retry implementations in adapters are forbidden (STORY-116).

## Quick Start

```python
from solstein.core.retry_policy import retry_policy, RetryProfile

@retry_policy(profile=RetryProfile.NETWORK_DEFAULT)
async def fetch_from_api():
    ...
```

## Available Profiles

**NETWORK_DEFAULT** (3 retries, 1-30s exponential backoff): For general network calls to external APIs.

**RATE_LIMIT** (5 retries, 5-60s exponential backoff): For APIs with rate limiting where longer waits help.

**STRICT** (1 retry, no backoff): For idempotent writes where retrying risks duplication.

## Direct Call Wrappers

```python
from solstein.core.retry_policy import call_with_retry, call_with_retry_sync, RetryProfile

# Async
result = await call_with_retry(
    lambda: client.get("/data"),
    profile=RetryProfile.RATE_LIMIT,
    name="yahoo_finance",
)

# Sync
result = call_with_retry_sync(
    lambda: requests.get(url),
    profile=RetryProfile.NETWORK_DEFAULT,
    name="companies_house",
)
```

## Custom Configuration

```python
from solstein.core.retry_policy import get_config, RetryProfile, call_with_retry

# Override specific fields from a profile
cfg = get_config(RetryProfile.NETWORK_DEFAULT, max_retries=5, timeout_per_attempt=60.0)
result = await call_with_retry(func, config=cfg, name="custom")
```

## Metrics

Every retry sequence automatically logs structured metrics including attempt count, final outcome, and total duration. These appear in the structured log under the `retry_*` extra fields.

## Migration from Independent Implementations

Replace any `for attempt in range(...)` retry loops with the canonical module. The `data/connectors/runtime.py` ConnectorRuntime already uses `infrastructure/retry_policy.py` which is re-exported through `core/retry_policy.py`.
