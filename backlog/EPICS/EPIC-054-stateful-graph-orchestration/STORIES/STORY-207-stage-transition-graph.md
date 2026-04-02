# STORY-207: Convert stage flow to explicit transition graph

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | L (2-3 days) |
| **Epic** | [EPIC-054](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Stage order and branching are currently implicit in code paths, making behavior hard to verify.

## Affected Files
- `src/solstein/research/pipeline.py`
- `src/solstein/research/pipeline_stages.py`
- `src/solstein/research/ai_research_orchestrator.py`

## Architectural Requirements
- Represent primary flow as explicit graph transitions.
- Preserve existing stage logic, only refactor control flow.

## Acceptance Criteria
- Graph transition map is declared and unit tested.
- All legacy stages are mapped to graph nodes.
- Unsupported transitions fail with explicit error.

## Definition of Done
- Transition docs added.
- Regression tests prove output parity.

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
