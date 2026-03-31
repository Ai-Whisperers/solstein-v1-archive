# Async HTTP Client Guidelines

> EPIC-035: Async-First External Adapters

## Overview

Solstein uses **httpx** as its HTTP client library. The `requests` library is **banned** in all adapter and agent code. This was established in EPIC-035 to eliminate event-loop blocking and enable true concurrency.

## Rules

1. **Never `import requests`** in any file under `src/solstein/agents/` or `src/solstein/adapters/`. The pre-commit hook and CI script (`scripts/ci/check_banned_imports.py`) will reject it.

2. **Use `httpx.AsyncClient` in async functions.** If the calling function is `async def`, the HTTP call must be awaited via `httpx.AsyncClient`, not wrapped in `asyncio.to_thread()`.

3. **Use `httpx.get()`/`httpx.post()` in sync functions.** For sync callers (e.g., `discover()`, `enrich()`), use the top-level `httpx.get()` convenience function.

4. **Use `asyncio.gather()` for concurrent fetches.** When fetching data for multiple companies, use `asyncio.gather(*tasks, return_exceptions=True)` instead of sequential `await` calls.

5. **Catch httpx-specific exceptions.** Replace `requests.RequestException` with `(httpx.HTTPError, httpx.TimeoutException, OSError)`.

## Patterns

### Sync HTTP call (for sync methods like `discover`, `enrich`)

```python
import httpx

def _fetch_data(self, company_name: str) -> dict | None:
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        return response.json()
    except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
        logger.warning(f"Fetch failed: {e}")
        return None
```

### Async HTTP call (for async methods like `fetch_facts`, `gather`)

```python
import httpx

async def _fetch_data_async(self, company_name: str) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
        return response.json()
    except (httpx.HTTPError, httpx.TimeoutException, OSError) as e:
        logger.warning(f"Fetch failed: {e}")
        return None
```

### Concurrent fetching with asyncio.gather

```python
import asyncio

async def fetch_facts(self, company_ids: list[str]) -> list[dict]:
    async def _fetch_one(cid: str) -> dict | None:
        data = await self._fetch_data_async(cid)
        if data:
            return {"company_id": cid, "value": data}
        return None

    results = await asyncio.gather(
        *[_fetch_one(cid) for cid in company_ids],
        return_exceptions=True,
    )

    facts = []
    for i, result in enumerate(results):
        if isinstance(result, BaseException):
            logger.warning(f"Failed for {company_ids[i]}: {result}")
        elif result is not None:
            facts.append(result)

    return facts
```

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|---|---|---|
| `import requests` | Banned library | Use `import httpx` |
| `asyncio.to_thread(requests.get, ...)` | Blocks a thread pool thread unnecessarily | Use `httpx.AsyncClient` directly |
| `asyncio.to_thread(httpx.get, ...)` | Creates sync client per call, no connection pooling | Use `httpx.AsyncClient` |
| Sequential `await` in a loop | Serial I/O, no concurrency | Use `asyncio.gather()` |
| `except requests.RequestException` | Wrong library | Use `except (httpx.HTTPError, httpx.TimeoutException, OSError)` |

## Timeouts

All timeouts are centralized in `solstein.config.HttpTimeoutSettings`. Access via:

```python
from solstein.config import get_settings

settings = get_settings()
timeout = settings.http_timeouts.github  # or .news_api, .funding, etc.
```

## CI Enforcement

The banned-import check runs in two places:

1. **Pre-commit hook**: `scripts/ci/agent_precommit_hook.py` (check 7) -- blocks commits with `import requests`
2. **CI script**: `scripts/ci/check_banned_imports.py` -- scans all files under `src/solstein/`

### Running manually

```bash
python3 scripts/ci/check_banned_imports.py --path src/solstein
```

## Allowlist

Some legacy files in `src/solstein/data/sources/` still use `requests` and are explicitly allowlisted in the CI script. These are slated for removal or migration in a future epic.
