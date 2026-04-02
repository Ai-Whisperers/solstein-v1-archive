# STORY-206: Define typed state contract for orchestration graph

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-054](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Pipeline stages pass loosely structured data, increasing transition bugs and making resume logic brittle.

## Affected Files
- `src/solstein/research/pipeline_stages.py`
- `src/solstein/research/pipeline.py`
- `src/solstein/research/pipeline_async.py`

## Architectural Requirements
- Define a canonical typed state model for stage inputs/outputs.
- Validate state at each stage boundary.

## Acceptance Criteria
- State schema exists and is imported by all core stage executors.
- Invalid stage output fails fast with structured error.
- Unit tests cover schema validation failure cases.

## Definition of Done
- Tests added and passing.
- Documentation updated in epic README.

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
