# EPIC-071: Enrich Market Catalog with Real Data Hooks

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P1: Data Supply |
| **Phase** | P1 — Make Pipeline Produce Real Data |
| **Created** | 2026-04-01 |
| **Source** | Product readiness audit 2026-04-01 |

## Context

Market catalog companies in `market_catalogs.py` lack website URLs, stock tickers, LinkedIn slugs,
and other data hooks needed by enrichment adapters. Without these, connectors have no entry points.

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [STORY-277](STORIES/STORY-277.md) | Add website URLs to all 24 Dutch Energy catalog companies | 🔴 READY |
| [STORY-278](STORIES/STORY-278.md) | Add stock tickers for all publicly traded catalog companies | 🔴 READY |
| [STORY-279](STORIES/STORY-279.md) | Add LinkedIn company slugs to all catalog companies | 🔴 READY |
| [STORY-280](STORIES/STORY-280.md) | Add GitHub org names where applicable | 🔴 READY |
| [STORY-281](STORIES/STORY-281.md) | Add CrunchBase slugs for startups/funded companies | 🔴 READY |

## Dependencies

None — pure data entry, can start immediately.
