# STORY-103: Stabilize Yahoo Finance Integration

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-028: External Service Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `data/yahoo_finance.py` and `data/global_market.py` use the `yfinance` library which scrapes Yahoo Finance HTML. No retry on failure. No circuit breaker. Yahoo regularly changes its HTML structure, breaking scraping integrations without notice.

## Problem Statement

The `yfinance` library is a community-maintained HTML scraper, not an official API. Yahoo Finance has broken yfinance multiple times in the past two years by changing their authentication flow or HTML structure. When it breaks, it breaks silently — the data pipeline continues to run, records zero financial data, and the platform serves stale market data with no indication that the source is down. For a platform that PE/VC analysts trust for market benchmarks, "Yahoo Finance broke again" is not an acceptable operational state.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Quality** | Silently stale market data when Yahoo changes structure |
| **Reliability** | No circuit breaker means broken source runs indefinitely |

## Affected Files

| File | Issue |
|------|-------|
| `data/yahoo_finance.py` | Uses yfinance scraping |
| `data/global_market.py` | Uses yfinance scraping |

## Architectural Requirements

- Replace `yfinance` scraping with a proper financial data API: Alpha Vantage (free tier: 25 requests/day) or EOD Historical Data (paid but stable)
- If yfinance is retained as a fallback, wrap in circuit breaker (STORY-116 dependency)
- Add explicit failure detection: if market cap field is None for 3 consecutive fetches, emit a WARNING log and mark source as DEGRADED
- Alternative: use Supabase Edge Functions to proxy Yahoo Finance requests (rate limiting, retry, caching in one place)
- Market data cached in PostgreSQL with `fetched_at` timestamp — stale data served with staleness indicator, not as fresh
- Data freshness SLA documented: market data considered stale after 24h

## Acceptance Criteria

- [ ] Financial data fetches do not use HTML scraping as primary method
- [ ] Failed fetches trigger circuit breaker after 3 consecutive failures
- [ ] Stale data (>24h) is flagged in API responses with `data_freshness` field
- [ ] Source degradation emits structured WARNING log with source name and failure reason

## Definition of Done

- **Tests Required**: Integration test: disable financial data source, verify circuit breaker fires
- **Documentation Required**: Data freshness SLA documentation
- **Code Review Gate**: Reviewer verifies no raw HTML parsing remains in financial data path

## Notes

HTML scraping is not a production data strategy.
