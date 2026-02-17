# FD-018: Confidence Dashboard Sheet

## Objective

Add a "Data Confidence" sheet to the Excel report showing research quality per competitor. Differentiator vs consulting firms that present estimates as facts. Shows intellectual honesty and research depth.

**In scope**: New Excel sheet with confidence metrics, conditional formatting, stacked bar chart, and portfolio summary.
**Out of scope**: Changes to existing sheets; modifying how confidence tags are stored in competitor markdown files.

## Requirements

1. Per competitor, count data points by confidence level: Confirmed, Estimated, Unknown
2. Calculate confidence ratio: Confirmed / (Confirmed + Estimated + Unknown)
3. Include columns: Company, Tier, Confirmed Count, Estimated Count, Unknown Count, Confidence %, Data Quality Rating
4. Data Quality Rating: High (>70% confirmed), Medium (40-70%), Low (<40%)
5. Conditional formatting: green/yellow/red based on confidence %
6. Chart: stacked bar chart showing Confirmed vs Estimated vs Unknown per competitor
7. Summary row: overall portfolio confidence level (aggregated across all competitors)

## Implementation Strategy

1. **Add confidence-counting helper** to `generate_excel_report.py`:
   - `count_confidence_tags(competitor: dict) -> tuple[int, int, int]` -- returns (confirmed, estimated, unknown) counts by scanning the competitor's source markdown content for `Confirmed`, `Estimated`, `Unknown` annotations
   - `calc_confidence_ratio(confirmed, estimated, unknown) -> float` -- returns ratio, handles zero-total edge case
   - `get_quality_rating(ratio: float) -> str` -- returns "High" / "Medium" / "Low" per thresholds

2. **Add `write_confidence_sheet(wb, competitors, link_base)`** following the existing pattern used by `write_efficiency_sheet`, `write_summary_sheet`, etc.:
   - Header row: Company | Tier | Confirmed | Estimated | Unknown | Confidence % | Data Quality Rating
   - One row per competitor (all 33)
   - Summary row at bottom with portfolio-level aggregates
   - Apply conditional formatting (green/yellow/red color scale on Confidence % column)

3. **Add stacked bar chart** using `openpyxl.chart.BarChart` with `grouping="stacked"`:
   - Categories: competitor names
   - Series: Confirmed, Estimated, Unknown counts
   - Position chart below the data table

4. **Wire into main pipeline** by adding `("Data Confidence", write_confidence_sheet, [wb, competitors, link_base])` to the `sheets` list in `generate_workbook()`

5. **Verify** by running `generate_excel_report.py` against existing competitor data, confirming the sheet renders with correct metrics and chart

**Key files**:
- `.cursor/scripts/analysis/market/generate_excel_report.py` (main script -- add sheet writer + helpers)
- `tickets/COMPETITION/*/financial-growth.md` (data source -- confidence annotations)

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires parsing confidence tags from unstructured markdown files, creating a new Excel sheet with conditional formatting and a stacked bar chart. Follows an established pattern but involves non-trivial text parsing.

**Criteria**:
- Root Cause: N/A (new feature, not a fix)
- Files Affected: 1 (generate_excel_report.py)
- Lines Changed: ~80-120 (helper functions + sheet writer + chart + pipeline wiring)
- Risk Level: Low (additive change, no modification to existing sheets)
- Solution Pattern: Known (follows existing `write_*_sheet` pattern in the codebase)

**Effort**: ~1h

## Acceptance Criteria

- [ ] "Data Confidence" sheet present in generated Excel workbook
- [ ] All 33 competitors listed with confidence metrics (one row each)
- [ ] Columns present: Company, Tier, Confirmed Count, Estimated Count, Unknown Count, Confidence %, Data Quality Rating
- [ ] Confidence % calculated correctly as Confirmed / (Confirmed + Estimated + Unknown)
- [ ] Data Quality Rating displays High (>70%), Medium (40-70%), Low (<40%) correctly
- [ ] Conditional formatting applied: green (High), yellow (Medium), red (Low) on Confidence % column
- [ ] Stacked bar chart renders with Confirmed / Estimated / Unknown per competitor
- [ ] Summary row displays overall portfolio confidence level
- [ ] Zero-total edge case handled gracefully (no division by zero)

## Status

Complete
