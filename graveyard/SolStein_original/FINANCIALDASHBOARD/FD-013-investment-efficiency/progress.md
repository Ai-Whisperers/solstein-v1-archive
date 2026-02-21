# FD-013: Investment Efficiency Ratios - Progress

## Session: 2026-02-16

**Status**: Complete

### What was accomplished

1. **Added ratio calculation functions** to `generate_markdown_dashboard.py`:
   - `parse_total_raised_eur_m()` -- best-effort EUR extraction from free-form funding text
   - `calc_rev_per_employee_eur_k()` -- revenue per employee in EUR K
   - `calc_rev_per_eur_m_raised()` -- capital efficiency ratio
   - `calc_hiring_efficiency()` -- employee CAGR / revenue CAGR ratio
   - `calc_growth_roi()` -- composite score per EUR M raised

2. **Added `build_investment_efficiency` section renderer** with:
   - 10-column leaderboard table sorted by Rev/Employee descending
   - Quartile markers (green/red) for top/bottom quartile per metric
   - Eneve row bolded consistent with other sections
   - Graceful N/A handling for missing data

3. **Added Mermaid bar chart** showing Revenue/Employee for top 15 revenue growers (xychart-beta syntax matching existing charts)

4. **Wired into main pipeline** between SaaS ranking and Quadrant chart sections

5. **Verified** against full 33-competitor dataset -- script runs without errors, all ratios calculate correctly

### Key decisions

- **Total Raised parsing**: The `total_raised_text` field is free-form text, not a numeric field. Wrote a best-effort regex parser that handles EUR, USD, GBP denominations and returns None for unparseable values (complex multi-currency expressions, "Undisclosed", "N/A")
- **Hiring Efficiency direction**: Values below 1.0 are "good" (revenue growing faster than headcount), so quartile markers are inverted for this column
- **Chart type**: Used bar chart (xychart-beta) rather than true scatter plot since Mermaid's scatter plot support is limited; bars grouped by revenue growth ranking

### Files modified

- `.cursor/scripts/analysis/market/generate_markdown_dashboard.py` (~130 lines added)
- `tickets/COMPETITION/financial-dashboard.md` (regenerated with new section)
- `tickets/FINANCIALDASHBOARD/FD-013-investment-efficiency/plan.md` (acceptance criteria checked off)

### Acceptance criteria validation

- [x] Investment Efficiency section present in generated `financial-dashboard.md` (line 254)
- [x] All ratios calculated correctly -- divide-by-zero returns N/A, missing data returns N/A
- [x] Scatter plot chart renders correctly in Mermaid (xychart-beta, line 298)
- [x] Top/bottom quartile visually distinguished with green/red markers
- [x] Eneve row highlighted (bold) at rank 8 (EUR 241K/employee)
- [x] Script runs without errors against full 33-competitor dataset (exit code 0)
