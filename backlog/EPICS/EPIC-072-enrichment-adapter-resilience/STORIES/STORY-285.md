# STORY-285: FundingEnrichment: implement Crunchbase-free fallback using GDELT + web scraping

| Field | Value |
|-------|-------|
| **Epic** | EPIC-072 |
| **Priority** | P1 |
| **Size** | L |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

FundingEnrichment relies on CrunchBase API which requires a paid key. Implement a fallback that uses GDELT news search + web scraping to detect funding rounds from press releases and news articles.

## Acceptance Criteria

- [ ] FundingEnrichment produces results without CrunchBase API key
- [ ] GDELT fallback detects funding rounds from news mentions
- [ ] Funding amounts extracted from news have `confidence < 0.5`
- [ ] Known funding rounds (seed, Series A/B) are correctly classified
