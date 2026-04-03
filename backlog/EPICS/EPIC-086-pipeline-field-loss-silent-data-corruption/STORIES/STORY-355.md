# STORY-355: Create Unit Tests for Pipeline Extractor Layer (aggregate.py)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P0 |
| **Size** | M (2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss |
| **Created** | 2026-04-03 |
| **Risk** | Low |
| **Blocked By** | STORY-349 (extractors must be complete before tests are authoritative) |

---

## Problem Statement

`src/solstein/research/aggregate.py` has zero isolated unit tests. The per-source extractors (`_extract_yahoo_finance`, `_extract_crunchbase`, `_extract_linkedin`, etc.) are the gateway from raw adapter output to typed facts. Any silent change to the extractor — a renamed key, a missing nested path — drops data with no detection. This was the root mechanism of the 70% field loss.

## Acceptance Criteria

- [ ] `tests/unit/test_aggregate_extractors.py` exists with tests for every extractor function
- [ ] Each test asserts the exact set of `(fact_type, value)` tuples produced from a fully-populated synthetic payload
- [ ] Each test also asserts that an empty/null payload produces no facts (no crash)
- [ ] All tests run in < 200ms (no I/O, no DB, no network)
- [ ] Coverage of `aggregate.py` extractor functions reaches 90%+
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

## Tasks

- [ ] Write tests for `_extract_yahoo_finance()` with fully populated nested payload
- [ ] Write tests for `_extract_crunchbase()` with all funding fields
- [ ] Write tests for `_extract_linkedin()` with all employee/hiring fields
- [ ] Write tests for `_extract_website()` with products, tech_stack, pricing_model, target_customers
- [ ] Write tests for `_extract_news()` with sentiment and article counts
- [ ] Write tests for `_extract_patents()` with total and AI-related patents
- [ ] Write tests for `_extract_exa_search()` and `_extract_generic()`
- [ ] Write tests for `DefaultFactAggregator.aggregate()`: assert all expected fact types present in output
- [ ] Assert that a missing nested key (e.g., `financials` key absent) produces no crash and no partial fact

## Autonomous Continuation Notes

These tests intentionally verify the contract between adapter output shape and fact extraction. If a test fails after a new adapter field is added, that is a signal to update the extractor — not to weaken the test.
