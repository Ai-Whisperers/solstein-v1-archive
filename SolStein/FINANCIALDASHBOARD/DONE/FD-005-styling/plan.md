# FD-005: Professional Styling

## Objective

Upgrade the visual styling from functional to board-presentation quality. This includes a refined color palette, proper number formatting, alternating row shading, trend indicators, and print-ready layout with confidentiality footer.

**In scope**: Color palette, number formatting, alternating rows, trend indicators, print layout, confidentiality footer -- all within `generate_excel_report.py`.

**Out of scope**: Data transformations, new sheets, new data columns, chart modifications, or changes to data-fetching logic.

## Requirements

1. **Color palette refresh**: Replace existing header, highlight, and classification fills with a professional dark-navy / gold / subtle-green / subtle-red scheme.
2. **Alternating row shading**: Apply light-gray banding to data rows that have no classification fill, improving readability.
3. **Number formatting**: Apply consistent decimal formats to revenue, percentage, and score columns; display missing data as `--`.
4. **Trend indicators**: Add visual growth indicators (arrows or icon sets) to growth columns without converting numeric cells to text.
5. **Print-ready layout**: Configure landscape orientation, repeating headers, narrow margins, confidentiality footer, and fit-to-width on every sheet.
6. **No data regressions**: All existing cell values and sheet content must remain unchanged; only formatting is modified.

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Touches every sheet-writing function in the file with coordinated styling changes across color constants, cell-styling helpers, number-formatting helpers, and print-layout configuration. Many small interrelated changes increase regression risk.

**Criteria Met**:
- Root Cause: N/A (feature work, not a bug fix)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~80-120 (new helpers + updates to every `write_*()` function)
- Risk Level: Medium (changes affect all sheets; visual regressions possible)
- Solution Pattern: Known (openpyxl styling/print APIs are well-documented)

**Decision Principle Applied**: Complex track chosen because the change touches many functions and carries medium regression risk despite a single file.

## Acceptance Criteria

### Color Palette
- [ ] Header band updated to dark navy `#1B2A4A`
- [ ] Eneve highlight updated to gold accent `#FFC000`
- [ ] Rocket fill changed to subtle green `#E2EFDA` (lighter, more professional)
- [ ] Dinosaur fill changed to subtle red `#FCE4EC`
- [ ] Alternating row shading: light gray `#F2F2F2` on even rows

### Number Formatting
- [ ] Revenue columns formatted as `#,##0.0` (one decimal for millions, e.g., "245.3")
- [ ] Percentage columns formatted as `0.0%` where applicable
- [ ] Score columns formatted as `0.0`
- [ ] Missing/null data displays as `--` instead of blank

### Conditional Formatting
- [ ] Trend arrows on growth columns: green up-arrow for positive, red down-arrow for negative
- [ ] Data bars on score columns (subtle visual weight indicator)

### Print Layout
- [ ] Page orientation: Landscape on all sheets
- [ ] Headers repeat on every printed page
- [ ] Footer: "Confidential - Board Material | Generated [DATE] | Page X of Y"
- [ ] Print area set to data range (no blank columns)
- [ ] Page margins: Narrow (0.5 inch)

### General
- [ ] All existing sheet content remains correct (no data changes)
- [ ] Script compiles clean

## Implementation Strategy

### 1. Update Color Constants

Replace the existing constants at the top of the file:

```python
# Professional color palette
HEADER_FILL = PatternFill(start_color="1B2A4A", end_color="1B2A4A", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
ENEVE_FILL = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
ROCKET_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
DINOSAUR_FILL = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")
ALT_ROW_FILL = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
```

### 2. Enhance `style_data_cell()` for Alternating Rows

```python
def style_data_cell(cell, is_eneve: bool = False, classification: Optional[str] = None, row_idx: int = 0) -> None:
    cell.font = BOLD_FONT if is_eneve else DATA_FONT
    cell.border = THIN_BORDER
    cell.alignment = Alignment(vertical="center", wrap_text=True)
    if is_eneve:
        cell.fill = ENEVE_FILL
    elif classification == "Rocket":
        cell.fill = ROCKET_FILL
    elif classification == "Dinosaur":
        cell.fill = DINOSAUR_FILL
    elif row_idx % 2 == 0:
        cell.fill = ALT_ROW_FILL
```

**Note**: This adds a `row_idx` parameter. All callers must be updated to pass `row_idx`.

### 3. Number Format Helper

```python
REVENUE_FORMAT = '#,##0.0'
PERCENT_FORMAT = '0.0"%"'
SCORE_FORMAT = '0.0'

def apply_number_format(cell, col_header: str) -> None:
    """Apply appropriate number format based on column header."""
    header_lower = col_header.lower()
    if "revenue" in header_lower and "eur" in header_lower:
        cell.number_format = REVENUE_FORMAT
    elif "%" in col_header or "cagr" in header_lower or "growth" in header_lower:
        cell.number_format = PERCENT_FORMAT
    elif "score" in header_lower or "composite" in header_lower:
        cell.number_format = SCORE_FORMAT
```

### 4. Missing Data Placeholder

When writing cell values, replace None with `"--"`:

```python
def format_value(val):
    """Return display value, using '--' for missing data."""
    if val is None:
        return "--"
    return val
```

### 5. Trend Arrow Helper

```python
def add_trend_indicator(cell, value) -> None:
    """Prefix cell value with trend arrow for growth metrics."""
    if value is None or not isinstance(value, (int, float)):
        return
    if value > 0:
        cell.value = f"\u2191 {value}"  # Up arrow
        cell.font = Font(name="Calibri", size=10, color="548235")
    elif value < 0:
        cell.value = f"\u2193 {value}"  # Down arrow
        cell.font = Font(name="Calibri", size=10, color="C00000")
```

### 6. Print Layout Function

```python
from openpyxl.worksheet.page import PrintPageSetup

def setup_print_layout(ws, num_cols: int) -> None:
    """Configure sheet for professional printing."""
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_margins.left = 0.5
    ws.page_margins.right = 0.5
    ws.page_margins.top = 0.75
    ws.page_margins.bottom = 0.75
    ws.oddFooter.center.text = "Confidential - Board Material"
    ws.oddFooter.right.text = "Page &P of &N"
    ws.print_title_rows = "1:1"  # Repeat header row
    last_col = get_column_letter(num_cols)
    ws.print_area = f"A1:{last_col}{ws.max_row}"
```

Call `setup_print_layout(ws, len(headers))` at the end of each `write_*()` function.

### 7. Update All Sheet Functions

Each `write_*()` function needs:
- Pass `row_idx` to `style_data_cell()`
- Call `apply_number_format()` after setting cell values
- Call `setup_print_layout()` at the end
- Use `format_value()` for cell values

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook and visually verify:
   - Navy headers, gold Eneve rows, subtle green/red for Rocket/Dinosaur
   - Alternating gray rows where no classification fill
   - Revenue numbers show one decimal
   - Missing data shows "--"
3. Print preview to verify landscape layout and footer
4. Verify no data values changed (only formatting)

## Risks

- **`style_data_cell()` signature change**: Adding `row_idx` parameter breaks all existing callers. Use `row_idx: int = 0` default to maintain backward compatibility until all callers are updated.
- **Trend arrows in cells**: Prefixing with Unicode arrow converts numeric cells to text, which breaks conditional formatting and sorting. Consider using a separate "Trend" column instead of modifying the value.
- **Print margins**: Different printers may clip content. Use `fitToWidth=1` to auto-scale.

## Dependencies

None (can be done independently of FD-003/FD-004). Apply styling to all sheets that exist at time of execution.

## Status

**Current**: Completed
