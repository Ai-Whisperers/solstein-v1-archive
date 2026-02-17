# FD-008: Methodology Sheet

## Objective

Add a "Methodology" sheet as the last sheet in the workbook. This sheet answers the inevitable board question: "Where does this data come from?" It builds credibility and transparency by documenting data sources, confidence levels, scoring methodology, and caveats.

## Requirements

1. Add a new `write_methodology_sheet()` function to `generate_excel_report.py`
2. Sheet must contain 7 fixed-text sections: Data Sources, Confidence Levels, Scoring Methodology, Classification Thresholds, Currency Conversion, Data Freshness, Caveats & Limitations
3. Data Freshness section must pull live values from `data["metadata"]` (total_folders, with_financial_data, without_financial_data)
4. Sheet must be the last tab in the workbook (called after all other sheet writers)
5. Professional formatting consistent with existing sheets (header style, dark navy section headers)
6. No grid lines on the Methodology sheet for a cleaner document-style appearance

## Complexity Assessment

- **Classification**: Simple Fix (static content, no data processing)
- **Effort**: 30 minutes
- **Risk**: Low (new sheet with fixed content, no logic)
- **Files**: `generate_excel_report.py`

## Acceptance Criteria

- [ ] "Methodology" sheet is the last tab in the workbook
- [ ] Contains the following sections:
  1. **Data Sources**: Summary of where competitor data comes from
  2. **Confidence Levels**: Explanation of High / Medium / Low / Estimated
  3. **Scoring Methodology**: The 6 scorecard dimensions, scale (1-10), composite calculation
  4. **Classification Thresholds**: Rocket (7.0-10.0), Riser (5.0-6.9), Steady (3.0-4.9), Dinosaur (1.0-2.9)
  5. **Currency Conversion**: Notes on EUR conversion methodology
  6. **Data Freshness**: Date of last data update (from metadata)
  7. **Caveats & Limitations**: Known data gaps, estimation methodology
- [ ] Professional formatting (same header style as other sheets)
- [ ] Content is human-readable, not a data table
- [ ] Script compiles clean

## Implementation Strategy

### 1. `write_methodology_sheet()` Function

This is a text-heavy sheet, not a data table. Use merged cells and multi-line text:

```python
def write_methodology_sheet(wb: Workbook, data: dict) -> None:
    """Methodology and data quality notes."""
    ws = wb.create_sheet("Methodology")
    
    sections = [
        ("DATA SOURCES", [
            "Financial data is sourced from a combination of:",
            "  - Public annual reports and financial filings",
            "  - Market research databases (Gartner, IDC, Forrester)",
            "  - Company press releases and investor presentations",
            "  - Industry analyst reports and news articles",
            "  - LinkedIn data for employee headcount trends",
            "  - Crunchbase/PitchBook for funding data",
        ]),
        ("CONFIDENCE LEVELS", [
            "Each data point is assessed for confidence:",
            "  - High: Direct from official source (annual report, regulatory filing)",
            "  - Medium: From reputable secondary source or cross-referenced",
            "  - Low: Single unverified source or analyst estimate",
            "  - Estimated: Calculated/interpolated from available data points",
        ]),
        ("SCORING METHODOLOGY", [
            "Each competitor is scored across 6 dimensions on a 1-10 scale:",
            "  1. Revenue Growth: YoY and CAGR trajectory",
            "  2. Funding Momentum: Capital raised, valuation trajectory",
            "  3. Employee Growth: Headcount CAGR, hiring signals",
            "  4. Geographic Expansion: International presence, new markets",
            "  5. M&A Activity: Acquisition cadence, strategic fit",
            "  6. SaaS Maturity: Cloud revenue %, recurring revenue %",
            "",
            "Composite Score = Average of all 6 dimension scores",
        ]),
        ("CLASSIFICATION THRESHOLDS", [
            "Based on composite score:",
            "  - Rocket: 7.0 - 10.0 (high-growth, aggressive competitor)",
            "  - Riser: 5.0 - 6.9 (growing steadily, gaining momentum)",
            "  - Steady: 3.0 - 4.9 (stable, moderate growth)",
            "  - Dinosaur: 1.0 - 2.9 (declining or stagnant)",
        ]),
        ("CURRENCY CONVERSION", [
            "All revenue figures converted to EUR using annual average exchange rates.",
            "Source currencies include USD, NOK, SEK, PLN, GBP.",
            "Conversion rates sourced from European Central Bank annual averages.",
        ]),
        ("DATA FRESHNESS", [
            f"Total competitors tracked: {data.get('metadata', {}).get('total_folders', 'N/A')}",
            f"Competitors with financial data: {data.get('metadata', {}).get('with_financial_data', 'N/A')}",
            f"Competitors without financial data: {data.get('metadata', {}).get('without_financial_data', 'N/A')}",
            f"Source directory: {data.get('metadata', {}).get('source_directory', 'N/A')}",
        ]),
        ("CAVEATS & LIMITATIONS", [
            "- Not all competitors disclose financial data publicly",
            "- Revenue figures for private companies are estimates unless noted",
            "- Employee counts from LinkedIn may include contractors",
            "- Funding data may be incomplete for bootstrapped companies",
            "- Geographic data reflects known market presence, not exhaustive coverage",
            "- Scores reflect relative positioning within this competitor set",
        ]),
    ]
```

### 2. Layout

```
Row 1: Title "METHODOLOGY & DATA QUALITY" (merged, styled as header)
Row 3+: Section headers (bold, dark navy font) followed by content rows
Each section separated by a blank row
Column A used for all text (wide column, ~100 chars)
```

### 3. Styling

- Section headers: Bold, dark navy, 12pt
- Content: Regular, 10pt, wrapped text
- Column A width: 100 characters
- No grid lines on this sheet (cleaner look): `ws.sheet_view.showGridLines = False`

### 4. Wire into `generate_workbook()`

Add as the last sheet call and pass `data` (not just `competitors`):

```python
log.info("Writing Methodology...")
write_methodology_sheet(wb, data)
```

Note: This function takes `data` (the full JSON dict) instead of just `competitors`, because it needs metadata.

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook and verify:
   - Methodology is the last tab
   - All 7 sections present and readable
   - Data freshness numbers match actual data
   - Grid lines are hidden
   - Text wraps properly

## Risks

- Minimal. This is static content with no data processing.

## Dependencies

None. Can be implemented at any point.

## Status

**Complete** -- Implementation done, all acceptance criteria met.
