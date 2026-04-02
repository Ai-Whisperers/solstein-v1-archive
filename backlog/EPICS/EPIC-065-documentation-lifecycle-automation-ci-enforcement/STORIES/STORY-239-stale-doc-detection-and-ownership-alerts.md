# STORY-239: Add Stale-Doc Detection and Ownership Alerts

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Stale documentation is not systematically identified, escalated, or reviewed.

## Acceptance Criteria

- [ ] Staleness policy is defined by document class and review interval.
- [ ] Automated stale-doc detector emits actionable report.
- [ ] Ownership mapping is used to route notifications.
- [ ] Escalation path exists for unowned documents.
- [ ] Exceptions to staleness policy use the same `owner`, `rationale`, and `expiry` model used in STORY-234 and STORY-238.

## Definition of Done

- [ ] Weekly stale-doc report is generated and stored.
- [ ] Alert routing is verified for at least one stale-doc scenario.

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
