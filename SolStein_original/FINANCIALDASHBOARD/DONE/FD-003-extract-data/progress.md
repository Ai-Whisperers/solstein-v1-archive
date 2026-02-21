# FD-003: Progress

## 2026-02-15 - Implementation Complete

**Action**: Executed plan -- implemented all 4 extraction categories and accessor functions.

### Changes Made

**`extract_competitor_data.py`**:
- Added `_parse_eur_k()` helper to normalise revenue-per-employee values (handles both "~EUR 118K" and "EUR 79,500" formats to EUR thousands)
- Added `_extract_year()` and `_latest_metric()` helpers to select the most recent year's data when multiple years exist
- Enhanced `extract_profitability()` with `ebitda_margin_pct` and `revenue_per_employee_eur_k` fields parsed from the raw metrics table
- Enhanced `extract_funding()` with `lead_investors` (deduplicated set from "Lead Investor(s)" column) and `war_chest_signals` (narrative text)
- Added `extract_geographic()` -- extracts `international_revenue_pct` and `countries_count` from "Geographic & Market Expansion" section
- Added `extract_saas_metrics()` -- extracts `deployment_model` (classified as SaaS/Hybrid/On-Premise) and `cloud_revenue_pct` from "SaaS Transition Metrics" table
- Wired `extract_geographic` and `extract_saas_metrics` into `extract_competitor()` output

**`competitor_utils.py`**:
- Added 8 accessor functions: `get_ebitda_margin`, `get_revenue_per_employee`, `get_lead_investors`, `get_war_chest_signals`, `get_international_revenue_pct`, `get_countries_count`, `get_deployment_model`, `get_cloud_revenue_pct`

### Validation Results

- Both files compile clean (`py_compile`)
- No linter errors
- Full extraction of all 24 competitors succeeds (5 expected missing)
- Existing fields (scorecard, revenue, employees, funding rounds) unchanged
- New fields spot-checked against source markdown for seeburger, eneve, engineering-group, eg-utility, tietoevry, indra-minsait, ferranti, soptim
- Revenue per employee normalisation verified: "~EUR 118K" -> 118.0, "EUR 79,500" -> 79.5, "~EUR 200-230K" -> 215.0

### Decisions

- Used `_parse_eur_k()` instead of `parse_number()` for revenue/employee because `parse_number` K-suffix handling (divides by 1000) was designed for revenue-in-millions context, not per-employee values
- Deployment model classification falls back to raw text when it doesn't match SaaS/Hybrid/On-Premise exactly (e.g. "Services company")
- Countries count uses "X countries" text pattern first, then falls back to scanning expansion events table for known country names

**Status**: Implementation complete. Ready for validation.

## 2026-02-15 - Ticket Created

**Action**: Initialized FD-003 ticket for extracting additional data fields.
**Status**: Ready for implementation.
