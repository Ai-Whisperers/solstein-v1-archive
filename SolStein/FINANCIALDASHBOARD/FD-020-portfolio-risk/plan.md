# FD-020: Portfolio Risk Dashboard Sheet

## Objective

Add a "Portfolio Risk" sheet that aggregates competitive threats at portfolio level. This flips the view from single-company analysis to how PE firms actually think: across their entire portfolio. Scope: one new sheet in the existing workbook with KPIs, risk matrix, bubble chart, and top-5 summary. Out of scope: interactive filtering (covered by FD-021) and styling (covered by FD-022).

## Requirements

1. Summary KPI tiles:
   - Total Rockets in market
   - Total capital deployed by Rockets (EUR)
   - Competitors with AI in production
   - Competitors operating in NL
   - Average SaaS maturity vs Eneve's SaaS maturity
2. Risk matrix: categorize each competitor by threat proximity (Immediate/Near-term/Long-term/Negligible) and threat severity (Critical/High/Medium/Low)
3. Include columns: Company, Threat Proximity, Threat Severity, Risk Category, Primary Risk Factor, Mitigation
4. Chart: bubble chart with proximity on X-axis, severity on Y-axis, bubble size = revenue or funding
5. Top 5 risks summary with one-line descriptions

## Data Sources

- Existing composite scores, tier classifications
- `deep-analysis.md` threat assessments
- `financial-dashboard.md` Meteor Warning narrative

## Implementation Strategy

1. **Extract risk data**: In `extract_competitor_data.py`, add logic to derive threat proximity and severity from existing tier classifications, composite scores, and deep-analysis threat assessments. Map classifications to proximity/severity enums.
2. **Build risk matrix**: In `generate_excel_report.py`, add a `_create_portfolio_risk_sheet()` method. Write KPI summary tiles in the top rows, then populate the full competitor risk matrix table below.
3. **Add bubble chart**: Use openpyxl `BubbleChart` to plot proximity (X) vs severity (Y) with bubble size mapped to revenue or total funding. Position chart beside or below the risk matrix.
4. **Add top-5 summary**: Sort competitors by combined risk score (proximity x severity), extract top 5, and write one-line risk descriptions below the chart.
5. **Handle missing data**: Competitors without revenue/funding data get minimum bubble size; competitors without sufficient data for classification get "Unrated" category with a note.

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires synthesis of multiple data points (tier, composite scores, threat assessments) into a new risk classification scheme, plus a chart type (BubbleChart) not yet used in the workbook.

**Criteria Met**:
- Root Cause: Multiple data sources to synthesize (not a single change)
- Files Affected: 2 (`extract_competitor_data.py`, `generate_excel_report.py`)
- Lines Changed: ~150-200 (new sheet function + extraction logic)
- Risk Level: Low-Medium (additive, no modification of existing sheets)
- Solution Pattern: Partially known (sheet creation pattern established; BubbleChart is new)
- Effort: 2-3h

## Acceptance Criteria

- [ ] Portfolio Risk sheet present in workbook
- [ ] KPI summary tiles at top (all 5 metrics populated)
- [ ] All 33 competitors in risk matrix with proximity, severity, and risk category
- [ ] Bubble chart renders correctly with labeled axes
- [ ] Top 5 risks identified with one-line descriptions
- [ ] Competitors with missing revenue/funding handled gracefully (no errors, minimum bubble size or "N/A")
- [ ] Sheet follows existing workbook patterns (consistent header style, Eneve highlighted)

## Status

**Complete** -- Implemented and validated
