# STORY-135: Replace requests with httpx in Companies House and Website Agents

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> companies_house_agent.py, website_agent.py use requests.

## Problem Statement

UK company data fetching and website scraping are both I/O-bound operations that currently block the event loop. Companies House API calls can take 500ms-2s. Website scraping can take 1-5s depending on the site. These are serialized in the current implementation, making the UK data collection path unnecessarily slow.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | UK company research 2-5x slower than necessary |
| **User Experience** | Longer wait times for UK companies |

## Affected Files

| File | Issue |
|------|-------|
| `agents/companies_house_agent.py` | Uses requests |
| `agents/website_agent.py` | Uses requests |

## Architectural Requirements

- httpx.AsyncClient for Companies House API calls
- httpx.AsyncClient for website fetching (or aiohttp if httpx has issues with certain sites)
- Concurrent fetching where possible: website + Companies House in parallel
- Respect robots.txt (existing behavior preserved)
- Timeout handling: website fetches need longer timeouts (10-30s)
- Retry logic for transient failures

## Acceptance Criteria

- [ ] Companies House agent uses httpx
- [ ] Website agent uses httpx/aiohttp
- [ ] Concurrent fetching where independent
- [ ] robots.txt still respected

## Definition of Done

- **Tests Required**: Integration test: UK company research
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies no blocking I/O in async functions

## Notes

UK data collection should be as fast as other regions.
