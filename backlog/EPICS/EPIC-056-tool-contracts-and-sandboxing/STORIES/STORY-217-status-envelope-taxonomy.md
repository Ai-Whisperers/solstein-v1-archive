# STORY-217: Update merge strategy from adjudication outcomes

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-056](README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Adjudication decisions are not consistently reflected in downstream merge/confidence behavior.

## Affected Files
- `src/solstein/data/enrichment/conflict_resolver.py`
- `src/solstein/data/provenance.py`
- `src/solstein/analytics/data_quality.py`

## Acceptance Criteria
- Approved/rejected/overridden claim outcomes alter merge preference weights.
- Confidence adjustments are deterministic and traceable to decision IDs.
- Regression tests verify merge behavior change on adjudication input.
