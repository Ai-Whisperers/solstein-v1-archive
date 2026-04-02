# STORY-116: Centralize All Retry/Backoff in core/retry_policy.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-031: Shared Library & Architecture |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `src/solstein/core/retry_policy.py` exists as the intended central retry module. Individual adapter files (`data/yahoo_finance.py`, news adapters, `agents/`) implement their own retry logic independently — different backoff strategies, different max retry counts, different exception types caught.

## Problem Statement

The retry policy module exists. Nobody uses it. Instead, individual adapters implement their own retry logic with different semantics — some retry on any exception, some only on network errors, some use exponential backoff, some use linear. The result is a platform where Yahoo Finance retries 5 times with 1-second linear delays, NewsAPI retries 3 times with exponential backoff, and some adapters don't retry at all. This inconsistency makes operational behavior unpredictable and makes testing retry behavior a per-adapter exercise. The central module is doing no work while 15 places reinvent it.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Retry changes require touching 15+ files |
| **Reliability** | Inconsistent retry semantics across services |
| **Testability** | Retry behavior untestable from central point |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/core/retry_policy.py` | Exists but unused |
| `data/yahoo_finance.py` | Independent retry implementation |
| `data/news_unified.py` | Independent retry implementation |
| All adapter files | Scattered retry logic |

## Architectural Requirements

- `core/retry_policy.py` defines the canonical retry decorator/context manager
- Retry configuration: max_retries, backoff_base, backoff_max, jitter, retryable_exceptions — all configurable per call site
- Default profiles: `NETWORK_DEFAULT` (3 retries, exp backoff 1-30s), `RATE_LIMIT` (5 retries, exp backoff 5-60s), `STRICT` (1 retry, no backoff — for idempotent writes)
- All adapter retry logic replaced with `@retry_policy(profile=NETWORK_DEFAULT)` or equivalent
- Independent retry implementations DELETED from all adapters
- Circuit breaker integration: after N consecutive failures, circuit opens and retries are skipped (plugs into `resilience.py`)
- Retry metrics emitted per call site: attempt count, final outcome (success/failure), total duration

## Acceptance Criteria

- [ ] `grep -r "tenacity\|retry_count\|for attempt in range" src/solstein/` returns only `core/retry_policy.py`
- [ ] All adapters use `core/retry_policy.py` for retry logic
- [ ] Retry behavior configurable without modifying adapter code
- [ ] Circuit breaker wired to retry policy
- [ ] Retry metrics logged in structured format

## Definition of Done

- **Tests Required**: Unit tests for each retry profile
- **Documentation Required**: Retry policy usage guide
- **Code Review Gate**: Reviewer verifies zero independent retry implementations remain

## Notes

This consolidates 15+ implementations into one canonical module.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `READY`.

### Next Agent Action

- Use this as the preferred EPIC-031 entry story.
- Centralize one retry ownership model without bundling unrelated shared-package or CLI work.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Remove duplicate retry logic only where the canonical policy can replace it with verifiable parity.

### Minimum Verification For Future Agents

- Prove the maintained retry policy is used at the touched call sites.
- Run targeted regression tests plus relevant strict checks after the refactor.
