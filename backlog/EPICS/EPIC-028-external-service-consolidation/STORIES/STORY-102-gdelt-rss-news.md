# STORY-102: Replace NewsAPI with GDELT + RSS Aggregation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-028: External Service Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `data/news_unified.py` and `agents/additional_sources.py` call `newsapi.org`. NewsAPI free tier: 100 requests/day, no commercial use. NewsAPI paid: $449/month minimum. GDELT is a free, open, real-time global news database with no rate limits.

## Problem Statement

NewsAPI's free tier exists for personal/development use. Commercial use — which this platform is — requires a $449/month plan. GDELT (Global Database of Events, Language, and Tone) is a real-time, open-access news intelligence database that covers 100+ languages, supports full-text search, and provides structured event data including tone analysis. RSS aggregation covers company-specific sources (press releases, blog feeds, industry publications) that NewsAPI doesn't index. Together, GDELT + RSS is a superior news intelligence layer at zero marginal cost.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Cost** | Eliminates $449+/month NewsAPI cost |
| **Data Quality** | GDELT provides structured event and tone data beyond NewsAPI's article listing |

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | Uses NewsAPI |
| `agents/additional_sources.py` | Uses NewsAPI |
| `config.py` | NewsAPI key configuration |

## Architectural Requirements

- GDELT API client for news search (full-text, company name, date range)
- GDELT event data extraction: tone score, themes, geography — feed into signal layer
- RSS aggregation layer: configurable per-company feed list, respects feed `<ttl>` for polling cadence
- `news_unified.py` updated to aggregate GDELT + RSS + any retained paid sources
- NewsAPI retained as optional fallback (configured off by default)
- News deduplication by URL before persistence (same article from multiple sources = one record)
- Article retention policy: configurable TTL (default: 90 days)

## Acceptance Criteria

- [ ] News pipeline runs successfully without a NewsAPI key
- [ ] GDELT returns results for a real company name query
- [ ] Duplicate articles from multiple sources are deduplicated
- [ ] RSS feeds poll at their declared TTL interval (no over-polling)
- [ ] Tone/sentiment data from GDELT is surfaced in the signal layer

## Definition of Done

- **Tests Required**: Integration test: run news pipeline for a known company, verify GDELT results
- **Documentation Required**: News source configuration guide
- **Code Review Gate**: Reviewer verifies NewsAPI dependency is optional (not required for startup)

## Notes

GDELT + RSS replaces a $449/month dependency with open alternatives.
