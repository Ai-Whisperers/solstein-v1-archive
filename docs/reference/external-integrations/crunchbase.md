# Crunchbase

Verified on `2026-03-25`.

## Local Usage

- [crunchbase.py](../../../src/solstein/connectors/financial/crunchbase.py)
- [funding.py](../../../src/solstein/data/sources/funding.py)
- [funding_refresh.py](../../../src/solstein/infrastructure/connectors/funding_refresh.py)

## Official Surfaces

- Docs: `https://data.crunchbase.com/docs`
- `llms.txt`: `https://data.crunchbase.com/llms.txt`
- `robots.txt`: `https://data.crunchbase.com/robots.txt`

## Good Patterning

- Use one verified contract for auth and endpoint shape across the whole repo.
- Normalize Crunchbase organization identity separately from funding-round facts.
- Keep fallback public-news-derived funding inference explicitly lower confidence than paid API data.
- Treat missing values and absent funding blocks as normal, not exceptional.

## Current Contract Drift

Two different patterns exist in the repo today:

- [crunchbase.py](../../../src/solstein/connectors/financial/crunchbase.py) uses `X-cb-user-key` and `searches/organizations`
- [funding.py](../../../src/solstein/data/sources/funding.py) uses `Authorization: Bearer ...` and `/v4/organizations/{company_name}`

This should be reconciled before treating Crunchbase as a hardened integration.

## Caveats

- Crunchbase access and endpoint availability depend heavily on account plan and package.
- Company-name lookup is not the same as stable entity resolution.
- News-derived funding estimates are not a substitute for authoritative round data.

## Test Gates

- auth-header regression tests
- endpoint-shape contract tests
- organization payload normalization
- funding-round schema fixtures
