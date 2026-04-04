# STORY-198: Enforce Provenance Completeness at Enrichment Write Boundary

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-052 Provenance, Confidence, Quality Gates |
| **Created** | 2026-04-01 |

## Problem Statement
Enrichment adapters can write data without source URL, timestamp, or confidence score. This means scoring and export may use unprovenanced data.

## Acceptance Criteria
- [ ] Every enrichment write path requires: source_url, retrieved_at, confidence_score
- [ ] Writes missing any field are rejected with a clear error
- [ ] Existing data without provenance is flagged (not deleted)
- [ ] Tests: at least 5 tests covering valid/invalid provenance at write boundary

## Implementation Notes
- Check `src/solstein/data/provenance.py` for existing provenance models
- Check `src/solstein/adapters/enrichment/` for write paths
- Do NOT modify `research/graph/` (FROZEN)
