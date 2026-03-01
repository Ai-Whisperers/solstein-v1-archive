# STORY-134: Replace requests with httpx in News and Funding Adapters

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> news_unified.py, funding_unified.py, additional_sources.py use requests.

## Problem Statement

The news and funding adapters — which make multiple external API calls per research job — are all synchronous. A single research job that fetches news from NewsAPI, GDELT, and RSS feeds serializes these calls. What should be 3 concurrent requests taking 1 second total takes 3 seconds sequentially. At scale, this blocking behavior multiplies pipeline duration by the number of external sources.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | Research pipeline 3-5x slower than necessary |
| **Scalability** | Limited by serial API calls |

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | Uses requests |
| `data/funding_unified.py` | Uses requests |
| `agents/additional_sources.py` | Uses requests |

## Architectural Requirements

- httpx.AsyncClient used for all HTTP calls
- Concurrent fetching where independent: NewsAPI + GDELT + RSS fetched in parallel with asyncio.gather()
- Connection pooling per adapter
- Timeout and retry configured per source
- Backward compatibility: adapter interfaces remain unchanged
- Error handling updated for httpx exception types

## Acceptance Criteria

- [ ] All three adapters use httpx
- [ ] Independent sources fetched concurrently
- [ ] Adapter interfaces unchanged
- [ ] Error handling works with httpx exceptions

## Definition of Done

- **Tests Required**: Integration test: research job with news+funding
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies asyncio.gather() used for independent calls

## Notes

Concurrent fetching reduces pipeline duration significantly.
