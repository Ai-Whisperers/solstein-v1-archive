# STORY-088: Fix In-Memory DLQ — Persist to PostgreSQL

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-025: Worker Reliability |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict
> `src/solstein/worker_tasks.py:104-127` — `DeadLetterQueue` class stores failed tasks in a Python list (`self._queue = []`). On worker restart, this list is garbage-collected. Every failed task is permanently lost.

## Problem Statement

The in-memory DLQ is not a DLQ. It is a temporary staging area for task failures that disappears at the worst possible moment — when a worker crashes. A research job that fails due to a transient API rate limit is silently dropped, the data is never collected, and no one is notified.

The platform's data freshness guarantee is a fiction built on top of a list that doesn't survive a process restart. There is no admin interface to inspect failures, no alerting on accumulation, and no retry mechanism beyond the initial `max_retries=3` on the task itself.

For a competitive intelligence platform that promises timely data, losing failed tasks without a trace is not a minor inconvenience — it is a fundamental breach of the system's contract with its users.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Failed tasks are permanently lost on worker restart — no recovery path exists |
| **Operational** | No visibility into what failed or why; failures are invisible until someone notices stale data |
| **Data Integrity** | Stale data propagates without detection; freshness guarantees are silently violated |
| **Developer Experience** | Debugging production failures requires reading ephemeral logs — if they haven't rotated out |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/worker_tasks.py:104-127` | `DeadLetterQueue` class uses in-memory Python list; lost on process exit |
| `src/solstein/celery_config.py` | No configuration for persistent failure tracking |

## Architectural Requirements
- A `failed_tasks` PostgreSQL table with columns: task_id (UUID PK), task_name (VARCHAR), queue_name (VARCHAR), args (JSONB), kwargs (JSONB), error_message (TEXT), traceback (TEXT), retry_count (INTEGER), tenant_id (VARCHAR, nullable), created_at (TIMESTAMPTZ), last_attempted_at (TIMESTAMPTZ), resolved_at (TIMESTAMPTZ, nullable), resolved_by (VARCHAR, nullable)
- All task failures must write a row to `failed_tasks` before the task terminates
- A `/api/v1/admin/dlq` endpoint to list, inspect, and manually re-queue DLQ entries
- Alerting threshold: alert when DLQ accumulates >10 unresolved entries in any 1-hour window
- The existing in-memory `DeadLetterQueue` class must be deleted entirely
- An Alembic migration must create the `failed_tasks` table
- DLQ write failures must not cause the original task to fail with a different error — log the DLQ write failure and continue with the original error propagation
- DLQ entries must be queryable by queue_name, task_name, time range, and resolution status

## Acceptance Criteria
- [ ] `failed_tasks` table exists and is populated on task failure
- [ ] Worker restart does not lose any DLQ entries
- [ ] Admin API returns paginated DLQ entries filterable by queue, task_name, time range
- [ ] Manual re-queue from admin API creates a new Celery task and marks DLQ entry as resolved
- [ ] In-memory `DeadLetterQueue` class is deleted from codebase
- [ ] Alembic migration is present and reversible

## Definition of Done
- **Tests Required**: Integration test covering task failure → DLQ write → worker restart → DLQ entry still present. Unit tests for DLQ query filters and re-queue logic.
- **Documentation Required**: Update worker README with DLQ admin API usage. Document alerting threshold configuration.
- **Code Review Gate**: Reviewer must verify DLQ write cannot cascade-fail the task. Reviewer must confirm Alembic migration is reversible.

## Notes
- This story supersedes the DLQ concept introduced in STORY-087 (EPIC-018). STORY-087 identified the gap; this story delivers the full persistent implementation.
- The DLQ write path must be resilient to PostgreSQL connection failures — use a separate short-lived connection or connection pool, not the main application pool, to avoid coupling DLQ durability to application DB health.
- Consider indexing `(resolved_at IS NULL, created_at DESC)` for the admin list endpoint's default query pattern.
