# GitHub API

Verified on `2026-03-25`.

## Local Usage

- [github_connector.py](../../../src/solstein/data/connectors/github_connector.py)
- [github.py](../../../src/solstein/connectors/product/github.py)
- [github_refresh.py](../../../src/solstein/infrastructure/connectors/github_refresh.py)

## Official Surfaces

- Docs: `https://docs.github.com/en/rest`
- `llms.txt`: `https://docs.github.com/llms.txt`
- `robots.txt`: `https://docs.github.com/robots.txt`
- Official MCP server: `https://github.com/github/github-mcp-server`

Confirmed during this pass:

- the docs site exposes an LLM index
- the docs page itself advertises markdown and JSON alternates
- the MCP server repo is explicitly titled as GitHub's official MCP server

## Good Patterning

- Always send `User-Agent` and a token when available.
- Keep `403` rate-limit or access-denied handling separate from `404`.
- Treat public events as a weaker proxy than direct repository or commit endpoints.
- Normalize repository, activity, and commit payloads into typed internal models before scoring.
- Prefer official docs alternates and `llms.txt` for future retrieval instead of scraping docs HTML.

## Caveats

- Public event streams are not full commit history.
- Private repository visibility depends on scopes and org permissions.
- Unauthenticated behavior is not an acceptable production contract for Solstein.

## Test Gates

- repository list contract fixtures
- public-event parsing fixtures
- rate-limit branch coverage
- schema validation for normalized tech-signal payloads
