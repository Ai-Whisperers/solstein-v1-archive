# STORY-207: Convert stage flow to explicit transition graph

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | L (2-3 days) |
| **Epic** | [EPIC-054](README.md) |
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
