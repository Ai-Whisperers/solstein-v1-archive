# EPIC-072: Fix Enrichment Adapter Resilience

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P1: Data Supply |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Created** | 2026-04-01 |

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

## Dependencies

- STORY-277 (website URLs in catalog) — for YahooFinance ticker fallback
- STORY-287 (SearXNG adapter) — for website auto-discovery
- STORY-314 (SearXNG deployed) — for web search
