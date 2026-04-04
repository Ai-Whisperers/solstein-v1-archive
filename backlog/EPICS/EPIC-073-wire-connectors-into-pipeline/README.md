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
| [STORY-292](STORIES/STORY-292.md) | Register all new enrichment adapters in build_default_registry() | 🔴 READY | Deps: STORY-287 through STORY-291 |

## Success Criteria

- All 5 new adapters exist and pass unit tests with mocked responses
- `build_default_registry()` registers all adapters
- At least 3 new adapters produce real data in a live enrichment run
- GitHub adapter successfully extracts tech stack for companies with known GitHub orgs

## Dependencies

- SearXNG deployed (STORY-314)
- GITHUB_TOKEN configured in environment
