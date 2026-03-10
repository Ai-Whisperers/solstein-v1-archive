# STORY-221: Add recipe versioning, promotion rules, and rollback controls

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-057](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Recipe changes are difficult to compare, promote, and roll back safely.

## Affected Files
- `src/solstein/research/config.py`
- `src/solstein/research/pipeline.py`

## Acceptance Criteria
- Recipe versions are stored with promotion metadata.
- Rollback to prior recipe version requires config change only.
- Batch outputs include recipe id and version for traceability.
