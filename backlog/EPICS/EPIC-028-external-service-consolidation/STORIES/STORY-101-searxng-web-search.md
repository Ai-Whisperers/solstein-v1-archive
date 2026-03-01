# STORY-101: Replace Google Custom Search with Self-Hosted SearXNG

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-028: External Service Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-026 (Docker Infrastructure) |

## The Audit Verdict

> `agents/web_search_agent.py` calls `googleapis.com/customsearch/v1`. Google Custom Search allows 100 free queries/day, $5 per 1000 after. A PE/VC platform analyzing hundreds of companies per day will hit this limit constantly.

## Problem Statement

Google Custom Search has a free tier designed for personal projects and demos. One hundred queries per day. A competitive intelligence platform that researches even 20 companies per day, with 5-10 search queries per company, exhausts the free tier before lunch. After that, every query costs $5 per thousand. The billing is metered, unpredictable, and scales linearly with usage — exactly the wrong cost model for a platform whose value proposition is "analyze more companies, faster."

SearXNG is a self-hosted, open-source meta search engine. It aggregates results from Google, Bing, DuckDuckGo, Brave Search, and dozens of other engines through their public interfaces. It's free, unlimited, and runs as a Docker container — which the platform already supports (EPIC-026). The operational cost is one container's worth of compute. The search quality is equal or better than Google CSE alone, because SearXNG aggregates multiple sources and deduplicates results.

The migration is straightforward: replace the Google CSE API call with a SearXNG JSON API call. The response format changes; the search result semantics (title, URL, snippet) do not. Google CSE is retained as a fallback for the rare case where SearXNG is unreachable, but it is no longer the primary search provider. The API key stays in the config; it's just no longer on the critical path.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | No more quota exhaustion at 100 queries/day. Search availability is under platform control, not Google's billing tier. |
| **Operational** | Full control over search behavior, aggregation sources, and caching. No external API key dependency on the critical path. |
| **Developer Experience** | Local development no longer requires a Google Cloud project and API key for web search to work. `docker compose up` includes SearXNG. |
| **Security** | Search queries no longer sent to Google's API (which logs them). Queries stay within the platform's infrastructure. |

## Affected Files

| File | Issue |
|------|-------|
| `agents/web_search_agent.py` | Calls Google Custom Search API directly; needs to call SearXNG with GCS fallback |
| `docker-compose.yml` | SearXNG service not present |
| `config.py` | No SearXNG configuration; GCS is hardcoded as the only search provider |

## Architectural Requirements

- SearXNG added as a service in `docker-compose.yml` with appropriate resource limits and health check
- SearXNG configured to aggregate results from: Google, Bing, DuckDuckGo, and Brave Search (at minimum)
- SearXNG engine list configurable via environment variable or mounted config file — not hardcoded
- `web_search_agent.py` updated to call the local SearXNG instance via its JSON API as the primary search backend
- Google Custom Search adapter retained but demoted to fallback: SearXNG unreachable → log WARNING → fall back to GCS → if GCS also fails → raise with structured error
- Search results normalized to a common interface regardless of which backend provided them (title, URL, snippet, source engine, relevance score)
- Result caching via Redis: identical query within a configurable TTL (default: 1 hour) returns cached results without hitting any search backend
- Rate limiting per originating `company_id` to prevent runaway search jobs from consuming all search capacity
- SearXNG instance configured with rate limiting toward upstream engines to avoid IP-level blocks from Google/Bing

## Acceptance Criteria

- [ ] `docker compose up` starts SearXNG service alongside the application
- [ ] Web search calls route to SearXNG by default — no Google API key required for search to function
- [ ] SearXNG unavailable triggers automatic fallback to Google CSE with a WARNING-level log including the SearXNG error
- [ ] Search results include source attribution: which search engine(s) returned each result
- [ ] Repeated identical queries within the TTL window return cached results (verified by checking Redis key exists)
- [ ] Search results from SearXNG and GCS conform to the same response schema

## Definition of Done

- **Tests Required**: Integration test — run web search with SearXNG running (verify SearXNG results). Stop SearXNG container, run the same search (verify GCS fallback fires and results still return). Unit test — verify result normalization produces identical schema from both backends.
- **Documentation Required**: SearXNG configuration documented (engine list, rate limits, caching TTL). Fallback behavior documented (when does GCS activate, how to tell from logs).
- **Code Review Gate**: Reviewer verifies Google CSE is the fallback, not the primary. Reviewer verifies SearXNG container has a health check and resource limits. Reviewer verifies search results are normalized to a single schema.

## Notes

SearXNG's strength is aggregation — it queries multiple engines and deduplicates. This means search quality is generally higher than any single engine, because results that appear across multiple engines are ranked higher. However, SearXNG depends on the upstream engines' public interfaces, which can change. The engine list should be monitored: if a particular engine starts returning errors consistently, it should be disabled in SearXNG config rather than failing silently.

SearXNG also supports academic engines (Google Scholar, Semantic Scholar), which could be valuable for a PE/VC platform researching companies with published patents or academic partnerships. This is a future enhancement, not a requirement for this story.

The Redis caching layer serves double duty: it reduces load on SearXNG (and upstream engines), and it provides consistent results for the same query across multiple pipeline stages. If the research pipeline searches for "Acme Corp competitors" in the web search stage and again in the validation stage, the second query should return the same results — not a different set because a new article was indexed between the two queries.
