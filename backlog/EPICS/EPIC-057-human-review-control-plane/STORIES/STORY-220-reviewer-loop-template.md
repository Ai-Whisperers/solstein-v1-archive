# STORY-220: Add producer-reviewer loop template with bounded retries

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-057](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Low-quality outputs are not consistently routed through iterative correction loops.

## Affected Files
- `src/solstein/agents/coordinator_agent.py`
- `src/solstein/research/pipeline_stages.py`

## Acceptance Criteria
- Producer-reviewer loop template exists and is reusable by recipes.
- Loop retries are bounded by policy and terminate deterministically.
- Failed loops route to human review stage.
