# STORY-216: Enforce scoring/export hold for unresolved critical claims

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P0 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-056](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Critical unresolved contradictions can still leak into scoring/export paths.

## Affected Files
- `src/solstein/analytics/scoring.py`
- `src/solstein/research/pipeline_stages.py`
- `src/solstein/data/enrichment/orchestrator.py`

## Acceptance Criteria
- Scoring/export stages block unresolved critical claims by policy.
- Override path requires recorded adjudication decision.
- Block/override decisions are visible in run journal.
