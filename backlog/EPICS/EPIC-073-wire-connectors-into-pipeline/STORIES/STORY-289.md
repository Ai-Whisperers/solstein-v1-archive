# STORY-289: Create SEC EDGAR enrichment adapter (10-K/10-Q)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None (SEC API is free) |

## Description

Create an enrichment adapter that fetches 10-K and 10-Q filings from SEC EDGAR for US-listed companies. Extracts: revenue, net income, employee count, risk factors, business description.

## Acceptance Criteria

- [ ] Adapter implements `EnrichmentAdapter` interface
- [ ] Fetches most recent 10-K and 10-Q for companies with SEC CIK
- [ ] Extracts structured financial data from XBRL/inline XBRL
- [ ] Uses configured email for User-Agent header (not placeholder)
- [ ] Unit tests with mocked SEC API responses
