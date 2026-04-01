# STORY-209: Add replay diagnostics for failed runs

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-054](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Failure triage is slow because stage-level transition history is incomplete.

## Affected Files
- `src/solstein/research/pipeline.py`
- `src/solstein/monitoring/errors.py`

## Architectural Requirements
- Persist transition history with node, input hash, output summary, duration.

## Acceptance Criteria
- Replay report reconstructs full transition path for failed run id.
- Diagnostics include failing node and upstream context.
