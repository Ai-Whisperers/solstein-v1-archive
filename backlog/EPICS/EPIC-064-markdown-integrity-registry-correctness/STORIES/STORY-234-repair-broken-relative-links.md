# STORY-234: Repair Broken Relative Links and Establish Baseline Report

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | L (1 week) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

Broken links prevent reliable navigation and can invalidate operational runbooks.

## Acceptance Criteria

- [ ] A reproducible link-check command is documented.
- [ ] All broken relative links in scoped trees are fixed or explicitly allowlisted.
- [ ] Link exceptions require `owner`, `rationale`, and `expiry` metadata.
- [ ] Post-fix report includes before/after counts.

## Definition of Done

- [ ] CI link check passes on target branches.
- [ ] No unresolved high-severity broken links remain.

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
