# STORY-293: Add revenue sanity checks in aggregation

| Field | Value |
|-------|-------|
| **Epic** | EPIC-074 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add revenue sanity checks in the aggregation layer: cap revenue at industry-appropriate maximum (EUR 500B for energy majors), flag outliers more than 3 sigma from peer group mean.

## Acceptance Criteria

- [ ] Revenue values capped at EUR 500B (energy major ceiling)
- [ ] Outliers >3 sigma flagged in enrichment result metadata
- [ ] Zero revenue values do not pass validation as 'real' data
