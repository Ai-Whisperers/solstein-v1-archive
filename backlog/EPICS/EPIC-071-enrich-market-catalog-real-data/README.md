# EPIC-071: Enrich Market Catalog with Real Data Hooks

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Effort** | S (1–2 days) |
| **Stories** | 5 ([STORY-277](STORIES/STORY-277.md) through [STORY-281](STORIES/STORY-281.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, Success Criteria, DoD) |

## Context

Market catalog companies in `market_catalogs.py` lack website URLs, stock tickers, LinkedIn slugs, and other data hooks needed by enrichment adapters. Without these, connectors have no entry points and every adapter falls back or raises ValueError.

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [STORY-277](STORIES/STORY-277.md) | Add website URLs to all 24 Dutch Energy catalog companies | 🔴 READY |
| [STORY-278](STORIES/STORY-278.md) | Add stock tickers for all publicly traded catalog companies | 🔴 READY |
| [STORY-279](STORIES/STORY-279.md) | Add LinkedIn company slugs to all catalog companies | 🔴 READY |
| [STORY-280](STORIES/STORY-280.md) | Add GitHub org names where applicable | 🔴 READY |
| [STORY-281](STORIES/STORY-281.md) | Add CrunchBase slugs for startups/funded companies | 🔴 READY |

## Success Criteria

- All 24 Dutch Energy catalog companies have at least a website URL
- All publicly traded companies have a stock ticker
- At least 80% of companies have a LinkedIn slug
- GitHub org names added where a public org exists
- CrunchBase slugs added for all VC-funded companies

## Definition of Done

- [ ] [STORY-277](STORIES/STORY-277.md): `market_catalogs.py` — all 24 companies have `website` field
- [ ] [STORY-278](STORIES/STORY-278.md): all publicly traded companies have `ticker` field
- [ ] [STORY-279](STORIES/STORY-279.md): all companies have `linkedin_slug` field where known
- [ ] [STORY-280](STORIES/STORY-280.md): companies with public GitHub orgs have `github_org` field
- [ ] [STORY-281](STORIES/STORY-281.md): funded companies have `crunchbase_slug` field
- [ ] `pytest tests/unit/ -k catalog` passes

## Dependencies

None — pure data entry, can start immediately.
