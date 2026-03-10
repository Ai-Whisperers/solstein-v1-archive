# STORY-219: Implement recipe-to-plan compilation with deterministic hashing

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-057](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Execution plans are generated ad hoc, making output comparisons and rollback difficult.

## Affected Files
- `src/solstein/research/pipeline.py`
- `src/solstein/research/pipeline_async.py`

## Acceptance Criteria
- Compiler produces deterministic plan from recipe + inputs.
- Plan hash is stable for identical recipe/input combinations.
- Plan hash is persisted in run metadata.
