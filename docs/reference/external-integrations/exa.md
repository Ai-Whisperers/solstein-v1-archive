# Exa

Verified on `2026-03-25`.

## Local Usage

- [web_search_client.py](../../../src/solstein/data/web_search_client.py)

## Official Surfaces

- Docs: `https://docs.exa.ai/reference`
- `llms.txt`: `https://docs.exa.ai/llms.txt`
- `robots.txt`: `https://docs.exa.ai/robots.txt`
- Official MCP server: `https://github.com/exa-labs/exa-mcp-server`

## Good Patterning

- Keep Exa as the first structured search path when `EXA_API_KEY` is configured.
- Preserve original result URLs, titles, snippets, and publication dates.
- Keep Exa payload handling distinct from DuckDuckGo and Google fallback payload handling.
- Validate normalized search result objects before they become company facts.
- Prefer official docs and `llms.txt` for future retrieval over HTML scraping.

## Caveats

- The repo currently falls back from Exa to Google and then DuckDuckGo.
- Those fallback paths should never be treated as equivalent source quality.
- Search-derived evidence is inherently more volatile than registry or filing data.

## Test Gates

- Exa success normalization
- fallback order coverage
- publication-date handling
- source URL preservation
