# FD-001: Executive Summary Sheet

## Objective

Add a new "Executive Summary" sheet as the **first sheet** in the workbook (the one that opens when the file is opened). This is what the CTO/Board sees first. It should look like a presentation slide, not a spreadsheet.

## Requirements

1. Add a new `write_executive_summary()` function to `generate_excel_report.py` that renders a presentation-quality KPI overview sheet
2. Display headline KPI tiles: total competitors, rockets count, market vs Eneve CAGR, composite score comparison, Eneve classification
3. Include a "Top 5 Competitive Threats" table ranked by composite score (excluding Eneve)
4. Show dynamic insight callouts computed from the competitor dataset (faster growers, funding totals, rocket count)
5. Sheet must be positioned as the first (leftmost) tab in the workbook
6. Layout must fit on a single screen without scrolling, using merged cells and large fonts for readability
7. All data sourced from the existing `competitors` list -- no changes to data extraction pipeline

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Although the change is confined to a single file and carries low risk, the implementation adds a substantial new function (~100+ lines) with merged-cell layout, multiple styling constants, computed KPIs, a ranked table, and dynamic text generation. This exceeds the Simple Fix threshold for lines of code and involves a non-trivial formatting pattern (openpyxl merged cells).

**Criteria Met**:
- Root Cause: N/A (feature addition, not a defect)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~100-150 (new function + constants + wiring)
- Risk Level: Low (additive change, no modification of existing sheets)
- Solution Pattern: Familiar (follows existing `write_*_sheet()` pattern in codebase)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Status

**Current**: Ready for Implementation

## Acceptance Criteria

- [ ] "Executive Summary" is the first sheet (leftmost tab) when the workbook opens
- [ ] Headline KPI tiles displayed with large fonts (16-20pt):
  - Total competitors tracked
  - Rockets identified (green highlight)
  - Average market CAGR vs Eneve CAGR (side-by-side)
  - Eneve's composite score vs market average
  - Eneve's classification with color badge
- [ ] "Competitive Threat Radar" table showing top 5 threats (highest composite, excluding Eneve)
  - Columns: Rank, Company, Classification, Composite Score, Revenue CAGR, Latest Revenue
- [ ] Key insight callouts (merged cells, bold):
  - "X competitors grew revenue faster than Eneve"
  - "Y competitors have raised EUR Z in funding"
  - "N competitors are classified as Rockets"
- [ ] Sheet uses merged cells, large fonts, dark blue header band
- [ ] No scroll needed to see all KPIs (fits in one screen)
- [ ] Script compiles clean and `--help` works

## Implementation Strategy

### 1. New function `write_executive_summary()`

Add to `generate_excel_report.py` after the helper functions, before `write_summary_sheet()`.

```python
def write_executive_summary(wb: Workbook, competitors: list[dict], link_base: Optional[Path] = None) -> None:
```

### 2. KPI Computation

All data comes from the existing `competitors` list -- no extraction changes needed.

```python
eneve = next((c for c in competitors if is_eneve(c)), None)
non_eneve = [c for c in competitors if not is_eneve(c)]

total_count = len(competitors)
rockets = [c for c in competitors if get_classification(c) == "Rocket"]
rocket_count = len(rockets)

market_cagrs = [c.get("revenue", {}).get("cagr_3yr_pct") for c in non_eneve if c.get("revenue", {}).get("cagr_3yr_pct") is not None]
avg_market_cagr = sum(market_cagrs) / len(market_cagrs) if market_cagrs else None
eneve_cagr = eneve.get("revenue", {}).get("cagr_3yr_pct") if eneve else None

composites = [get_composite(c) for c in non_eneve if get_composite(c) is not None]
avg_composite = sum(composites) / len(composites) if composites else None
eneve_composite = get_composite(eneve) if eneve else None
eneve_classification = get_classification(eneve) if eneve else None

faster_than_eneve = len([c for c in non_eneve if (c.get("revenue", {}).get("cagr_3yr_pct") or 0) > (eneve_cagr or 0)])
```

### 3. Layout Structure

```
Row 1-2:   Title bar "COMPETITIVE INTELLIGENCE DASHBOARD" (merged A1:L2, dark navy, 20pt white)
Row 3:     Blank spacer
Row 4-6:   KPI tiles in columns A-B, C-D, E-F, G-H, I-J (merged pairs)
           Each tile: Label (row 4, 10pt gray), Value (row 5, 20pt bold), Subtitle (row 6, 9pt)
Row 7:     Blank spacer
Row 8:     Section header "TOP 5 COMPETITIVE THREATS" (merged, 14pt, dark navy)
Row 9:     Table headers (Rank, Company, Classification, Composite, Revenue CAGR, Latest Revenue)
Row 10-14: Top 5 threats data rows
Row 15:    Blank spacer
Row 16-18: Insight callouts (merged cells, each spanning full width)
```

### 4. KPI Tile Styling

```python
TITLE_FONT = Font(name="Calibri", size=20, bold=True, color="FFFFFF")
KPI_LABEL_FONT = Font(name="Calibri", size=10, color="808080")
KPI_VALUE_FONT = Font(name="Calibri", size=24, bold=True, color="1B2A4A")
KPI_SUBTITLE_FONT = Font(name="Calibri", size=9, color="A0A0A0")
INSIGHT_FONT = Font(name="Calibri", size=12, bold=True, color="1B2A4A")
```

### 5. Make it the First Sheet

After creating all sheets, move the Executive Summary to position 0:

```python
wb.move_sheet("Executive Summary", offset=-wb.sheetnames.index("Executive Summary"))
```

### 6. Wire into `generate_workbook()`

Add the call alongside the other `write_*()` calls:

```python
log.info("Writing Executive Summary...")
write_executive_summary(wb, competitors, link_base)
```

## Testing Strategy

1. `python -m py_compile generate_excel_report.py` -- syntax check
2. `python generate_excel_report.py --help` -- CLI validation
3. Generate workbook with test data and verify:
   - Executive Summary is the first tab
   - KPI values are correct (spot-check against raw data)
   - Top 5 threats table shows correct competitors
   - Insight callouts reflect actual data
   - Layout fits on screen without scrolling

## Risks

- **Merged cell complexity**: openpyxl merged cells can be finicky with formatting. Apply styles to the top-left cell of the merge range.
- **Eneve not found**: Handle gracefully if no competitor has "eneve" in folder name -- show "N/A" for Eneve-specific KPIs.

## Dependencies

None. Uses only existing extracted data from the `competitors` list.
