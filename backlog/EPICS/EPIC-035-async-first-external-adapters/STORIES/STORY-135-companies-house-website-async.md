# STORY-135: Replace requests with httpx in Companies House and Website Agents

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

> `companies_house_agent.py`, `website_agent.py` — synchronous `requests` library used in async agents. UK company data fetching and website scraping are I/O-bound operations that currently block the event loop, serializing the UK research path unnecessarily.

---

## Problem Statement

UK company research involves two distinct I/O-bound operations: querying the Companies House API for official registration data, and fetching the company's own website for supplementary intelligence. Both operations are slow by nature — Companies House API calls routinely take 500ms to 2 seconds, and website fetches can take 1 to 5 seconds depending on the target site's response time and payload size. Both operations are currently synchronous.

The `companies_house_agent.py` and `website_agent.py` agents use `requests` inside async functions. The consequence is identical to the pattern seen elsewhere in this audit: the event loop blocks for the duration of each HTTP call. For UK company research, this means the Companies House lookup and the website fetch are serialized — the website fetch cannot begin until the Companies House response has been received and processed. In the best case, this doubles the time required for UK company data collection. In the worst case, with slow websites and rate-limited Companies House responses, it multiplies it by 5 or more.

The website agent presents an additional consideration: website scraping is inherently more variable than API calls. Target sites may be slow, may redirect multiple times, may return large HTML payloads, or may require following links to gather meaningful content. These characteristics make long timeouts necessary and make the blocking behavior particularly costly — a 5-second website fetch blocks the event loop for 5 seconds, during which no other research job can make progress.

There is also a correctness concern with the website agent: it must respect `robots.txt`. This behavior must be preserved through the migration. The async HTTP client used must support the same `robots.txt` checking mechanism, or the checking logic must be adapted to work with the new client.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | UK company research path is 2-5× slower than necessary due to serialized Companies House + website fetches. |
| **User Experience** | Users researching UK companies wait significantly longer than users researching companies with faster data sources. |
| **Event Loop Health** | Website fetches of 1-5 seconds block the event loop entirely, starving all other concurrent operations. |
| **Scalability** | Batch UK company research jobs are disproportionately slow relative to their data requirements. |

---

## Affected Files

| File | Issue |
|------|-------|
| `agents/companies_house_agent.py` | `requests` used for Companies House API calls — blocks event loop for 500ms-2s per call |
| `agents/website_agent.py` | `requests` used for website fetching — blocks event loop for 1-5s per fetch; `robots.txt` behavior must be preserved |
| Tests for both agents | Mocks targeting `requests` must be updated to target `httpx` or `aiohttp` |

---

## Architectural Requirements

- `httpx.AsyncClient` must replace `requests` in `companies_house_agent.py` for all Companies House API calls
- `httpx.AsyncClient` must replace `requests` in `website_agent.py` for website fetching; `aiohttp` is an acceptable alternative if `httpx` proves insufficient for specific website scraping scenarios (e.g., sites requiring particular TLS configurations or connection behaviors)
- Where Companies House lookup and website fetch are independent operations within the same research job, they must be issued concurrently using `asyncio.gather()` or equivalent
- Timeout configuration must be appropriate for each use case: Companies House API calls (shorter timeout, ~10s), website fetches (longer timeout, 10-30s to accommodate slow sites)
- Retry logic must be updated to handle `httpx` (or `aiohttp`) exception types
- `robots.txt` compliance in `website_agent.py` must be preserved — the existing behavior for checking and respecting `robots.txt` must continue to function correctly after the migration
- The public interface of both agents must remain unchanged — callers must not require modification
- Connection pooling must be configured to avoid overwhelming target websites with concurrent connections

---

## Acceptance Criteria

- [ ] No `import requests` or `from requests` statements remain in `companies_house_agent.py` or `website_agent.py`
- [ ] All HTTP calls in both agents use `await` with `httpx.AsyncClient` (or `aiohttp` for website agent if justified)
- [ ] Companies House lookup and website fetch are issued concurrently where they are independent operations
- [ ] Timeout configuration is appropriate per use case: shorter for API calls, longer (10-30s) for website fetches
- [ ] `robots.txt` compliance is preserved and verified by test
- [ ] All existing unit tests pass with mocks updated to target the new HTTP client
- [ ] An integration test demonstrates parallel API calls for UK company research (verifiable via timing)
- [ ] Agent public interfaces are unchanged — no callers require modification

---

## Definition of Done

- **Tests Required**: Integration test covering UK company research, verifying that Companies House API call and website fetch are issued concurrently (not sequentially). Unit test verifying `robots.txt` compliance is preserved. All existing tests pass. Timing assertion: combined fetch completes in ≤ max(companies_house_time, website_time) + overhead.
- **Documentation Required**: If `aiohttp` is chosen for the website agent instead of `httpx`, a brief inline comment explaining the rationale (e.g., specific compatibility requirement). No new external documentation required.
- **Code Review Gate**: Reviewer must verify (a) no `requests` imports remain, (b) concurrent fetching is implemented where applicable, (c) `robots.txt` compliance is preserved, (d) timeout values are appropriate for each use case, (e) no blocking I/O remains in any `async def` function.

---

## Notes

The `robots.txt` requirement is the most important non-obvious constraint in this story. The website agent's existing `robots.txt` checking logic was presumably written against the `requests` library's synchronous interface. After migration to an async HTTP client, the `robots.txt` fetch itself must also be async — a synchronous `robots.txt` check would reintroduce the blocking behavior this story is designed to eliminate.

The choice between `httpx` and `aiohttp` for the website agent should be made pragmatically. `httpx` is preferred for consistency with the rest of the codebase (as established by STORY-133). However, website scraping sometimes encounters edge cases — unusual TLS configurations, non-standard redirect behaviors, sites that require specific connection characteristics — where `aiohttp` may be more robust. The implementer should default to `httpx` and only switch to `aiohttp` if specific, documented compatibility issues arise.

Connection pooling deserves attention for the website agent specifically. Unlike API calls to a single endpoint, website fetches target many different domains. The connection pool should be configured to limit concurrent connections per domain to avoid appearing as a DDoS attack to target sites. This is a behavioral requirement, not just a performance consideration.

This story is independent of STORY-134 and could be worked in parallel by a separate engineer.

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
