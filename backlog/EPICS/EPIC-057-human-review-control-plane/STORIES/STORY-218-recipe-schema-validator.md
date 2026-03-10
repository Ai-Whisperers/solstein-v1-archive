# STORY-218: Define recipe schema and validator

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-057](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Research orchestration parameters are distributed across code paths, limiting repeatability.

## Affected Files
- `src/solstein/research/config.py`
- `src/solstein/research/pipeline_stages.py`

## Acceptance Criteria
- Recipe schema defines stages, constraints, and policies with versioning.
- Validator reports field-level errors with remediation hints.
