# STORY-243: Generate Master Audit Issue Index and Keep It Current

| Field | Value |
|---|---|
| **Status** | 🟡 In Progress |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | High |

---

## Problem Statement

The master audit is the historical source of truth, but it is expensive to re-read and unsafe to manually duplicate. The repo needs a generated issue index that preserves the source audit while making the full inventory cheaply queryable.

## Acceptance Criteria

- [x] A generated markdown issue index exists under `docs/audit/generated/`.
- [x] A generated JSON issue index exists for machine consumers.
- [x] The generator deduplicates repeated issue table rows by issue identifier.
- [x] The generated artifact records the source line count and declared tracker totals.
- [ ] The generated artifact is cross-linked from future fix-verification audits.

## Definition of Done

- [x] The master audit remains unedited by the generator.
- [x] `docs-generated-check` fails when the committed index is stale.
- [ ] Fix-verification audits explicitly reconcile against the generated issue index.

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
