# Search Fallbacks: SearXNG, DuckDuckGo, Google Package, Website Scraping

Verified on `2026-03-26`.

## Local Usage

- [web_search_client.py](../../../src/solstein/data/web_search_client.py)
- [web.py](../../../src/solstein/data/sources/web.py)
- [ai_research_orchestrator.py](../../../src/solstein/research/ai_research_orchestrator.py)
- [duckduckgo.py](../../../src/solstein/data/connectors/lookup_strategies/duckduckgo.py)
- [web_search_refresh.py](../../../src/solstein/infrastructure/connectors/web_search_refresh.py)

## Search Classes In This Repo

There are at least four distinct search modes in the codebase:

- Exa structured search
- SearXNG metasearch
- DuckDuckGo library and HTML fallbacks
- a dynamically imported `google_search` package of unclear provenance

There is also direct website scraping as a separate behavior.

## Official Surfaces

### SearXNG

- Docs: `https://docs.searxng.org/`
- Docs `robots.txt`: `https://docs.searxng.org/robots.txt` returned `404` in this pass
- Docs `llms.txt`: `https://docs.searxng.org/llms.txt` returned `404` in this pass
- Official repo: `https://github.com/searxng/searxng`

### DuckDuckGo

- `robots.txt`: `https://duckduckgo.com/robots.txt`
- `llms.txt`: `https://duckduckgo.com/llms.txt`

Important caveat from this pass:

- DuckDuckGo serves an `llms.txt` route, but in this check it rendered as an HTML page, not a simple plain-text manifest

### Google Fallback

- The repo does not reference an official Google search API client here.
- [web_search_client.py](../../../src/solstein/data/web_search_client.py) dynamically imports a package named `google_search`.

That should be treated as an implementation risk, not as a stable provider contract.

### Website Scraping

- [web.py](../../../src/solstein/data/sources/web.py) uses raw `requests.get(...)`
- It notes respect for `robots.txt`, but the implementation does not currently enforce a `robots.txt` gate before scraping

## Good Patterning

- Keep each fallback backend tagged in the normalized output.
- Do not label web-search-derived content as equivalent to first-party provider data.
- The fallback chain should be explicit and deterministic.
- Dynamic optional imports should be pinned to known packages and versions if they stay in the repo.
- Website scraping should validate robots policy before fetch.

## Current Contract Drift

- [web_search_refresh.py](../../../src/solstein/infrastructure/connectors/web_search_refresh.py) labels the backend as `exa_search` whenever results exist, even though [web_search_client.py](../../../src/solstein/data/web_search_client.py) can fall back to Google or DuckDuckGo.
- [web.py](../../../src/solstein/data/sources/web.py) claims robots respect, but does not enforce it.
- Search and scraping results currently cross boundaries mostly as loose dicts.

## Caveats

- SearXNG is a metasearch layer, not a single authoritative source.
- DuckDuckGo has explicit crawl restrictions in `robots.txt` for some surfaces.
- The `google_search` package path is a supply-chain and contract-risk surface until it is pinned and documented.

## Test Gates

- backend-tag preservation tests
- fallback-order tests
- website-scraping robots gate tests once implemented
- strict schema validation for normalized search results
