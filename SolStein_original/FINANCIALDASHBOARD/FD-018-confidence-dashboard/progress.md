# FD-018: Confidence Dashboard - Progress

## Session: 2026-02-16

**Status**: Complete

### What was done

1. **Added confidence-counting helpers** to `generate_excel_report.py`:
   - `_classify_confidence(tag)` -- maps raw strings ("Confirmed (range)", "Estimated (proxy)", etc.) to canonical buckets
   - `_count_confidence_from_markdown(md_path)` -- regex-parses the full `financial-growth.md` for all confidence annotations across Revenue, Profitability, Funding, and Employee tables
   - `_count_confidence_from_json(comp)` -- fallback counting from `revenue.timeline[].confidence` in the already-extracted JSON
   - `count_confidence_tags(comp, link_base)` -- orchestrator that prefers markdown source when available
   - `calc_confidence_ratio(confirmed, estimated, unknown)` -- returns Confirmed / Total percentage, handles zero-total
   - `get_quality_rating(ratio)` -- returns "High" / "Medium" / "Low" / "N/A" per defined thresholds

2. **Added `write_confidence_sheet(wb, competitors, link_base)`**:
   - Header row: Company, Tier, Confirmed, Estimated, Unknown, Confidence %, Data Quality Rating
   - 33 competitor rows sorted by confidence ratio (descending)
   - Summary row with portfolio-level aggregates
   - Cell-level conditional formatting on Data Quality Rating column (green/yellow/red fills)
   - ColorScaleRule on Confidence % column (red-yellow-green gradient)
   - Stacked bar chart (Confirmed / Estimated / Unknown per competitor) positioned below the data table

3. **Wired into pipeline**: Added `("Data Confidence", write_confidence_sheet, ...)` to the `sheets` list in `generate_workbook()`, positioned between Threat Timeline and Raw Data

### Validation results

| # | Acceptance Criterion | Status |
|---|---|---|
| 1 | "Data Confidence" sheet present | Pass |
| 2 | All 33 competitors listed (one row each) | Pass (33 rows) |
| 3 | Columns: Company, Tier, Confirmed, Estimated, Unknown, Confidence %, Data Quality Rating | Pass |
| 4 | Confidence % = Confirmed / (Confirmed + Estimated + Unknown) | Pass (verified: 6/7 = 85.7%) |
| 5 | Data Quality Rating: High (>70%), Medium (40-70%), Low (<40%) | Pass (boundary tests: 71=High, 70=Medium, 40=Medium, 39=Low) |
| 6 | Conditional formatting: green/yellow/red on Confidence % | Pass (ColorScaleRule + cell fills) |
| 7 | Stacked bar chart renders | Pass (1 chart present) |
| 8 | Summary row with portfolio confidence | Pass (PORTFOLIO TOTAL: 90 Confirmed, 86 Estimated, 19 Unknown, 46.2%, Medium) |
| 9 | Zero-total edge case handled | Pass (returns None/N/A, no division by zero) |

### Files modified

- `.cursor/scripts/analysis/market/generate_excel_report.py` -- added `import re`, confidence helpers (~60 lines), `write_confidence_sheet` (~100 lines), pipeline wiring (1 line)

### Decisions

- **Markdown-first parsing**: The implementation reads the raw `financial-growth.md` files when `link_base` is available, capturing confidence tags from all table sections (Revenue, Profitability, Funding, Employees). Falls back to revenue-timeline-only data from JSON when source files are unavailable.
- **Sort order**: Competitors are sorted by descending confidence ratio so highest-quality research appears first.
- **Chart colors**: Used blue (Confirmed), orange (Estimated), gray (Unknown) for the stacked bar chart to visually distinguish data quality levels.
