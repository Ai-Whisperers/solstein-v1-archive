# STORY-288: Create GDELT news enrichment adapter

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None (GDELT API is free) |

## Description

Create an enrichment adapter that uses the GDELT API to fetch news signals for companies: funding mentions, M&A activity, executive changes, regulatory news.

## Acceptance Criteria

- [ ] Adapter implements `EnrichmentAdapter` interface
- [ ] Queries GDELT API for company name mentions
- [ ] Extracts: funding_mentions, ma_signals, executive_changes, sentiment
- [ ] Handles API rate limits with exponential backoff
- [ ] Unit tests with mocked GDELT responses
