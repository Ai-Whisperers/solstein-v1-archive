# STORY-212: Migrate web acquisition connectors to runtime contracts

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-055](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Core acquisition connectors still bypass common contract wrapper and failure semantics.

## Affected Files
- `src/solstein/data/web_research_pipeline.py`
- `src/solstein/data/connectors/lookup_service.py`
- `src/solstein/data/enrichment_service.py`

## Acceptance Criteria
- Acquisition connectors return typed runtime envelope in all outcomes.
- No silent failures remain in migrated connector paths.
- Integration tests cover degraded and failure envelope branches.

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
