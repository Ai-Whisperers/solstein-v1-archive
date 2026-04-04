# STORY-282: YahooFinanceEnrichment: fall back to web scraping when no ticker available

| Field | Value |
|-------|-------|
| **Epic** | EPIC-072 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-277 |

## Description

YahooFinanceEnrichment currently raises ValueError when no ticker is provided. Add a fallback that attempts to find the ticker via web scraping or name-based search when the ticker field is empty.

## Acceptance Criteria

- [ ] YahooFinanceEnrichment does not raise ValueError for missing ticker
- [ ] Fallback successfully finds tickers for at least 50% of untickered test companies
- [ ] Result has `confidence < 0.5` when using fallback path
- [ ] Raises specific `EnrichmentFallbackError` if all paths fail (not ValueError)
