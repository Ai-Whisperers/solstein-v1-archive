# STORY-121: Restore Error Handling in news_unified.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-092 (merge task files) |

---

## The Audit Verdict

> Forensic audit found `news.py` (old) has `AdditionalDataSources` wrapper with error handling and retry. `news_unified.py` (new) lacks this wrapper — errors pass through unhandled.

---

## Problem Statement

The "unified" news adapter is a regression. The old version had a wrapper that caught API errors, applied retry logic, and transformed responses into structured domain errors. The unified version assumes the base connector handles everything — it doesn't. When NewsAPI returns a 429 or 500, the unified adapter propagates the raw exception instead of the structured error the old version would have caught. This is not a migration; it's a partial rewrite that lost functionality.

The `AdditionalDataSources` wrapper in `news.py` was not incidental scaffolding. It was the error boundary for the entire news data path. It knew that NewsAPI rate-limits aggressively, that 500s are transient, and that timeouts should be retried with backoff. The unified adapter knows none of this. It inherits from `BaseRefreshConnector` and trusts that the base class will handle what it cannot. The base class does not.

The practical consequence is that any research pipeline run that hits a NewsAPI rate limit will fail with an unhandled exception rather than retrying and succeeding. This is a silent reliability regression that will not be caught in unit tests that mock the happy path. It will be caught in production, at the worst possible time, with the least useful error message.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Unhandled 429/500/503 responses from NewsAPI crash the research pipeline instead of triggering retry |
| **Maintainability** | Two versions of the news adapter with different error semantics; developers cannot know which behavior to expect |
| **Error Observability** | Raw HTTP exceptions surface instead of structured domain errors, making debugging significantly harder |
| **Test Coverage** | Error path tests written against `news.py` do not cover `news_unified.py` behavior |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | Missing `AdditionalDataSources` wrapper; no retry logic; raw exceptions propagate |
| `data/news.py` | Reference implementation — contains the error handling that must be ported; to be deleted after parity |

---

## Architectural Requirements

- Error handling wrapper equivalent to `AdditionalDataSources` in `news.py` must be present in `news_unified.py`
- Retry logic must cover HTTP 429 (rate limit), 500 (server error), and 503 (service unavailable) status codes
- Retry strategy must use exponential backoff with jitter, not fixed-interval polling
- Maximum retry attempts must be configurable, not hardcoded
- API errors must be transformed into structured domain errors before propagating to callers
- Timeout errors must be caught and retried up to the configured maximum
- All retry attempts must be logged at WARNING level with attempt number and delay
- Final failure after exhausting retries must be logged at ERROR level with full context
- `news.py` must be deleted only after integration tests confirm `news_unified.py` handles all error scenarios correctly
- No changes to the public interface of `news_unified.py` — callers must not require updates

---

## Acceptance Criteria

- [ ] `news_unified.py` handles NewsAPI HTTP 429 response with retry and exponential backoff
- [ ] `news_unified.py` handles NewsAPI HTTP 500 response with retry
- [ ] `news_unified.py` handles NewsAPI HTTP 503 response with retry
- [ ] `news_unified.py` handles connection timeout with retry
- [ ] After exhausting retries, `news_unified.py` raises a structured domain error (not a raw `requests.HTTPError`)
- [ ] Error messages from `news_unified.py` match the format produced by the old `news.py` wrapper
- [ ] Retry attempts are logged at WARNING level with attempt count and backoff delay
- [ ] `news.py` is deleted
- [ ] All existing news-related unit tests pass against `news_unified.py`
- [ ] No import of `news.py` remains anywhere in the codebase

---

## Definition of Done

- **Tests Required**: Integration test that mocks NewsAPI to return 429 on first two calls and 200 on the third; verifies that the adapter retries exactly twice with increasing delay and returns the successful response. Separate test that mocks all retries as 429 and verifies a structured domain error is raised (not `requests.HTTPError`).
- **Documentation Required**: Inline docstring on the error handling wrapper explaining the retry strategy and which HTTP status codes trigger retry.
- **Code Review Gate**: Reviewer must compare error handling logic line-by-line with `news.py`'s `AdditionalDataSources` wrapper and confirm behavioral equivalence. Reviewer must verify `news.py` is absent from the repository after merge.

---

## Notes

The temptation will be to add a generic retry decorator and call it done. Resist this. The old wrapper was specific: it knew which status codes to retry, it knew the backoff profile that works with NewsAPI's rate limiting behavior, and it knew how to transform the error into something the research pipeline could handle. A generic decorator will pass the tests and miss the point.

The deletion of `news.py` is not optional. If both files exist after this story closes, the story is not done. The whole purpose of this work is to eliminate the parallel versions, not to add a third.

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
