# STORY-281: Add CrunchBase slugs for startups/funded companies

| Field | Value |
|-------|-------|
| **Epic** | EPIC-071 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add CrunchBase organization slugs to catalog companies that appear on CrunchBase (primarily startups and VC-backed companies). This enables the funding enrichment adapter to fetch funding rounds.

## Acceptance Criteria

- [ ] All startup/funded catalog companies have a `crunchbase_slug` field
- [ ] Slugs resolve to valid crunchbase.com/organization/slug pages
- [ ] Companies not on CrunchBase have `crunchbase_slug = None`

## Technical Notes

- File: `src/solstein/data/market_catalogs.py`
- Pure data entry — no logic changes
