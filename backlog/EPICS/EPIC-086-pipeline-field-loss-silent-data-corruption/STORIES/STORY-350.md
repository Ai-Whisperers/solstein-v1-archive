# STORY-350: Map All Surviving Signals and Facts to Company/FinancialMetric Fields

| Field | Value |
|---|---|
| **Status** | ✅ DONE |
| **Priority** | P0 |
| **Size** | M (2 days) |
| **Epic** | EPIC-086 Pipeline Field Loss — Silent Data Corruption |
| **Created** | 2026-04-02 |
| **Risk** | Medium |
| **Execution Order** | 3 of 4 — after STORY-349 |
| **Blocked By** | STORY-349 |

---

## Problem Statement

Even after adding signal extractors (STORY-349), the signals and facts that survive must be explicitly
mapped into `Company` or `FinancialMetric` fields in `company_builder.py`. Two additional gaps exist:

1. **Fields in `FinancialMetric` that are never populated**: `ebitda_margin` and `recurring_revenue_pct`
   exist in the model definition but `_build_financials()` never sets them, even when the data is available.

2. **Company model missing fields entirely**: Fields like `products`, `pricing_model`, `target_customers`,
   `exchange`, `patent_categories`, `last_round_stage`, `funding_rounds`, `positive_article_count`,
   `negative_article_count` have nowhere to go in the `Company` model. They need to either be added
   as explicit fields or collected into a typed `extra_facts: dict[str, Any]` field with a clear contract.

---

## Acceptance Criteria

- [ ] `FinancialMetric.ebitda_margin` is populated from the `ebitda` fact when present
- [ ] `FinancialMetric.recurring_revenue_pct` is populated when a `recurring_revenue` fact exists
- [ ] `Company` has explicit fields or a typed `extra_facts` dict for product, market, and news data
- [ ] `build_company_entity_from_signals()` maps all signals from STORY-349 into the Company constructor
- [ ] No field is passed to `Company(...)` or `FinancialMetric(...)` that isn't in the model (enforced by `extra="forbid"` from STORY-348)
- [ ] `pytest` passes at 0 failures
- [ ] `ruff check` passes at 0 errors

---

## Tasks

### FinancialMetric additions
- [ ] Add `ebitda: float | None = None` to `FinancialMetric` (absolute value) and populate from `ebitda` fact — do NOT put this in `ebitda_margin` which is a ratio field
- [ ] Only populate `ebitda_margin` if both `ebitda` and `revenue` are available: `ebitda_margin = ebitda / revenue`
- [ ] Add `net_income: float | None = None` to `FinancialMetric` and populate from `net_income` fact
- [ ] Add `pe_ratio: float | None = None` to `FinancialMetric` and populate from `pe_ratio` fact
- [ ] Add `current_price: float | None = None` to `FinancialMetric` and populate from `current_price` fact
- [ ] Add `eps_ttm: float | None = None` to `FinancialMetric` and populate from `eps_ttm` fact
- [ ] Populate `recurring_revenue_pct` from `recurring_revenue` or `revenue` ratio if available

### Company additions
- [ ] Add `exchange: str | None = None` to `Company` and populate from `exchange` fact
- [ ] Add `sector: str | None = None` to `Company` (distinct from `industry`) and populate from `sector` fact
- [ ] Add `products: list[str]` (default `[]`) to `Company` and populate from `products` fact
- [ ] Add `pricing_model: str | None = None` to `Company` and populate from `pricing_model` fact
- [ ] Add `target_customers: list[str]` (default `[]`) to `Company` and populate from `target_customers` fact
- [ ] Add `funding_rounds: int | None = None` to `Company` and populate from `funding_rounds` fact (also wire from `_signal_funding` source_facts)
- [ ] Add `last_round_stage: str | None = None` to `Company` and populate from `last_round_stage` fact (also wire from `_signal_funding` reasoning)
- [ ] Add `last_round_amount: float | None = None` to `Company` and populate from `last_round_amount` fact
- [ ] Add `patent_count: int | None = None` to `Company` and populate from `total_patents` fact
- [ ] Add `patent_categories: list[str]` (default `[]`) to `Company` and populate from `patent_categories` fact
- [ ] Add `news_sentiment: float | None = None` to `Company` and populate from `sentiment_score` fact
- [ ] Add `news_article_count: int | None = None` to `Company` and populate from `article_count` fact
- [ ] Add `employee_growth_pct: float | None = None` to `Company` and populate from `hiring_velocity` signal value (already extracted in `_signal_hiring_velocity`)
- [ ] Add `ai_jobs_count: int | None = None` to `Company` and populate from `ai_related_positions` fact

### company_builder.py wiring
- [ ] Update `build_company_entity_from_signals()` to pass all new fields into the `Company(...)` constructor call
- [ ] Update `_build_financials()` to populate new `FinancialMetric` fields
- [ ] Ensure all new fields appear in `Company.model_dump()` output

---

## Autonomous Continuation Notes

### Prefer explicit fields over a generic dict
A typed `Company.products: list[str]` is better than `Company.extra_facts["products"]` because it's
type-checked, shows up in model_dump(), and is visible to downstream consumers like the scoring engine.
Only use a generic dict as a last resort for truly variable-schema data.

### Do not add fields with no upstream source
Only add fields that have a confirmed fact type in `_extract_facts_from_source()`. Do not add speculative fields.

### Run tests after each field addition
With `extra="forbid"` active, each field addition unlocks a previously-failing test. This gives a clear,
incremental progress signal.
