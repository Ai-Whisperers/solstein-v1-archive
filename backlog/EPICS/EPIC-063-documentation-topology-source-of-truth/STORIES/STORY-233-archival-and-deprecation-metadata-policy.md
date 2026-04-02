# STORY-233: Establish Archival and Deprecation Metadata Policy

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P2 - Medium |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-063 Documentation Topology and Source-of-Truth Governance |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Archived and superseded docs are not consistently labeled with lifecycle metadata and successor pointers.

## Acceptance Criteria

- [ ] Standard metadata keys are defined (`status`, `owner`, `last_reviewed`, `superseded_by`).
- [ ] Archival rules define when and how docs move to archive areas.
- [ ] Superseded docs require successor links or explicit rationale.
- [ ] Policy includes machine-checkable front-matter requirements.

## Definition of Done

- [ ] Metadata standard is documented and approved.
- [ ] At least one automated check design is included in policy.

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
