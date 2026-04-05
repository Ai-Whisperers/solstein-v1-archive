# EPIC-086: Pipeline Field Loss — Silent Data Corruption

| Field | Value |
|-------|-------|
| **Status** | ✅ Complete |
| **Priority** | P0 — CRITICAL |
| **Phase** | P0 — Must resolve before any pipeline work |
| **Effort** | L (5–7 days) |
| **Stories** | 4 ([STORY-348](STORIES/STORY-348.md) through [STORY-351](STORIES/STORY-351.md)) |
| **Created** | 2026-04-02 |
| **Updated** | 2026-04-05 (standardized metadata; all 4 stories done as of 2026-04-03) |
| **Audit Reference** | `docs/audit-2026-04-02.md` (Section: Field Loss Root Cause) |

---

## Why This Is P0

The pipeline is the core product. Every output — scores, classifications, reports, exports — is derived from
data that flows through a 4-layer transformation chain. At each layer, fields are **silently dropped** with
no error, no warning, and no test. The result is:

- Scoring runs on incomplete data → produces **hallucinated/misleading scores**
- Classification assigns tiers based on absent signals → **Phoenix/Salt/Lead labels are not trustworthy**
- Exported reports contain fabricated narrative where real data should be
- Every new adapter, signal, or field added to the system will suffer the same silent loss until this is fixed

**This is not a data quality issue. It is a structural correctness issue.** Nothing built on top of this pipeline
is reliable until the field propagation is verified and enforced.

---

## The Four Loss Layers (Root Cause — Confirmed 2026-04-02)

### Layer 1 — `aggregate.py`: Adapter output → Facts
Each source type has a hardcoded extractor (`_extract_yahoo_finance`, `_extract_crunchbase`, etc.).
Only fields explicitly listed in each extractor survive. Any new adapter field not listed is **dropped silently**.

### Layer 2 — `signals.py`: Facts → Signals (LARGEST DROP)
Only **10 signal extractors** are defined. The following fact types are **collected but never converted
to any signal** and therefore never reach the Company model:
- `ebitda`, `net_income`, `pe_ratio`, `current_price`, `eps_ttm`
- `products`, `pricing_model`, `target_customers`
- `positive_article_count`, `negative_article_count`
- `patent_categories`, `last_round_amount`, `sector`, `exchange`

Additionally, five fact types (`last_round_stage`, `funding_rounds`, `employee_growth_pct`, `ai_related_positions`, `ai_signal_strength`) have signal extractors but their values are **not mapped to Company fields** — this is a Layer 3 gap, not Layer 2.

### Layer 3 — `company_builder.py`: Signals + Facts → Company
Only a subset of signals and facts is explicitly mapped into the `Company` constructor.
`FinancialMetric` has `ebitda_margin` (a ratio) and `recurring_revenue_pct` fields that are never populated.
The absolute `ebitda` value needs its own field (`ebitda: float | None`) — do not conflate with `ebitda_margin`.

### Layer 4 — `extra="ignore"` on domain models (MAKES ALL LOSSES INVISIBLE)
`Company` and `FinancialMetric` are both configured with `model_config = ConfigDict(extra="ignore")`.
This was set deliberately in STORY-251 to prevent unknown keys from leaking out, but the side effect is
that every mapping error in Layers 1–3 produces **zero observable signal** — no exception, no log line,
no test failure. The domain models become a silent corruption sink.

---

## Stories

| Story | Title | Priority | Size | Blocks |
|-------|-------|----------|------|--------|
| [STORY-348](STORIES/STORY-348.md) | Change `extra="ignore"` to `extra="forbid"` on Company and FinancialMetric | P0 | S | All others — this makes all existing losses visible |
| [STORY-349](STORIES/STORY-349.md) | Add signal extractors for all orphaned fact types | P0 | M | [STORY-350](STORIES/STORY-350.md) |
| [STORY-350](STORIES/STORY-350.md) | Map all surviving signals and facts to Company/FinancialMetric fields | P0 | M | — |
| [STORY-351](STORIES/STORY-351.md) | Add field-count regression gate: assert field survival across all pipeline layers | P0 | S | — |

**Execution order: 348 → 349 → 350 → 351** (run in sequence; each story will cause failures that the next fixes)

---

## Definition of Done

- [x] `extra="forbid"` enforced on `Company` and `FinancialMetric` ([STORY-348](STORIES/STORY-348.md))
- [x] All orphaned fact types have signal extractors (ebitda, net_income, pe_ratio, current_price, eps_ttm added; 15 extractors total) ([STORY-349](STORIES/STORY-349.md))
- [x] All surviving signals and facts mapped to Company/FinancialMetric fields; 5 new FinancialMetric fields + 14 new Company fields ([STORY-350](STORIES/STORY-350.md))
- [x] Pipeline regression test asserts field survival across all layers (8 tests in test_pipeline_field_survival.py) ([STORY-351](STORIES/STORY-351.md))
- [x] `ruff check` and `pytest` both pass at 0 errors
- [x] No existing test deleted or weakened

---

## Acceptance Criteria

**AC-1**: Passing `Company(id="x", name="y", unknown_field=123)` raises a `ValidationError`. Currently it silently discards `unknown_field`.

**AC-2**: A company enriched with `ebitda=$500M` from YahooFinance has that value present in `company.financials.ebitda_margin` (or an equivalent mapped field) after the full pipeline.

**AC-3**: A pipeline regression test logs field names present at adapter output and asserts they are present in `Company.model_dump()` or an explicit documented exclusion list.

**AC-4**: `extract_signals()` has extractors for all fact types currently produced by `_extract_facts_from_source()`. Any un-extracted fact type triggers a test failure.

---

## Implementation Notes

### [STORY-348](STORIES/STORY-348.md) will break existing tests intentionally
Changing to `extra="forbid"` will expose every place in the codebase that passes undeclared fields to
`Company` or `FinancialMetric`. **Each failure is a real bug, not a test problem.** Fix the caller,
not the model config.

### Do NOT revert to `extra="ignore"` as a workaround
If any test passes an undeclared field, fix the field mapping — don't silence the error.

### The orphaned fact types already exist in the aggregated record
They are produced correctly by the adapters and aggregated correctly by `DefaultFactAggregator`.
They just have no onward path. Adding signal extractors or direct Company field mappings is sufficient.

### Reference files
- `src/solstein/research/aggregate.py` — Layer 1+2 extractors
- `src/solstein/research/signals.py` — Layer 2 signal definitions (`_SIGNAL_EXTRACTORS` list)
- `src/solstein/research/company_builder.py` — Layer 3 Company construction
- `src/solstein/domain/models.py` — Layer 4 `Company` and `FinancialMetric` with `extra="ignore"`
