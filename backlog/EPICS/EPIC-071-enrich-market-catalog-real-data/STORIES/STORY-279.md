# STORY-279: Add LinkedIn company slugs to all catalog companies

| Field | Value |
|-------|-------|
| **Epic** | EPIC-071 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add LinkedIn company page slugs to all Dutch Energy catalog companies for use by the LinkedIn enrichment adapter.

## Acceptance Criteria

- [ ] All 24 catalog companies have a `linkedin_slug` field
- [ ] Slugs resolve to valid LinkedIn company pages
- [ ] Companies with no LinkedIn presence have `linkedin_slug = None`

## Technical Notes

- File: `src/solstein/data/market_catalogs.py`
- Pure data entry — no logic changes
