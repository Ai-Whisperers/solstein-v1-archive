# STORY-277: Add website URLs to all 24 Dutch Energy catalog companies

| Field | Value |
|-------|-------|
| **Epic** | EPIC-071 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add `website_url` field to all 24 Dutch Energy catalog companies in `market_catalogs.py`. Research each company's official website URL.

## Acceptance Criteria

- [ ] All 24 Dutch Energy catalog companies have a non-null `website_url`
- [ ] URLs are verified (return HTTP 200 or redirect to working page)
- [ ] URLs use HTTPS where available

## Technical Notes

- File: `src/solstein/data/market_catalogs.py` (Dutch Energy market catalog)
- Pure data entry — no logic changes
