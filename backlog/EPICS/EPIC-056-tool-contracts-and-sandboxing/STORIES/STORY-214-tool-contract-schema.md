# STORY-214: Detect and escalate critical contradictory claims

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P0 |
| **Size** | L (2-3 days) |
| **Epic** | [EPIC-056](README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Critical claims can conflict across sources without deterministic escalation.

## Affected Files
- `src/solstein/data/enrichment/conflict_resolver.py`
- `src/solstein/analytics/data_quality.py`
- `src/solstein/data/enrichment/orchestrator.py`

## Acceptance Criteria
- Contradictions on critical fields (`revenue`, `employee_count`, `funding_total`, `valuation`) create escalation events.
- Escalation payload includes conflicting claims, sources, and confidence.
- Escalations are persisted and queryable.
