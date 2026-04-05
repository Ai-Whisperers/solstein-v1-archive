# EPIC-072: Fix Enrichment Adapter Resilience

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Effort** | M (3–5 days) |
| **Stories** | 5 ([STORY-282](STORIES/STORY-282.md) through [STORY-286](STORIES/STORY-286.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, DoD; clarified cross-epic deps) |

## Context

Enrichment adapters fail hard when data is missing or unavailable instead of returning partial data with reduced confidence. YahooFinance raises ValueError when no ticker is provided. Website enrichment fails when no URL is given. This prevents any company without pre-filled metadata from being enriched at all.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-282](STORIES/STORY-282.md) | YahooFinanceEnrichment: fall back to web scraping when no ticker available | 🔴 READY | Deps: STORY-277 |
| [STORY-283](STORIES/STORY-283.md) | WebsiteEnrichment: auto-discover website URL from company name via SearXNG when not provided | 🔴 READY | Deps: none |
| [STORY-284](STORIES/STORY-284.md) | GlobalMarketEnrichment: fall back to sector ETF data when no ticker | 🔴 READY | Deps: none |
| [STORY-285](STORIES/STORY-285.md) | FundingEnrichment: implement Crunchbase-free fallback using GDELT news + web scraping | 🔴 READY | Deps: none |
| [STORY-286](STORIES/STORY-286.md) | All enrichment adapters: return partial data with low confidence instead of raising ValueError | 🔴 READY | CRITICAL — Deps: none |

## Success Criteria

- No enrichment adapter raises ValueError for missing metadata
- Each adapter returns partial data with `confidence < 0.5` when falling back
- YahooFinance successfully enriches companies without pre-configured tickers
- Website adapter discovers URLs for at least 80% of companies when URL not provided

## Definition of Done

- [ ] [STORY-286](STORIES/STORY-286.md): `grep -rn "raise ValueError" src/solstein/adapters/` returns zero results in enrichment adapters
- [ ] [STORY-282](STORIES/STORY-282.md): YahooFinance enriches a company with no ticker via web fallback
- [ ] [STORY-283](STORIES/STORY-283.md): WebsiteEnrichment auto-discovers URL when none provided
- [ ] [STORY-284](STORIES/STORY-284.md): GlobalMarketEnrichment returns sector data when no ticker
- [ ] [STORY-285](STORIES/STORY-285.md): FundingEnrichment returns partial funding data without Crunchbase
- [ ] `pytest tests/unit/ -k "enrichment"` passes

## Dependencies

- STORY-277 (website URLs in catalog) — for YahooFinance ticker fallback
- STORY-287 ([EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md)) — SearXNG adapter — for website auto-discovery
- STORY-314 ([EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md)) — SearXNG deployed — for web search
