# STORY-134: Replace requests with httpx in News and Funding Adapters

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-133 (establishes httpx pattern for the codebase) |

---

## The Audit Verdict

> `news_unified.py`, `funding_unified.py`, `additional_sources.py` — synchronous `requests` library used throughout async adapters. Multiple external API calls that should run concurrently are serialized by blocking I/O.

---

## Problem Statement

The news and funding adapters are responsible for fetching data from multiple independent external sources per research job: NewsAPI, GDELT, RSS feeds, Crunchbase, PitchBook, and various supplementary data providers. These sources are independent — a response from NewsAPI has no bearing on when a GDELT request can be sent. They should be fetched concurrently. They are not.

All three adapters — `news_unified.py`, `funding_unified.py`, and `additional_sources.py` — use the synchronous `requests` library inside async functions. The consequence is that what should be 3 concurrent requests taking approximately 1 second total instead takes 3 seconds sequentially. At the scale of a full research job covering 10 companies, each with news and funding lookups across 3+ sources, this serialization multiplies pipeline duration by the number of external sources. The math is not subtle.

The problem compounds because these adapters are called from within the broader research pipeline, which is itself async. The pipeline's concurrency model assumes that each adapter will yield control to the event loop while waiting for network responses. When an adapter blocks instead, it doesn't just slow itself down — it prevents every other concurrent pipeline stage from making progress. A news fetch that takes 2 seconds doesn't cost 2 seconds; it costs 2 seconds multiplied by however many other operations were waiting to run.

The fix requires two things: replacing `requests` with `httpx.AsyncClient`, and restructuring the fetch logic within each adapter to use `asyncio.gather()` for independent source calls. The first change makes the code non-blocking. The second change makes it actually concurrent.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | Research pipeline 3-5× slower than necessary due to serial API calls across independent sources. |
| **Scalability** | Each additional data source added to the pipeline multiplies the performance penalty linearly. |
| **Throughput** | Concurrent research jobs compete for event loop time that is being wasted on blocking I/O waits. |
| **User Experience** | Research jobs that should complete in under a minute take several minutes due to serialized fetching. |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | `requests` used for NewsAPI, GDELT, and RSS feed fetches — all should be concurrent |
| `data/funding_unified.py` | `requests` used for funding data sources — blocks event loop per source |
| `agents/additional_sources.py` | `requests` used for supplementary data providers — serializes independent calls |
| Tests for all three adapters | Mocks targeting `requests` must be updated to target `httpx` |

---

## Architectural Requirements

- `httpx.AsyncClient` must replace `requests` in all three adapters: `news_unified.py`, `funding_unified.py`, and `additional_sources.py`
- Independent source fetches within each adapter must be restructured to use `asyncio.gather()` — sources that do not depend on each other's results must not be fetched sequentially
- Each adapter must manage its own `httpx.AsyncClient` instance appropriately — either as a shared instance with connection pooling or as a context manager scoped to the fetch operation
- Timeout configuration must be source-specific: RSS feeds and slower external APIs may require longer timeouts than fast REST APIs
- Retry logic must be updated to handle `httpx` exception types for each source
- Error handling must be per-source: a failure fetching from GDELT must not prevent NewsAPI results from being returned
- The public interface of each adapter (function signatures, return types, error contracts) must remain unchanged — callers must not require modification
- Connection pooling must be configured to respect rate limits of each external source

---

## Acceptance Criteria

- [ ] No `import requests` or `from requests` statements remain in `news_unified.py`, `funding_unified.py`, or `additional_sources.py`
- [ ] All HTTP calls in all three adapters use `await` with `httpx.AsyncClient`
- [ ] Independent source fetches within each adapter use `asyncio.gather()` rather than sequential `await` calls
- [ ] Timeout configuration is source-specific and uses `httpx`-native timeout objects
- [ ] A failure fetching from one source does not prevent results from other sources being returned
- [ ] All existing unit tests pass with mocks updated to target `httpx`
- [ ] An integration test demonstrates that a research job with news and funding lookups issues parallel API calls (verifiable via timing or mock call ordering)
- [ ] Adapter public interfaces are unchanged — no callers require modification

---

## Definition of Done

- **Tests Required**: Integration test covering a research job with news + funding data collection, verifying that independent source fetches are issued concurrently (not sequentially). Unit tests updated to mock `httpx`. All existing tests pass. Timing assertion: 3-source fetch completes in ≤ max(individual source times) + overhead, not sum(individual source times).
- **Documentation Required**: Inline comments documenting the concurrency model within each adapter (which calls are gathered, which are sequential and why). No new external documentation required.
- **Code Review Gate**: Reviewer must verify (a) `asyncio.gather()` is used for independent source fetches, (b) no `requests` imports remain, (c) per-source error handling is preserved, (d) adapter interfaces are unchanged.

---

## Notes

The `asyncio.gather()` requirement deserves emphasis. Simply replacing `requests` with `httpx.AsyncClient` and using `await` for each call is necessary but not sufficient. Sequential `await` calls are non-blocking but still serial — each one waits for the previous to complete before starting. True concurrency requires `asyncio.gather()` (or equivalent) to launch multiple coroutines simultaneously.

The distinction matters: `await fetch_newsapi(); await fetch_gdelt()` is non-blocking but sequential (total time = newsapi_time + gdelt_time). `await asyncio.gather(fetch_newsapi(), fetch_gdelt())` is concurrent (total time ≈ max(newsapi_time, gdelt_time)). For adapters fetching from 3+ independent sources, this is the difference between 3 seconds and 1 second per research job.

Per-source error handling is a non-negotiable requirement. These are external APIs with independent reliability profiles. A GDELT outage should not prevent NewsAPI results from reaching the pipeline. The current `requests`-based implementation may already handle this correctly; the migration must preserve that behavior.

This story depends on STORY-133 only in the sense that STORY-133 establishes the `httpx` pattern for the codebase. The technical work here is independent and could proceed in parallel if needed.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
