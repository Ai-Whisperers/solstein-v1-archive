# STORY-295: Cross-validate revenue across 2+ sources

| Field | Value |
|-------|-------|
| **Epic** | EPIC-074 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Cross-validate revenue values across 2+ enrichment sources before accepting a high-confidence value. If sources disagree by >20%, mark confidence as medium and log the discrepancy.

## Acceptance Criteria

- [ ] Revenue accepted as high-confidence only when 2+ sources agree within 20%
- [ ] Discrepancies logged with both source values
- [ ] Single-source revenue marked as medium confidence
