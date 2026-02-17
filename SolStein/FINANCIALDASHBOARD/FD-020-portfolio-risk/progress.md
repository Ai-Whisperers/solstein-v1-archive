# FD-020: Portfolio Risk Dashboard - Progress

## Session: 2026-02-16

### Completed

- **Risk classification helpers** added to `generate_excel_report.py`:
  - `_classify_threat_proximity()`: Rocket+geo>=6 = Immediate, Rocket = Near-term, Riser+geo>=5 = Near-term, composite>=5 = Long-term, else Negligible
  - `_classify_threat_severity()`: Rocket+revenue>=100M or funded>=100M = Critical, Rocket = High, Riser+rev>=50M = High, Riser = Medium, composite>=4 = Medium, else Low
  - `_risk_category()`: combined proximity x severity score mapped to Critical/High/Moderate/Low Risk
  - `_primary_risk_factor()`: one-line summary from classification, revenue, funding, AI, SaaS signals
  - `_risk_mitigation()`: tailored mitigation advice per competitor profile
  - `_bubble_size()`: revenue or funding EUR M, minimum 1.0 for missing data

- **`write_portfolio_risk_sheet()`**: Full sheet function with:
  - KPI tiles: Rockets in market (6), Rocket capital (EUR 5633M), AI in production (0), Operating in NL est. (17), Average SaaS maturity (Market: 6.1 vs Eneve: 4.0)
  - Risk matrix: all 33 competitors with Rank, Company, Tier, Threat Proximity, Threat Severity, Risk Category, Primary Risk Factor, Mitigation
  - BubbleChart: proximity (X) vs severity (Y), bubble size = revenue/funding
  - Top 5 risks summary section with company links

- **Workbook registration**: Sheet added between "Threat Timeline" and "Data Confidence" (sheet count updated 17 -> 18)

- **Import**: `BubbleChart` added to openpyxl chart imports

### Validation Results

All 7 acceptance criteria passed:
- [x] Portfolio Risk sheet present in workbook
- [x] KPI summary tiles at top (all 5 metrics populated)
- [x] All 33 competitors in risk matrix with proximity, severity, and risk category
- [x] Bubble chart renders correctly with labeled axes
- [x] Top 5 risks identified with one-line descriptions
- [x] Competitors with missing revenue/funding handled gracefully (minimum bubble size 1.0)
- [x] Sheet follows existing workbook patterns (consistent header style, Eneve highlighted)

### Files Modified

- `.cursor/scripts/analysis/market/generate_excel_report.py`: +~200 lines (risk helpers + sheet function + registration)

### Decisions

- Risk classification derived from existing extracted data (composite scores, tier, geographic expansion, funding) rather than modifying `extract_competitor_data.py` -- keeps extraction pipeline unchanged
- "Operating in NL" KPI uses geographic expansion score >= 6 as proxy since country-level data is not extracted
- Used openpyxl `BubbleChart` (not previously used in workbook) with numeric proximity/severity axes
