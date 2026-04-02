# STORY-214: Detect and escalate critical contradictory claims

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P0 |
| **Size** | L (2-3 days) |
| **Epic** | [EPIC-056](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Critical claims can conflict across sources without deterministic escalation.

## Affected Files
- `src/solstein/data/enrichment/conflict_resolver.py`
- `src/solstein/analytics/data_quality.py`
- `src/solstein/data/enrichment/orchestrator.py`

## Acceptance Criteria
- Contradictions on critical fields (`revenue`, `employee_count`, `funding_total`, `valuation`) create escalation events.
- Escalation payload includes conflicting claims, sources, and confidence.
- Escalations are persisted and queryable.

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
