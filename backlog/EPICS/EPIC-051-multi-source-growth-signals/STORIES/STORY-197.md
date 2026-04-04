# STORY-197: Implement source fallback matrix (premium/free/degraded)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-051 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 Not Started |
| **Dependencies** | STORY-194, STORY-195, STORY-196 |

## Description

Define and implement the source fallback matrix for growth signals: for each signal family (hiring, product, funding), specify the ordered list of sources by tier (premium → free → degraded/estimated).

## Acceptance Criteria

- [ ] Fallback matrix defined as configuration (not hardcoded)
- [ ] Each signal family has ≥ 2 fallback sources
- [ ] Premium sources (LinkedIn API, Crunchbase) tried first if configured
- [ ] Free/scraping sources used as fallback
- [ ] "degraded" tier provides explicit unknown/low-confidence signal (no fabrication)
- [ ] Matrix coverage: 100% of required growth fields have at least one free-tier fallback
