# STORY-198: Enforce Provenance Completeness at Enrichment Write Boundary

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - High |
| **Epic** | EPIC-052 Provenance, Confidence, and Quality Gates |
| **Created** | 2026-03-30 |
| **Dependencies** | EPIC-050, EPIC-051, EPIC-003 |

## Problem Statement

Enrichment writes can still allow partially described facts to cross the write boundary without complete provenance. That makes later quality decisions unverifiable.

## Acceptance Criteria

- [ ] Every non-null enriched field written through the target boundary carries source, timestamp, and confidence metadata or an explicit unavailable marker.
- [ ] Malformed provenance payloads fail deterministically instead of being silently normalized.
- [ ] The gate result is observable in tests and error/reporting surfaces.

## Definition of Done

- [ ] Boundary validator exists at the write edge.
- [ ] Pass and fail regression cases exist.
- [ ] Future agents can locate the boundary from code and generated/reference docs.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This file was created in the 2026-03-30 autonomy pass because EPIC-052 previously lacked canonical story artifacts.

### Next Agent Action

- Implement the provenance completeness gate only at the write boundary; do not mix calibration or pre-scoring policy work into this story.

### Required Working Style

- Use `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` as the boundary map.
- Prefer strict typed validation over loose dict normalization.

### Minimum Verification For Future Agents

- Add one pass case and one fail case.
- Show the malformed payload is rejected at the intended boundary.
