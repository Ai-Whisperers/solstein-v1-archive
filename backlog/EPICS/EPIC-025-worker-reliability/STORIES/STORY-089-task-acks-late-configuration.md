# STORY-089: Set task_acks_late and task_reject_on_worker_lost

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-025: Worker Reliability |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-090 (idempotency must be planned alongside; both can be implemented in parallel but must be deployed together) |

## The Audit Verdict
> `src/solstein/celery_config.py` — `task_acks_late` is NOT SET (defaults to False). Tasks are acknowledged to the broker immediately upon receipt, before execution begins. A worker crash between ack and completion drops the task permanently.

## Problem Statement

Default Celery behavior acknowledges tasks the moment a worker picks them up. If the worker then dies — OOM kill, SIGKILL, container eviction — the broker considers the task complete. It is not. The task never ran, the data was never collected, and the broker will never retry it.

For a platform whose data freshness depends on 12 scheduled tasks running reliably, this is an architectural hole that turns infrastructure hiccups into silent data rot. A Kubernetes pod eviction, a Docker container restart, a simple memory spike — any of these becomes an invisible data collection gap.

The fix is two configuration lines, but nobody set them. This is the kind of default that framework authors warn about in their documentation, and the kind of warning that gets skipped by developers who assume defaults are safe. They are not.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | P0 data loss on any worker crash — tasks are silently dropped with no recovery |
| **Operational** | No indication that tasks were dropped; monitoring shows "no failures" because the task never ran long enough to fail |
| **Data Integrity** | Freshness guarantees violated silently; data gaps appear without corresponding error signals |
| **Developer Experience** | Impossible to reproduce in dev (workers rarely crash locally); manifests only in production |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/celery_config.py` | `task_acks_late` not set — defaults to False (acknowledge on receipt) |

## Architectural Requirements
- `task_acks_late = True` must be set in the Celery configuration
- `task_reject_on_worker_lost = True` must be set in the Celery configuration
- `worker_prefetch_multiplier = 1` must be verified as compatible (it is — document this explicitly in config comments)
- All 12 Beat-scheduled tasks must be reviewed for idempotency safety before this goes live — at-least-once delivery is only safe with idempotent tasks (see STORY-090)
- Worker startup documentation must be updated to reflect the new acknowledgment semantics
- The interaction between `acks_late` and the DLQ (STORY-088) must be documented: a task that fails after late-ack will both write to DLQ and be nacked to the broker — clarify which retry path takes precedence

## Acceptance Criteria
- [ ] `task_acks_late = True` present in celery_config
- [ ] `task_reject_on_worker_lost = True` present in celery_config
- [ ] Tasks re-queued automatically on worker crash (integration test)
- [ ] No duplicate execution observed when worker completes normally
- [ ] Configuration comments explain the ack semantics and prefetch interaction

## Definition of Done
- **Tests Required**: Integration test: start task, SIGKILL worker mid-execution, verify task is re-queued and eventually completes on a surviving worker.
- **Documentation Required**: Update worker README with new ack semantics. Document the deployment requirement: STORY-089 and STORY-090 must deploy together.
- **Code Review Gate**: Reviewer must verify all 12 tasks are safe for at-least-once delivery. Reviewer must confirm `worker_prefetch_multiplier` is set appropriately.

## Notes
- This story and STORY-090 (idempotency) are a paired deployment. Enabling `acks_late` without idempotency guarantees creates a different class of bugs (duplicate execution). Deploy both or neither.
- The SIGKILL integration test is non-trivial to automate. Consider a pytest fixture that spawns a worker subprocess, sends SIGKILL after task receipt, and verifies the task reappears in the queue.
- `task_reject_on_worker_lost` ensures that when the connection to a worker is lost (not just when the task raises an exception), the task is rejected back to the broker rather than acked.

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
