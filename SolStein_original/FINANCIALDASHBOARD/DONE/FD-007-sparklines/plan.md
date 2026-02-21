# FD-007: Sparklines -- Mini Revenue & Employee Trends

## Objective

Add sparkline columns to the Summary and Raw Data sheets showing revenue and employee trends over time (5-6 years of data per competitor). These mini line charts in cells give the board an instant visual sense of trajectory without needing to look at separate charts.

## Requirements

1. Add a "Revenue Trend" sparkline column to both Summary and Raw Data sheets showing revenue over time per competitor
2. Add an "Employee Trend" sparkline column to both Summary and Raw Data sheets showing headcount over time per competitor
3. Sparkline data sourced from existing `revenue.timeline` and `employees.timeline` arrays (5-6 data points per competitor)
4. Timeline data stored in hidden helper columns so sparklines reference real cell ranges
5. Competitors with no timeline data must produce an empty cell (no errors or crashes)
6. Prefer native Excel sparklines (openpyxl); fall back to Unicode text sparklines if rendering fails

## Acceptance Criteria

- [ ] Summary sheet has a "Revenue Trend" sparkline column after "Latest Headcount"
- [ ] Summary sheet has an "Employee Trend" sparkline column after Revenue Trend
- [ ] Raw Data sheet has the same two sparkline columns
- [ ] Sparklines show 5-6 data points per competitor (one per year)
- [ ] Data for sparklines is stored in hidden helper columns
- [ ] Sparklines render as mini line charts in Excel
- [ ] Gracefully handles competitors with no timeline data (empty cell, no error)
- [ ] Script compiles clean

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Although only one file is modified, the openpyxl sparkline API has limited documentation and uncertain rendering compatibility across Excel versions, requiring a two-option strategy with fallback. Estimated code changes exceed 10 lines and the solution pattern is partially known.

**Criteria Met**:
- Root Cause: Single (add sparkline columns to existing sheets)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~40-60 (helper column writes, sparkline group creation, header extensions, two options)
- Risk Level: Medium (openpyxl sparkline rendering varies by Excel version)
- Solution Pattern: Partially known (openpyxl sparkline API not well-documented)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Implementation Strategy

### Option A: openpyxl Sparklines (Preferred)

openpyxl 3.1+ supports sparklines via `openpyxl.worksheet.sparkline`:

```python
from openpyxl.worksheet.sparkline import SparklineGroup, Sparkline

# Write timeline data to hidden helper columns (far right)
helper_start_col = len(headers) + 2
for row_idx, comp in enumerate(competitors, 2):
    timeline = comp.get("revenue", {}).get("timeline", [])
    for i, entry in enumerate(timeline):
        ws.cell(row=row_idx, column=helper_start_col + i, value=entry.get("eur_millions"))

# Create sparkline group
sparkline_col = get_column_letter(len(headers) + 1)
helper_start = get_column_letter(helper_start_col)
helper_end = get_column_letter(helper_start_col + max_years - 1)

sparklines = []
for row_idx in range(2, len(competitors) + 2):
    data_range = f"{helper_start}{row_idx}:{helper_end}{row_idx}"
    location = f"{sparkline_col}{row_idx}"
    sparklines.append(Sparkline(sqref=location, formula=data_range))

sg = SparklineGroup(sparklines=sparklines, type="line")
ws.sparkline_groups.append(sg)

# Hide helper columns
for col in range(helper_start_col, helper_start_col + max_years):
    ws.column_dimensions[get_column_letter(col)].hidden = True
```

### Option B: Unicode Fallback (If openpyxl sparklines don't render well)

Use Unicode block characters to create text-based mini-charts:

```python
SPARK_CHARS = " _.-~^"  # 6 levels

def text_sparkline(values: list[Optional[float]]) -> str:
    """Create a text-based mini sparkline from values."""
    clean = [v for v in values if v is not None]
    if len(clean) < 2:
        return ""
    vmin, vmax = min(clean), max(clean)
    if vmax == vmin:
        return "=" * len(clean)
    chars = []
    for v in values:
        if v is None:
            chars.append(" ")
        else:
            idx = int((v - vmin) / (vmax - vmin) * (len(SPARK_CHARS) - 1))
            chars.append(SPARK_CHARS[idx])
    return "".join(chars)
```

### Recommendation

Try Option A first. If openpyxl sparklines don't render in Excel (some versions have issues), fall back to Option B.

### Changes to Sheet Functions

Add sparkline columns to `write_summary_sheet()` and `write_raw_data()`:

1. Extend `headers` list with "Revenue Trend" and "Employee Trend"
2. Write timeline data to hidden helper columns
3. Create sparkline groups referencing those columns
4. Or write text sparklines directly to cells (Option B)

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook and open in Excel:
   - Verify sparkline columns appear
   - Verify sparklines show trend data (not blank)
   - Verify hidden helper columns don't show (but are accessible)
3. If sparklines don't render, implement Option B and re-test

## Risks

- **openpyxl sparkline compatibility**: Sparklines may not render in all Excel versions or LibreOffice. Option B (Unicode) is a universal fallback.
- **Performance**: Writing 25+ competitors x 6 years of helper data adds ~150 cells. Negligible impact.
- **Max timeline length varies**: Some competitors have 5 years, others 6. Pad shorter timelines with None/empty.

## Dependencies

None (uses existing `revenue.timeline` and `employees.timeline` data already extracted).

## Status

**Current**: Implemented
