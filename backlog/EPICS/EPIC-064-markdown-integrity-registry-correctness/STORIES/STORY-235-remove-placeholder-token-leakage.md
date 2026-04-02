# STORY-235: Eliminate Placeholder Token Leakage in Active Docs

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Template placeholders are present in maintained docs, signaling incomplete or misleading content.

## Acceptance Criteria

- [ ] Placeholder scan rules are defined for active documentation trees.
- [ ] Tokens (`EPIC-XXX`, `STORY-XXX`, `ADR-XXX`, `FD-XXX`, `TODO:`, `TBD`) are removed or quarantined.
- [ ] Template-only directories are explicitly scoped to avoid false positives.
- [ ] Post-remediation scan output is attached to change log.

## Definition of Done

- [ ] Active docs scan returns zero unresolved placeholder tokens.
- [ ] Token policy is documented for contributors.

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
