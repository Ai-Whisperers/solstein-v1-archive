# STORY-216: Enforce scoring/export hold for unresolved critical claims

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P0 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-056](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Critical unresolved contradictions can still leak into scoring/export paths.

## Affected Files
- `src/solstein/analytics/scoring.py`
- `src/solstein/research/pipeline_stages.py`
- `src/solstein/data/enrichment/orchestrator.py`

## Acceptance Criteria
- Scoring/export stages block unresolved critical claims by policy.
- Override path requires recorded adjudication decision.
- Block/override decisions are visible in run journal.

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
