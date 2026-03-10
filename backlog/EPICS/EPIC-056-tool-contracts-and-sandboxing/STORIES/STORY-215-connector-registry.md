# STORY-215: Implement decision model and adjudication API

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-056](README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Escalated claim conflicts lack a formal decision lifecycle and API contract.

## Affected Files
- `src/solstein/data/enrichment/models.py`
- `src/solstein/data/enrichment/orchestrator.py`
- `src/solstein/data/provenance.py`

## Acceptance Criteria
- Decision API supports approve/reject/override with rationale.
- Decision records include actor, timestamp, claim ids, and policy context.
- API idempotently handles repeated submissions.
