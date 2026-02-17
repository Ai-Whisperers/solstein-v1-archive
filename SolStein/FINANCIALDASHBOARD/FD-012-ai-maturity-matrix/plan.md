# FD-012: AI Maturity Matrix Sheet

## Objective

Add a dedicated "AI Maturity" sheet that scores every competitor on AI adoption level. This is THE differentiator question PE/VC firms cannot answer today -- no consulting firm delivers this.

**Scope**: In scope: AI scoring sheet, heatmap formatting, bar chart, Eneve positioning. Out of scope: AI capability deep-dives per competitor, AI trend-over-time analysis.

## Requirements

1. Extract AI adoption signals from each competitor's `deep-analysis.md` file (AI & Innovation section) where available; for competitors without deep-analysis, extract signals from `financial-growth.md` and company markdown files, or default to score 0 with "No Data" flag
2. Score each competitor on AI maturity scale: None (0), Low (1-2), Moderate (3-4), Strong (5-7), Very Strong (8-10)
3. Include columns: Company, Tier, AI Score, AI Signal Level, Key AI Capabilities, AI Staff %, AI in Production (Y/N)
4. Conditional formatting: heatmap gradient from red (None) through yellow (Moderate) to green (Very Strong)
5. Chart: horizontal bar chart ranking all competitors by AI score with axis labels and company names visible
6. Highlight Eneve's position (currently: zero AI features, not on the board) using gold fill consistent with existing dashboard styling
7. Sort by AI score descending

## Data Sources

- `deep-analysis.md` per competitor (AI & Innovation section) -- available for 5 competitors (dexter, octopus-energy-kraken, hansen-technologies, creatica, eneve)
- `financial-growth.md` and company markdown files for remaining ~28 competitors (partial AI signals)
- `competitor_data.json` for baseline company/tier data
- Eneve baseline: AI score 0, no AI in production

## Implementation Strategy

1. **Add AI extraction logic to `competitor_utils.py`**: Create helper functions `get_ai_score()`, `get_ai_signal_level()`, `get_ai_capabilities()`, `get_ai_staff_pct()`, `get_ai_in_production()` that parse the AI & Innovation section from deep-analysis data in `competitor_data.json`
2. **Extend `competitor_data.json` schema**: Add AI-related fields per competitor. For the 5 with deep-analysis, populate from the AI & Innovation table. For the remaining 28, populate with best-effort data from existing markdown files or mark as "No Data"
3. **Add `_write_ai_maturity_sheet()` function in `generate_excel_report.py`**: Follow the existing sheet-writing pattern (header row, data rows, conditional formatting, Eneve highlight). Apply `ColorScaleRule` for red-yellow-green heatmap on AI Score column
4. **Add horizontal bar chart**: Use openpyxl `BarChart` (type="bar" for horizontal) referencing Company and AI Score columns, sorted descending
5. **Register the new sheet** in the main pipeline function alongside existing sheets
6. **Test**: Verify sheet renders in Excel, heatmap applies, chart is readable, Eneve is highlighted

**Key files**:
- `.cursor/scripts/analysis/market/generate_excel_report.py` (new sheet function)
- `.cursor/scripts/analysis/market/competitor_utils.py` (new AI extraction helpers)
- `tickets/COMPETITION/competitor_data.json` (AI data enrichment)

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires new data extraction logic for AI signals not currently parsed, extending the JSON schema, and creating a new sheet with chart -- affecting multiple files with new utility functions.

**Criteria Met**:
- Root Cause: Multiple (data extraction + new sheet + chart)
- Files Affected: 3 (generate_excel_report.py, competitor_utils.py, competitor_data.json)
- Lines Changed: ~80-120 (new functions + sheet writer + data)
- Risk Level: Medium (new data fields may have gaps for competitors without deep-analysis)
- Solution Pattern: Known (follows existing sheet-writing pattern in generate_excel_report.py)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Acceptance Criteria

- [x] AI Maturity sheet present in workbook
- [x] All 33 competitors scored (competitors without deep-analysis data flagged as "No Data" with score 0)
- [x] Heatmap conditional formatting applied (red-yellow-green gradient on AI Score column)
- [x] Horizontal bar chart renders with company names on Y-axis and AI scores on X-axis
- [x] Eneve highlighted with gold fill and its AI score position visible
- [x] Data sourced from deep-analysis.md AI & Innovation section where available

## Status

**Current**: Implementation Complete (2026-02-16)
