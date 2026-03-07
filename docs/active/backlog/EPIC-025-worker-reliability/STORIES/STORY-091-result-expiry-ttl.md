# STORY-091: Set Result Expiry TTL to Prevent Redis Bloat

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Medium |
| **Epic** | EPIC-025: Worker Reliability |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict
> `src/solstein/celery_config.py` — `result_expires` is NOT SET. Celery task results accumulate in Redis indefinitely. A long-running platform will exhaust Redis memory and begin evicting keys, causing silent data loss in the result backend.

## Problem Statement

Every Celery task result — whether the caller ever reads it or not — is written to Redis and left there forever. Most callers poll `AsyncResult(task_id).status` exactly once. The result is then orphaned but never deleted. Over weeks of operation with 12 scheduled tasks running hourly, this is thousands of result keys accumulating in Redis.

When Redis hits its memory limit and starts evicting with LRU policy, it will evict result keys — meaning pollers who check too late get a `PENDING` status for a task that actually completed or failed hours ago. This is worse than a missing result: it's an actively misleading result that tells the caller "your task hasn't started yet" when in fact it finished and the evidence was garbage-collected.

The fix is a 24-hour TTL on all results. Simple, obvious, and the kind of thing that should have been set from day one.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Stale status reads after Redis eviction — `PENDING` returned for completed tasks |
| **Operational** | Redis memory exhaustion is inevitable given sufficient uptime; failure mode is silent |
| **Data Integrity** | Callers receive incorrect task status, potentially triggering redundant re-submissions |
| **Developer Experience** | Redis memory issues manifest as seemingly random `PENDING` statuses with no obvious cause |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/celery_config.py` | `result_expires` not set — results persist indefinitely in Redis |

## Architectural Requirements
- `result_expires = 86400` (24 hours) must be set in the Celery configuration
- Result TTL must be configurable via environment variable `CELERY_RESULT_EXPIRES_SECONDS` with a sensible default of 86400
- Documentation must state the polling contract: callers must poll within 24 hours of task completion or accept that the result may be expired
- Any long-running export tasks (see EPIC-030) that store output in the result backend must either complete within the TTL window or store their output in PostgreSQL instead
- The TTL must apply globally to all task results — per-task overrides are not required for the initial implementation but the architecture should not preclude them

## Acceptance Criteria
- [ ] `result_expires` set in celery_config with 24-hour default
- [ ] Result keys expire from Redis after configured TTL (verified by inspecting Redis key TTL)
- [ ] TTL is environment-variable configurable via `CELERY_RESULT_EXPIRES_SECONDS`
- [ ] Documentation notes the polling deadline for all result consumers

## Definition of Done
- **Tests Required**: Unit test verifying config value is present and defaults to 86400. Unit test verifying environment variable override works.
- **Documentation Required**: Update worker README with result TTL semantics. Document which callers poll results and their expected polling latency.
- **Code Review Gate**: Reviewer confirms all long-duration result consumers (export, enrichment, bulk analysis) complete within the TTL window. Reviewer verifies environment variable naming follows project conventions.

## Notes
- This is the lowest-risk story in EPIC-025. It can be deployed independently at any time.
- Before setting the TTL, it may be worth running `redis-cli --scan --pattern 'celery-task-meta-*' | wc -l` in production to quantify the current accumulation. Include this number in the PR description for posterity.
- If any caller relies on polling results older than 24 hours, that caller has a design problem that should be tracked as a separate story, not accommodated by extending the TTL to infinity.
