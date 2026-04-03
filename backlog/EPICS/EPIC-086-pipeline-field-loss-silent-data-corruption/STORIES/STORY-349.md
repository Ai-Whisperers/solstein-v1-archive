# STORY-349: Add Signal Extractors for All Orphaned Fact Types

| Field | Value |
|---|---|
| **Status** | ✅ DONE |
| **Priority** | P0 |
| **Size** | M (2–3 days) |
| **Epic** | EPIC-086 Pipeline Field Loss — Silent Data Corruption |
| **Created** | 2026-04-02 |
| **Risk** | Medium |
| **Execution Order** | 2 of 4 — after STORY-348 |
| **Blocked By** | STORY-348 |

---

## Problem Statement

`signals.py` defines exactly 10 signal extractors. The aggregator (`aggregate.py`) produces **16+ distinct
fact types** that have no corresponding signal extractor. These facts are correctly collected from adapters,
correctly aggregated across sources, and then silently discarded because no `_SIGNAL_EXTRACTORS` function
consumes them.

The following fact types are currently orphaned (collected but never extracted into signals):

**Group A — No signal extractor AND no Company mapping (pure Layer 2+3 gap)**

| Fact Type | Source Adapter | Currently Reaches Company? |
|-----------|---------------|--------------------------|
| `ebitda` | YahooFinance | ❌ No |
| `net_income` | YahooFinance | ❌ No |
| `pe_ratio` | YahooFinance | ❌ No |
| `current_price` | YahooFinance | ❌ No |
| `eps_ttm` | YahooFinance | ❌ No |
| `exchange` | YahooFinance | ❌ No |
| `products` | Website adapter | ❌ No |
| `pricing_model` | Website adapter | ❌ No |
| `target_customers` | Website adapter | ❌ No |
| `positive_article_count` | News adapter | ❌ No |
| `negative_article_count` | News adapter | ❌ No |
| `patent_categories` | Patents adapter | ❌ No |
| `last_round_amount` | Crunchbase | ❌ No |
| `sector` | YahooFinance | ❌ No (distinct from `industry`) |

**Group B — Signal extractor exists, but value not mapped to Company field (Layer 3 gap only — fix in STORY-350, NOT here)**

| Fact Type | Source Adapter | Signal Extractor | Layer 3 Gap |
|-----------|---------------|-----------------|-------------|
| `last_round_stage` | Crunchbase | `_signal_funding` (reasoning only) | Not mapped to Company field |
| `funding_rounds` | Crunchbase | `_signal_funding` (source_facts only) | Not mapped to Company field |
| `employee_growth_pct` | LinkedIn | `_signal_hiring_velocity` (primary value) | Signal exists; not in Company |
| `ai_related_positions` | LinkedIn | `_signal_ai_maturity` (source_facts only) | Not mapped to Company field |
| `ai_signal_strength` | YahooFinance | `_signal_ai_maturity` (fallback value) | Signal exists; not in Company |

**Group C — Produced by extractors AND mapped via direct fact lookup in `company_builder.py` (verify, may already work)**

| Fact Type | Source Adapter | Direct Mapping in Builder? |
|-----------|---------------|--------------------------|
| `name` | YahooFinance, generic | `_get_fact_value(facts, "name")` ✓ |
| `website` | YahooFinance, generic | `_get_fact_value(facts, "website")` ✓ |
| `description` | YahooFinance, generic | `_get_fact_value(facts, "description")` ✓ |
| `headquarters` | YahooFinance, generic | `_get_fact_value(facts, "headquarters")` ✓ |
| `founded_year` | YahooFinance, generic | `_get_fact_value(facts, "founded_year")` ✓ |
| `tech_stack` | Website adapter | `_build_tech_stack(facts, candidate)` ✓ |
| `investors` | Crunchbase | `_extract_lead_investors(facts)` ✓ |

> **Note for Group C**: Verify with STORY-348 test failures. If `extra="forbid"` does NOT flag these, they are correctly wired. If it does flag them, add to Group A.

---

## Acceptance Criteria

- [ ] Every fact type produced by `_extract_facts_from_source()` in `aggregate.py` has either:
  - A signal extractor in `_SIGNAL_EXTRACTORS`, OR
  - A direct mapping in `company_builder.py` (for string/list facts that don't need a numeric signal), OR
  - An explicit exclusion comment explaining why it is intentionally discarded
- [ ] A test asserts that the set of fact types in `_NUMERIC_FACT_TYPES` ∪ extracted string facts
  is fully covered by signal extractors + direct mappings
- [ ] `pytest` passes at 0 failures (combined with fixes from STORY-350)
- [ ] `ruff check` passes at 0 errors

---

## Tasks

- [ ] Enumerate all fact types produced by `_extract_facts_from_source()` for each source type
- [ ] Cross-reference against `_SIGNAL_EXTRACTORS` and direct `company_builder.py` mappings
- [ ] Add signal extractors in `signals.py` for numeric orphaned facts (`ebitda`, `net_income`, `pe_ratio`, `current_price`, `eps_ttm`)
- [ ] Add direct Company/FinancialMetric mappings in `company_builder.py` for non-numeric orphaned facts (`products`, `pricing_model`, `target_customers`, `exchange`, `patent_categories`, `last_round_stage`, `funding_rounds`, `positive_article_count`, `negative_article_count`)
- [ ] For Group B facts: do NOT add signal extractors — fix belongs in STORY-350 (Layer 3 builder mapping)
- [ ] For Group C facts: verify via STORY-348 test failures — if already wired, no action needed
- [ ] For each Group A addition: first add the field to the domain model (Company or FinancialMetric) in STORY-350, THEN wire the mapping

---

## Signal Extractor Template

```python
def _signal_ebitda(facts: dict[str, AggregatedFact]) -> SignalExtraction | None:
    """EBITDA signal from financial facts."""
    ebitda = _get_numeric(facts, "ebitda")
    if ebitda is None:
        return None
    fact = facts["ebitda"]
    return SignalExtraction(
        signal_name="ebitda",
        signal_value=ebitda,
        signal_confidence=fact.confidence,
        source_facts=["ebitda"],
        calculation_method="direct",
        calculation_formula="ebitda from highest-confidence source",
        reasoning=f"EBITDA of {ebitda:,.0f} from {len(fact.sources_used)} source(s)",
        why_it_matters="EBITDA indicates operating profitability before capital structure effects",
    )
```

---

## Autonomous Continuation Notes

### Start from the failure list from STORY-348
The `pytest` failures from STORY-348 will show exactly which fact types are being passed to domain models
as undeclared fields. Use that list as the work queue for this story.

### Do not merge with STORY-350
Keep signal extraction (this story) separate from Company model field additions (STORY-350).
Run tests after each story to isolate regressions.
