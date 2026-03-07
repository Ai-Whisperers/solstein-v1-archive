# STORY-090: Implement Task Idempotency via Deduplication Lock

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-025: Worker Reliability |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-089 (must deploy together — acks_late creates the at-least-once semantics that require idempotency) |

## The Audit Verdict
> `src/solstein/celery_config.py` — no idempotency mechanism exists. Celery Beat can double-fire tasks on scheduler restart. Combined with STORY-089 (at-least-once delivery), tasks can execute multiple times for the same logical operation.

## Problem Statement

Once `task_acks_late` is enabled (STORY-089), tasks become at-least-once. Without idempotency, "at-least-once" becomes "sometimes twice, occasionally more." Beat scheduler restarts are not rare events — they happen on every deploy. When Beat restarts mid-schedule, it re-fires any task whose scheduled time just passed.

For tasks that write to the database (all 12 of them), duplicate execution means duplicate rows, conflicting updates, and corrupted aggregate scores. A company's competitive score computed twice with slightly different timing windows produces two different results — and whichever one writes last wins, regardless of correctness.

The platform needs at-most-once-per-logical-period semantics on top of at-least-once delivery. This is a standard distributed systems pattern: use a distributed lock keyed to the logical operation, not the physical task invocation.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Duplicate research records created on every deploy that restarts Beat |
| **Operational** | Conflicting concurrent writes on same company data produce non-deterministic results |
| **Data Integrity** | Aggregate scores corrupted by duplicate computations with different timing |
| **Developer Experience** | "Works locally" because local dev rarely restarts Beat mid-schedule |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/worker_tasks.py` | No idempotency checks on any task — all 12 tasks are vulnerable to duplicate execution |
| `src/solstein/celery_config.py` | No global idempotency configuration |
| Redis | Used as lock backend — no lock keys currently exist |

## Architectural Requirements
- A Redis-based distributed lock per `(task_name, idempotency_key)` acquired before task execution begins
- Idempotency key is derived from task arguments (e.g., `company_id + schedule_period`) — the derivation function must be documented per task type
- Lock TTL must be >= the task's `time_limit` to prevent concurrent duplicate execution while the original is still running
- Lock must be released on task completion (both success and failure paths)
- Tasks that fail to acquire the lock must log a WARNING and return early — this is not an error condition, it is expected behavior during Beat restarts
- Beat tasks must include the scheduled period (e.g., `2026-03-01T09:00`) in the idempotency key so that the same task can run in the next period without being blocked by a stale lock
- Lock implementation must handle Redis connection failures gracefully — if Redis is down, the task should execute (fail-open) rather than silently skip, with a WARNING log
- The lock mechanism should be implemented as a decorator or base class mixin, not copy-pasted into each task

## Acceptance Criteria
- [ ] Concurrent duplicate task execution is prevented by Redis lock
- [ ] Lock acquisition failure produces a WARNING log, not an error
- [ ] Beat restart does not cause duplicate data writes
- [ ] Lock TTL is configurable per-task based on expected duration
- [ ] Idempotency key derivation is documented for each task type
- [ ] Lock is released on both success and failure paths
- [ ] Redis unavailability causes fail-open behavior with WARNING log

## Definition of Done
- **Tests Required**: Unit tests for lock acquisition, release, TTL expiry, and fail-open behavior. Integration test: fire same task twice concurrently, verify exactly one execution produces database writes.
- **Documentation Required**: Document idempotency key derivation for all 12 tasks. Document fail-open vs. fail-closed decision and rationale.
- **Code Review Gate**: Reviewer verifies TTL > time_limit for all tasks. Reviewer verifies lock release in both success and exception paths (no lock leaks).

## Notes
- The fail-open decision is deliberate: a brief Redis outage should not halt all data collection. Duplicate execution during Redis downtime is preferable to zero execution. The DLQ (STORY-088) provides the safety net for any resulting data issues.
- Consider using `redis-py`'s `Lock` class with `blocking=False` rather than a hand-rolled SETNX implementation. The built-in Lock handles edge cases (owner verification, atomic release) that manual implementations typically miss.
- Idempotency key granularity matters. Too coarse (just `task_name`) and tasks block across unrelated companies. Too fine (include `request_id`) and the lock never deduplicates anything. The sweet spot is `task_name + primary_entity_id + schedule_period`.
