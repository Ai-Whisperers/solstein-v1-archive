# FD-013: Investment Efficiency Ratios Sheet

## Objective

Add an "Investment Efficiency" section to the financial dashboard showing capital efficiency metrics. PE firms use these ratios to evaluate who is building real value vs burning cash. This enables Eneve positioning analysis against competitors on capital efficiency dimensions.

**Scope**: New dashboard section with calculated ratios, leaderboard table, and scatter plot chart. Uses existing extracted competitor data only -- no new data collection required.

## Requirements

1. Calculate and display per competitor:
   - Revenue per Employee (EUR)
   - Revenue per EUR M Raised (capital efficiency)
   - Employee Growth vs Revenue Growth ratio (hiring efficiency)
   - Composite Score per EUR M Raised (growth ROI)
2. Include columns: Company, Tier, Revenue, Headcount, Total Raised, Rev/Employee, Rev/EUR M Raised, Classification
3. Conditional formatting: highlight top quartile (green) and bottom quartile (red) per metric
4. Chart: scatter plot of Revenue/Employee vs Revenue Growth (shows who's lean AND growing)
5. Sort by Revenue per Employee descending (default), with filter capability
6. Handle missing data gracefully (N/A for unfunded companies, missing headcount, or missing revenue)

## Data Sources

- Existing extracted competitor data (revenue, headcount, funding) from per-competitor `financial-growth.md` files
- JSON data loaded by `generate_markdown_dashboard.py`

## Implementation Strategy

1. **Add ratio calculation functions** to `generate_markdown_dashboard.py`:
   - `calc_rev_per_employee(revenue, headcount)` -- returns N/A if either value is None or zero
   - `calc_rev_per_eur_m_raised(revenue, total_raised)` -- returns N/A for unfunded companies
   - `calc_hiring_efficiency(emp_growth, rev_growth)` -- ratio of employee CAGR to revenue CAGR
   - `calc_growth_roi(composite, total_raised)` -- composite score per EUR M raised
2. **Add `build_investment_efficiency` section renderer** following the existing pattern used by `build_classification_matrix`, `build_revenue_leaderboard`, etc.
3. **Add Mermaid scatter plot** for Revenue/Employee vs Revenue Growth using `xychart-beta` syntax (consistent with existing charts)
4. **Wire into main pipeline** by calling the new section renderer in the `main()` function alongside existing section builders
5. **Verify** by running the script against existing competitor data and reviewing the generated markdown output

**Key files**:
- `.cursor/scripts/analysis/market/generate_markdown_dashboard.py` (main script)
- `.cursor/scripts/analysis/market/competitor_utils.py` (shared utilities)

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: All input data already exists in the extracted competitor JSON. This adds new ratio calculations and a new section renderer following an established pattern in the existing script.

**Criteria**:
- Root Cause: Single scope (add new section to existing dashboard generator)
- Files Affected: 1-2 (generation script, possibly competitor_utils)
- Lines Changed: ~50-80 lines (new functions + section renderer)
- Risk Level: Low (additive change, no modification to existing sections)
- Solution Pattern: Well-understood (follows existing leaderboard/chart pattern in the same script)

## Acceptance Criteria

- [x] Investment Efficiency section present in generated `financial-dashboard.md`
- [x] All ratios calculated correctly (handle divide-by-zero for unfunded companies and missing data)
- [x] Scatter plot chart renders correctly in Mermaid
- [x] Top/bottom quartile competitors visually distinguished in the table
- [x] Eneve row highlighted (bold) consistent with existing dashboard sections
- [x] Script runs without errors against full 33-competitor dataset

## Status

**Current**: Implementation complete, all acceptance criteria met
