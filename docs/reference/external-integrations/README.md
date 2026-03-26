# External Integrations

Durable documentation for third-party APIs, search tools, wrappers, and data providers used by Solstein.

Verified live on `2026-03-25` unless a file says otherwise.

## Purpose

- Keep a source-of-truth index of the external surfaces the pipeline depends on.
- Distinguish official APIs from unofficial wrappers, heuristics, and scrape-based fallbacks.
- Record discoverability for each provider:
  - official docs
  - `llms.txt`
  - `robots.txt`
  - official repos with examples or markdown docs
  - official MCP servers, when they exist
- Capture practical integration patterns and caveats so future fixes do not rediscover the same problems.

## Files

- [AUDIT_2026-03-25.md](./AUDIT_2026-03-25.md)
- [github.md](./github.md)
- [newsapi.md](./newsapi.md)
- [sec-edgar.md](./sec-edgar.md)
- [companies-house.md](./companies-house.md)
- [exa.md](./exa.md)
- [crunchbase.md](./crunchbase.md)
- [linkedin-proxycurl.md](./linkedin-proxycurl.md)
- [openfigi.md](./openfigi.md)
- [opencorporates.md](./opencorporates.md)
- [patentsview.md](./patentsview.md)
- [search-fallbacks.md](./search-fallbacks.md)
- [builtwith.md](./builtwith.md)
- [pitchbook.md](./pitchbook.md)
- [yahoo-finance-yfinance.md](./yahoo-finance-yfinance.md)

## Reading Rules

- Treat each provider file as the contract guide for that provider.
- Treat the audit file as the inventory and prioritization layer.
- If a provider is only reachable through an unofficial wrapper, document that explicitly instead of pretending it is an official API integration.
- If discoverability could not be verified cleanly, mark it as unverified rather than inferred.

## Next Queue

- Secondary product and social connectors present in `src/solstein/connectors/`
- decide whether `google_search` remains in the repo or is replaced with a verified provider path
- convert the next external payload boundaries into strict TS contract fixtures
