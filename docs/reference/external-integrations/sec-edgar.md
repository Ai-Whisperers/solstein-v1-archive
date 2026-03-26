# SEC EDGAR

Verified on `2026-03-25`.

## Local Usage

- [sec_edgar_connector.py](../../../src/solstein/data/connectors/sec_edgar_connector.py)
- [sec_edgar_refresh.py](../../../src/solstein/infrastructure/connectors/sec_edgar_refresh.py)
- [sec_edgar.py](../../../src/solstein/connectors/financial/sec_edgar.py)
- [sec_edgar_helpers.py](../../../src/solstein/data/unified/sec_edgar_helpers.py)

## Official Surfaces

- Docs: `https://www.sec.gov/edgar/sec-api-documentation`
- Related machine-readable access guidance is also referenced from `https://www.sec.gov/edgar/sec-api-documentation`

This pass hit SEC rate-threshold responses while checking `robots.txt` and `llms.txt` directly. That is operationally important:

- SEC is sensitive to automated retrieval patterns
- doc-surface probing must stay polite and low-frequency

## Good Patterning

- Always send a real contactable `SEC_USER_AGENT`.
- Keep request rates conservative and cache aggressively.
- Prefer filing-library abstractions only if they preserve traceability to filing type and period.
- Separate annual, quarterly, and current-report semantics.
- Validate extracted financial fields before merging them into unified company state.

## Caveats

- SEC is authoritative for filings, not for every derived metric the rest of the pipeline wants.
- Retrieval behavior that looks like scraping abuse can be blocked.
- CIK, ticker, and filing-period resolution need their own regression coverage.

## Test Gates

- filing lookup fixtures by filing type
- polite-rate and retry logic
- schema validation for extracted financial statements
- merge tests proving SEC data cannot silently overwrite stronger local invariants with null or malformed values
