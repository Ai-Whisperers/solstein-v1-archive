# STORY-170: Replace Fake Health Check with Real DB Probe

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 |
| **Size** | S |
| **Epic** | [EPIC-044: Quick Wins](../README.md) |
| **Created** | 2026-03-01 |
| **Risk** | Low |

---

## Audit Verdict

> `monitoring.py` lines 96, 127 call `asyncio.sleep(0.01)` and report success — they verify nothing.

---

## Problem Statement

The health check endpoint returns 200 OK even when the database is down. This masks outages and prevents proper alerting.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Health checks actually reflect system health |
| **Operations** | Alerts fire when database is down |
| **Debugging** | Can trust health endpoint for troubleshooting |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/monitoring.py` | Modify | Replace sleep with DB query |
| `tests/unit/test_health.py` | Modify | Test failure scenarios |

---

## Architectural Requirements

- **REQ-1**: Health check performs actual database query (`SELECT 1`)
- **REQ-2**: Returns 503 if database is unreachable
- **REQ-3**: Response time <100ms (fast fail)

---

## Acceptance Criteria

- [ ] Health check returns 200 when DB is up
- [ ] Health check returns 503 when DB is down
- [ ] Response time <100ms

---

## Definition of Done

- [ ] Real DB probe implemented
- [ ] Tests for both success and failure
- [ ] Deployed and verified

---

## Notes

Also addresses STORY-047 (full implementation). This quick win is the MVP version.

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
