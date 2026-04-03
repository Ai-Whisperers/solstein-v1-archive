# STORY-351: Add Field-Count Regression Gate Across All Pipeline Layers

| Field | Value |
|---|---|
| **Status** | 🔴 READY (unblocked after STORY-350) |
| **Priority** | P0 |
| **Size** | S (1 day) |
| **Epic** | EPIC-086 Pipeline Field Loss — Silent Data Corruption |
| **Created** | 2026-04-02 |
| **Risk** | Low |
| **Execution Order** | 4 of 4 — after STORY-350 |
| **Blocked By** | STORY-350 |

---

## Problem Statement

Even after STORY-348–350 fix the existing field loss, there is no structural guarantee that prevents
the same regression from re-appearing when a new adapter field or signal is added. Without a regression
gate, each new feature silently re-introduces the same class of bug.

This story adds an automated test that acts as a permanent contract: **every fact type produced by
any adapter extractor must either reach `Company.model_dump()` or appear in an explicit exclusion list**.

---

## Acceptance Criteria

- [ ] A test in `tests/unit/test_pipeline_field_survival.py` (or equivalent) exists that:
  - Creates a synthetic `RawDataSource` for each adapter type with all known fields populated
  - Runs it through `DefaultFactAggregator.aggregate()` → `extract_signals()` → `build_company_entity_from_signals()`
  - Asserts that each input fact type either appears in `company.model_dump()` OR is in a documented `INTENTIONALLY_EXCLUDED_FACTS` set
- [ ] The `INTENTIONALLY_EXCLUDED_FACTS` set is defined in a single place (e.g., `research/field_survival_policy.py`) with a comment explaining each exclusion
- [ ] The test fails if a new fact type is added to any extractor in `aggregate.py` without updating either the field mappings or `INTENTIONALLY_EXCLUDED_FACTS`
- [ ] The test runs in < 1 second (no I/O, no network, no database)
- [ ] `pytest` passes at 0 failures
- [ ] `ruff check` passes at 0 errors

---

## Tasks

- [ ] Verify the `tests/factories` import path is resolvable (pgvector import issue may block — use a plain `DiscoveryCandidate(...)` constructor directly instead of factory if needed)
- [ ] Create `tests/unit/test_pipeline_field_survival.py`
- [ ] Define synthetic adapter payloads for: yahoo_finance, news, patents, crunchbase, linkedin, website, exa_search, generic
- [ ] Run full transformation chain on synthetic data
- [ ] Implement `_fact_is_present()` helper — must recursively check `company.model_dump()` for each fact's value; do NOT leave as `...` or the test will pass vacuously
- [ ] Assert field survival for each known fact type
- [ ] Create `INTENTIONALLY_EXCLUDED_FACTS` constant (e.g., raw aggregation metadata fields that aren't business data)
- [ ] Add this test to the CI pre-commit or fast-test gate

---

## Test Skeleton

```python
# tests/unit/test_pipeline_field_survival.py
"""Regression gate: every fact type produced by adapters must reach Company or be explicitly excluded."""

import pytest
from solstein.research.aggregate import DefaultFactAggregator, _NUMERIC_FACT_TYPES
from solstein.research.signals import extract_signals
from solstein.research.company_builder import build_company_entity_from_signals
from solstein.domain.models import RawDataRecord, RawDataSource, DataSourceType

# Fields intentionally excluded — must have documented reason
INTENTIONALLY_EXCLUDED_FACTS: dict[str, str] = {
    "source_agreement_percentage": "Aggregation metadata, not a business fact",
    "contradiction_notes": "Aggregation metadata, surfaced via metric_observations",
    # Add others with reasons as discovered
}


def _make_full_yahoo_finance_source() -> RawDataSource:
    """Synthetic YahooFinance payload with all known fields populated."""
    return RawDataSource(
        source_name="yahoo_finance",
        source_type=DataSourceType.YAHOO_FINANCE,
        confidence=0.9,
        raw_content={
            "financials": {
                "revenue": 1_000_000,
                "revenue_growth_yoy": 0.15,
                "profit_margin": 0.12,
                "ebitda": 200_000,
                "net_income": 100_000,
            },
            "market_cap": 5_000_000,
            "pe_ratio": 25.0,
            "current_price": 45.0,
            "eps_ttm": 1.8,
            "employees": 500,
            "founded": 2010,
            "description": "Test company",
            "headquarters": "London",
            "website": "https://example.com",
            "name": "Test Co",
            "exchange": "NYSE",
            "growth": {
                "employee_count": 500,
                "employee_growth": 0.1,
                "job_postings_count": 25,
                "ai_related_jobs": 5,
            },
            "ai": {"ai_score": 7, "ai_signal_strength": "strong"},
            "technology": {"industry": "SaaS", "sector": "Technology"},
            "products": {"products": ["Product A", "Product B"]},
        },
    )


def test_all_yahoo_finance_facts_reach_company():
    """Every fact extracted from YahooFinance source must survive to Company."""
    sources = [_make_full_yahoo_finance_source()]
    raw = RawDataRecord(company_id="test-co", gathering_batch_id="test", sources=sources)
    aggregated = DefaultFactAggregator().aggregate("test-co", raw)
    signals_record = extract_signals(aggregated)
    
    from tests.factories import make_discovery_candidate  # adjust import
    candidate = make_discovery_candidate(company_id="test-co", name="Test Co", ticker="TST")
    signals = {s.signal_name: s for s in signals_record.signals}
    facts = {f.fact_type: f for f in aggregated.facts}
    company = build_company_entity_from_signals(candidate, signals_record, aggregated, signals, facts)
    
    company_data = company.model_dump()
    
    for fact in aggregated.facts:
        if fact.fact_type in INTENTIONALLY_EXCLUDED_FACTS:
            continue
        # Each fact type must be reachable somewhere in the company dump
        assert _fact_is_present(fact.fact_type, fact.value, company_data), (
            f"Fact type '{fact.fact_type}' (value={fact.value!r}) was lost in pipeline. "
            f"Add it to Company/FinancialMetric or to INTENTIONALLY_EXCLUDED_FACTS with a reason."
        )


def _fact_is_present(fact_type: str, value, company_data: dict) -> bool:
    """Check if a fact value appears anywhere in the company dump (recursive)."""
    # Implementation: flatten company_data and check if value appears
    # for any key that corresponds to fact_type
    ...  # implement in story
```

---

## Autonomous Continuation Notes

### This test is a contract, not a quality metric
Once it passes, it must NEVER be weakened. Any new adapter field that fails this test is a bug in the
adapter wiring, not a problem with the test.

### `INTENTIONALLY_EXCLUDED_FACTS` must have documented reasons
Do not add a fact type to the exclusion set without a comment explaining why it's intentionally excluded.
"I don't know what to do with it" is not a valid reason — that means it should be wired into Company.
