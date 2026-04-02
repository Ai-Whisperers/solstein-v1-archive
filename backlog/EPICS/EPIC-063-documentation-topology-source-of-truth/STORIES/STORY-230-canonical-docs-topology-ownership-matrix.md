# STORY-230: Define Canonical Docs Topology and Ownership Matrix

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-063 Documentation Topology and Source-of-Truth Governance |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

Documentation directories are extensive and partially overlapping. Owners and canonical paths are not consistently explicit.

## Acceptance Criteria

- [ ] Canonical docs topology map is published with clear boundaries for `docs`, `backlog`, and generated artifacts.
- [ ] Document classes are defined (`maintained`, `generated`, `template`, `archived`) with class-specific governance scope.
- [ ] Directory-level ownership matrix exists with at least one accountable owner per top-level area.
- [ ] New-doc creation rules include canonical placement examples.
- [ ] Class-to-owner and class-to-review-cadence mapping is defined.

## Definition of Done

- [ ] Topology and ownership documents are linked from `docs/DOCUMENTATION_INDEX.md`.
- [ ] Governance handoff notes explicitly delegate review workflow concerns to STORY-240.

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
