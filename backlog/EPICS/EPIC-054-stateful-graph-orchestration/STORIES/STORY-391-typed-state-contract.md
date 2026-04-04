# STORY-391: Define typed state contract for orchestration graph

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
