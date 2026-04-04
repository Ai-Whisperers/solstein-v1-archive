# EPIC-073: Wire Connectors into Pipeline

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P1: Data Supply |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Created** | 2026-04-01 |

## Context

Several free data sources (SearXNG, GDELT, SEC EDGAR, GitHub, arXiv/patents) are not yet connected to the enrichment pipeline. The pipeline only uses connectors that are explicitly registered in `build_default_registry()`. New adapters must be created and registered.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-287](STORIES/STORY-287.md) | Create SearXNG-based web search enrichment adapter (company website scraping + news) | 🔴 READY | Deps: none (SearXNG in docker-compose) |
| [STORY-288](STORIES/STORY-288.md) | Create GDELT news enrichment adapter (news signals, funding mentions, M&A) | 🔴 READY | Deps: none (GDELT API is free) |
| [STORY-289](STORIES/STORY-289.md) | Create SEC EDGAR enrichment adapter (10-K/10-Q for US-listed companies) | 🔴 READY | Deps: none (SEC API is free) |
| [STORY-290](STORIES/STORY-290.md) | Create GitHub enrichment adapter (tech stack, repo activity, open source signals) | 🔴 READY | Deps: none (GITHUB_TOKEN exists) |
| [STORY-291](STORIES/STORY-291.md) | Create arXiv/patent enrichment adapter (R&D and innovation signals) | 🔴 READY | Deps: none |
| [STORY-292](STORIES/STORY-292.md) | Register all new enrichment adapters in build_default_registry() | 🔴 READY | Deps: [STORY-287](STORIES/STORY-287.md) through [STORY-291](STORIES/STORY-291.md) |

## Success Criteria

- All 5 new adapters exist and pass unit tests with mocked responses
- `build_default_registry()` registers all adapters
- At least 3 new adapters produce real data in a live enrichment run
- GitHub adapter successfully extracts tech stack for companies with known GitHub orgs

## Dependencies

- SearXNG deployed (STORY-314)
- GITHUB_TOKEN configured in environment

## Verified Codebase State (2026-04-04)

**Currently registered in `build_default_registry()` at `src/solstein/adapters/registry.py:74`:**

| Adapter | File | Registered Condition |
|---------|------|----------------------|
| `StaticCatalogSource` | `adapters/discovery/static_catalog.py` | Always |
| `CompetitorJsonSource` | `adapters/discovery/competitor_json.py` | Always |
| `YahooFinanceEnrichment` | `adapters/enrichment/yahoo_finance.py` | Always |
| `GlobalMarketEnrichment` | `adapters/enrichment/global_market.py` | Always |
| `PatentEnrichment` | `adapters/enrichment/patents.py` | Always |
| `LinkedInEnrichment` | `adapters/enrichment/linkedin.py` | Always (uses news_api_key optionally) |
| `WebsiteEnrichment` | `adapters/enrichment/website.py` | Always |
| `FundingEnrichment` | `adapters/enrichment/funding.py` | Only if `crunchbase_api_key` set |

**Adapters that were removed and retired (not present in codebase):**
- `WebSearchDiscoverySource` (Exa) → moved to `adapters/discovery/_retired/web_search.py` (STORY-264)
- `NewsEnrichment` (NewsAPI) → moved to `adapters/enrichment/_retired/` (STORY-264)
- `WebSearchNewsEnrichment` (Exa) → moved to `adapters/enrichment/_retired/` (STORY-264)

**Adapters that DO NOT EXIST anywhere in codebase (all 6 stories are new code):**
- SearXNG web search adapter — zero files (STORY-287 creates it)
- GDELT news adapter — zero files (STORY-288 creates it)
- SEC EDGAR adapter — zero files (STORY-289 creates it)
- GitHub adapter — zero files (STORY-290 creates it)
- arXiv/patent API adapter — zero files; `PatentEnrichment` uses a different data source (STORY-291 creates it)

**Registration point for new adapters (STORY-292):** `build_default_registry()` at `src/solstein/adapters/registry.py:74` — add imports and `registry.register_*()` calls following the existing pattern.
