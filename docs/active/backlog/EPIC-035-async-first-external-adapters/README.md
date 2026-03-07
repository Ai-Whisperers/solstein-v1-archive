# EPIC-035: Async-First External Adapters

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Created** | 2026-03-01 |
| **Owner** | Platform Engineering |
| **Dependencies** | EPIC-021 (Modern LLM Stack), EPIC-028 (External Service Consolidation) |

---

## Executive Summary

A forensic audit of the codebase identified **12 files** using the synchronous `requests` library inside `async def` functions. This is not a minor code smell — it is a fundamental architectural defect that serializes what should be a concurrent pipeline. The research engine is async in name only. Under the hood, every external HTTP call blocks the event loop, preventing any other coroutine from making progress until the network round-trip completes.

The result: a research pipeline that should complete in 30 seconds with proper async concurrency routinely takes 5 minutes. The fix is mechanical but non-trivial: replace `requests` with `httpx.AsyncClient` across all affected adapters, enforce concurrent fetching where sources are independent, and establish standards that prevent the pattern from re-emerging.

---

## Audit Findings

The forensic audit flagged the following as the most egregious violations:

| File | Line(s) | Violation |
|------|---------|-----------|
| `agents/github_agent.py` | 56, 58 | `requests.get()` inside `async def gather()` — **BLOCKS EVENT LOOP** |
| `data/news_unified.py` | Multiple | `requests` in async adapter |
| `data/funding_unified.py` | Multiple | `requests` in async adapter |
| `agents/additional_sources.py` | Multiple | `requests` in async adapter |
| `agents/companies_house_agent.py` | Multiple | `requests` in async adapter |
| `agents/website_agent.py` | Multiple | `requests` in async adapter |

12 files total. The pattern is consistent: developers reached for `requests` because it's familiar, and no standard existed to stop them.

---

## Problem Context

Python's `asyncio` event loop is single-threaded. When a coroutine calls a synchronous blocking function — such as `requests.get()` — the entire event loop halts until that call returns. No other coroutine can run. No I/O can be processed. The event loop is frozen.

This means that every `requests.get()` call inside an `async def` function is a silent performance catastrophe. The code looks async. It uses `async def` and `await`. But the moment it hits a `requests.get()`, it reverts to synchronous behavior and takes the entire application with it.

The research pipeline is particularly vulnerable because it makes many external API calls — GitHub, NewsAPI, GDELT, Companies House, RSS feeds, website scraping — that are all I/O-bound and should run concurrently. Instead, they run serially, each one blocking the event loop while waiting for a network response.

The fix is not complicated. `httpx` is a drop-in replacement for `requests` with a proper async interface. The migration is mechanical. The performance gains are immediate and substantial.

---

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-133](STORIES/STORY-133-github-agent-async.md) | Replace requests with httpx in GitHub Agent | P2 | 🔴 Not Started |
| [STORY-134](STORIES/STORY-134-news-funding-async.md) | Replace requests with httpx in News and Funding Adapters | P2 | 🔴 Not Started |
| [STORY-135](STORIES/STORY-135-companies-house-website-async.md) | Replace requests with httpx in Companies House and Website Agents | P2 | 🔴 Not Started |
| [STORY-136](STORIES/STORY-136-async-http-guidelines.md) | Add Async HTTP Client Guidelines and Linting | P2 | 🔴 Not Started |

---

## Dependencies

### Upstream (must complete before this epic)
- **EPIC-021: Modern LLM Stack** — Establishes the async-first architectural pattern this epic extends to external adapters.
- **EPIC-028: External Service Consolidation** — Defines which external services are in scope and their adapter boundaries.

### Downstream (blocked by this epic)
- Any epic that requires concurrent external data fetching to meet performance SLAs.
- Pipeline throughput improvements that assume async I/O.

---

## Success Metrics

| Metric | Baseline (Current) | Target |
|--------|-------------------|--------|
| Research pipeline duration (10 companies) | ~5 minutes | ≤ 90 seconds |
| GitHub API calls (10 concurrent) | Serialized (~10s) | Parallel (~1-2s) |
| News + funding fetch (3 sources) | ~3s sequential | ~1s concurrent |
| UK company research (Companies House + website) | ~7s sequential | ~2s concurrent |
| `requests` imports in async files | 12 | 0 |
| CI failure on new `requests`-in-async violations | No gate | Enforced |

---

## Scope Boundaries

**In scope:**
- All files identified in the forensic audit
- `httpx.AsyncClient` migration for API-style HTTP calls
- `aiohttp` as an alternative for complex website scraping where `httpx` is insufficient
- Linting rule to prevent regression
- Standards documentation

**Out of scope:**
- Rewriting adapter business logic (only the HTTP client changes)
- Changing adapter public interfaces
- Database I/O (separate epic)
- LLM client async patterns (covered by EPIC-021)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `httpx` behavior differs from `requests` for edge cases | Medium | Medium | Integration tests against real endpoints in staging |
| Website scraping breaks with `httpx` (JS-heavy sites) | Medium | Low | `aiohttp` fallback permitted for website agent |
| Retry logic incompatible with `httpx` exceptions | Low | Medium | Map exception types in story requirements |
| New async bugs introduced (e.g., missing `await`) | Low | High | Mandatory async-aware code review gate |

---

## Notes

The irony of this situation is not lost on anyone: a platform built on FastAPI — one of the most async-native Python frameworks in existence — has been making synchronous HTTP calls in its core data pipeline. FastAPI's entire value proposition is async concurrency. Using `requests` inside it is like buying a sports car and pushing it.

This epic corrects that. The work is unglamorous but the impact is real: faster pipelines, better resource utilization, and a codebase that actually behaves the way it looks.
