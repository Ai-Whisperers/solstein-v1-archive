# STORY-284: GlobalMarketEnrichment: fall back to sector ETF data when no ticker

| Field | Value |
|-------|-------|
| **Epic** | EPIC-072 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

GlobalMarketEnrichment currently fails for private companies (no ticker). Add a fallback that uses sector ETF data to provide market context (sector performance, peer group metrics) when individual ticker data is unavailable.

## Acceptance Criteria

- [ ] GlobalMarketEnrichment produces output for companies without tickers
- [ ] Sector ETF fallback uses appropriate ETF for the company's industry
- [ ] Result is clearly marked as sector-level (not company-level) data
- [ ] Confidence ≤ 0.3 for ETF fallback data
