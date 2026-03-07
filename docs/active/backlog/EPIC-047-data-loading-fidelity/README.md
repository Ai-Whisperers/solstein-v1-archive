# EPIC-047: Data Loading Fidelity

> **Discovered**: 2026-03-01 via live end-to-end run analysis  
> **Priority**: P1 — High (scoring accuracy depends on correct data ingestion)  
> **Stories**: 4 (STORY-177 through STORY-180)  
> **Effort**: M (3–4 days total)

---

## Problem

When `data/input/competitor_data.json` is loaded into `Company` objects, several fields are silently lost or transformed incorrectly. The scoring engine receives fewer fields than the raw data contains, producing scores based on an incomplete picture of each company.

### Field Mapping Issues Found for Eneve

| JSON Field | JSON Value | Company Object Field | Company Value | Issue |
|-----------|-----------|---------------------|---------------|-------|
| `ai_score` | `7.5` | `ai_score` | `7` | Truncated to integer |
| `funding_raised` | `2,000,000` EUR | `financials.total_funding_raised` | `None` | Field not mapped |
| `profitability.ebitda_margin_pct` | `30` | — | Not exposed | Missing |
| `profitability.recurring_revenue_pct` | `85` | — | Not exposed | Missing |
| `enrichment_source_count` | `3` | `enrichment_source_count` | `0` | Field name mismatch |
| `growth_rate` (decimal) | `0.25` | `financials.growth_rate` | `35.0` (from timeline) | Source not used |

These are not cosmetic issues. Funding data directly impacts Financial Health Score and Growth Momentum Score. Missing recurring revenue (85%) is a strong signal for SaaS companies. EBITDA margin affects competitive positioning. The scoring engine produces lower scores than the data warrants.

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| STORY-177 | Fix `ai_score` float truncation in company loaders | P1 | S |
| STORY-178 | Map `funding_raised` to `financials.total_funding_raised` | P1 | S |
| STORY-179 | Expose `ebitda_margin_pct` and `recurring_revenue_pct` on `Company` model | P1 | M |
| STORY-180 | Add field mapping parity test between raw JSON and `Company` objects | P1 | M |

---

## Definition of Done

- [ ] All JSON fields in `competitor_data.json` have a corresponding `Company` attribute
- [ ] No field is silently truncated or type-coerced incorrectly
- [ ] A parity test verifies mapping completeness for all known input formats
- [ ] Scoring re-run on Eneve produces higher Financial Health and Growth Momentum scores (evidence that funding data is now being used)
