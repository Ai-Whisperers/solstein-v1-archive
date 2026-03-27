# Agent Cycle 039 — 2026-03-27

## Stories Completed

### STORY-089: At-least-once delivery (task_acks_late)
- **Status**: DONE → PR #131
- `task_acks_late=True` — tasks acked AFTER execution, not receipt
- `task_reject_on_worker_lost=True` — nack on connection loss for re-queue
- `worker_prefetch_multiplier=1` — limits in-flight unacked tasks to 1
- Inline documentation explains at-least-once semantics and why all three settings must ship together

### STORY-090: Redis deduplication lock
- **Status**: DONE → PR #131 (same PR as STORY-089)
- New module `src/solstein/worker/idempotency.py`
- `@deduplicate(ttl=N)` decorator wraps Celery tasks
- Lock key: `dlq:dedup:<task_name>:<sha256[:16]>` (time-bucketed default)
- Fail-open on Redis unavailability or lock.acquire() error — WARNING log + task executes
- Non-blocking: lock held → skip with WARNING (never queue)
- Lock released in `finally` block on both success and exception paths
- 21 unit tests, all passing

## Quality gates
- All pre-commit hooks passed (Agent Code Quality Checks, Code Smell Detection)
- ruff check: 0 errors
- No lazy imports, no bare excepts, all params ≤5

## PRs
- PR #131: `feature/STORY-089-090-acks-late-idempotency` → develop

## QUEUE.md
- STORY-089: READY → DONE | PR #131
- STORY-090: READY → DONE | PR #131
- STORY-092: BLOCKED → READY (all dependencies satisfied)

## Next
- STORY-092: Merge worker_tasks_v2.py — Eliminate Duplicate Task Files (now READY)
