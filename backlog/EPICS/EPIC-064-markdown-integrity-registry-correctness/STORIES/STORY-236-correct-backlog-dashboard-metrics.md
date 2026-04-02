# STORY-236: Correct Backlog Registry and Dashboard Metric Inconsistencies

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

`backlog/README.md` contains conflicting dashboard rows and non-authoritative totals.

## Acceptance Criteria

- [ ] Dashboard metric definitions are documented with formulas.
- [ ] Duplicate/contradictory rows are removed.
- [ ] Metric generation is automated from epic/story source data.
- [ ] A canonical metrics artifact is published and treated as the only source for docs health consumers.
- [ ] Story and epic counts in README match generated output.

## Definition of Done

- [ ] One command regenerates metrics and updates dashboard sections.
- [ ] Validation check fails if displayed counts diverge from source-of-truth.

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
