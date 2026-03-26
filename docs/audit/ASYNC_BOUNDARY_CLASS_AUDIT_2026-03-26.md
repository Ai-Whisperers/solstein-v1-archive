# Async Boundary Class Audit — 2026-03-26

**Bug class:** Blocking synchronous work inside `async` code paths, plus adjacent async-boundary misuse where coroutine-returning APIs were invoked like sync functions.

**Goal:** Remove the class globally from the currently live search, patent, web-research, and news-signal paths rather than fixing it one file at a time.

---

## Scope Reviewed

Targeted scan over async paths touching:

- patent lookup
- web search lookup
- DuckDuckGo search
- news signal detection
- company research refresh connectors

The concrete review focused on direct uses of:

- `search_company_patents(...)`
- `search_company_info(...)`
- `DDGS()`
- `researcher.research(...)`
- `detect_funding_signal(...)`
- `detect_partnership_signal(...)`
- `detect_key_hire_signal(...)`

---

## Fixes Applied

### 1. Patents unified refresh path

**File:** `src/solstein/adapters/enrichment/patents_unified.py`

**Before:** `async def fetch_facts(...)` called `search_company_patents(company_name)` directly.

**After:** The call is now wrapped with `await asyncio.to_thread(...)`.

**Why it matters:** Patent lookup is synchronous and can perform network/search work. Running it inline inside the event loop can stall unrelated async tasks.

### 2. Web search refresh path

**File:** `src/solstein/infrastructure/connectors/web_search_refresh.py`

**Before:** `async def fetch_facts(...)` called `search_company_info(...)` directly.

**After:** The lookup now runs behind `await asyncio.to_thread(...)`.

**Why it matters:** This path is part of refresh orchestration and must not block the loop during external search calls.

### 3. Web research pipeline DuckDuckGo path

**File:** `src/solstein/data/web_research_pipeline.py`

**Before:** `async def search_web(...)` instantiated `DDGS()` and executed the sync search inline.

**After:** A dedicated sync helper `_search_web_sync(...)` was introduced and `search_web(...)` now calls it via `await asyncio.to_thread(...)`.

**Why it matters:** This was a pure blocking sync library call inside an async method, repeated across multi-company research flows.

### 4. News signal refresh async misuse

**File:** `src/solstein/infrastructure/connectors/news_signal_refresh.py`

**Before:** Async detector methods were called without `await`, producing coroutine objects instead of signal lists.

**After:** The connector now awaits them with `await asyncio.gather(...)`.

**Why it matters:** This is not event-loop blocking in the same way as sync I/O, but it is the same async-boundary defect family: treating an async contract as if it were synchronous. In practice it breaks signal extraction just as badly.

---

## Regression Coverage Added

**File:** `tests/unit/test_async_boundary_regressions.py`

Added coverage for:

- patent refresh path offloads lookup to `asyncio.to_thread`
- web search refresh path offloads lookup to `asyncio.to_thread`
- web research DuckDuckGo path offloads sync search to `asyncio.to_thread`
- news signal refresh path awaits async detector methods

---

## Verification

Commands run:

```bash
uv run python -m py_compile \
  src/solstein/adapters/enrichment/patents_unified.py \
  src/solstein/infrastructure/connectors/web_search_refresh.py \
  src/solstein/infrastructure/connectors/news_signal_refresh.py \
  src/solstein/data/web_research_pipeline.py \
  tests/unit/test_async_boundary_regressions.py

DATABASE__URL=postgresql+asyncpg://user:pass@localhost/test \
SECURITY__SECRET_KEY=test-secret \
GITHUB_TOKEN=test-token \
COMPANIES_HOUSE_API_KEY=test-key \
NEWSAPI_KEY=test-news \
uv run pytest \
  tests/unit/test_async_boundary_regressions.py \
  tests/unit/test_web_search_refresh.py \
  tests/unit/test_news_signal_refresh.py -q
```

Result:

- `12 passed`

---

## Residual Notes

### 1. No remaining live offenders were found in the targeted bug-class scan

After the fix pass, the targeted search no longer found any unwrapped sync patent/web-search/DDG calls inside the audited async paths.

### 2. One stale integration suite is still noisy but unrelated

**File:** `tests/integration/test_unified_adapters.py`

This file currently fails on unrelated protocol and enum drift:

- outdated `UnifiedDataSource` expectations
- outdated `DataSourceType` expectations
- stale `SourceAuthority` names

These failures are not evidence that the async-boundary bug class remains. They are separate test debt and should be reconciled independently.

---

## Next Enforcement Step

If we want this class to stay dead, the next step should be a lint-style static gate that rejects:

1. direct use of known blocking helpers inside `async def`
2. direct use of sync search/scrape clients in refresh/adapter async paths
3. un-awaited async detector calls in connectors
