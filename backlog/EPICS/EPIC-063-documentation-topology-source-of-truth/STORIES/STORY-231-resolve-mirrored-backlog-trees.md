# STORY-231: Resolve Mirrored Backlog Trees with One-Way Sync or Migration

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1 week) |
| **Epic** | EPIC-063 Documentation Topology and Source-of-Truth Governance |
| **Created** | 2026-03-11 |
| **Risk** | High |

---

## Problem Statement

`docs/active/backlog` and `backlog/EPICS` contain mirrored markdown content with proven drift.

## Acceptance Criteria

- [ ] Canonical tree is selected and documented.
- [ ] Non-canonical tree strategy is defined (generated mirror, one-way sync, or retirement).
- [ ] Cutover control is defined for non-canonical edits (block, redirect, or alert) during transition.
- [ ] Drift detection rule is specified, with implementation delegated to STORY-237.
- [ ] Migration/synchronization dry-run report is produced before execution.

## Definition of Done

- [ ] No unresolved design ambiguity remains on source-of-truth policy.
- [ ] Script design for sync/migration is reviewed and approved.
- [ ] Temporary anti-drift control is approved before migration starts.

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
