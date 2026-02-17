# FD-001: Context

## Status: PENDING

## Current State

`generate_excel_report.py` has 7 sheet-writing functions. The first sheet created is "Summary" (uses `wb.active`). There is no executive summary or KPI overview.

## Key Code Locations

- `generate_excel_report.py` line 459: `generate_workbook()` orchestrates all sheet writes
- `generate_excel_report.py` line 118: `write_summary_sheet()` is the current first sheet
- `competitor_utils.py`: `is_eneve()`, `get_composite()`, `get_classification()`, `get_score()`
- Style constants defined at lines 47-59 (HEADER_FILL, HEADER_FONT, etc.)

## Dependencies

- `is_eneve()` from `competitor_utils.py` identifies Eneve entries
- `get_composite()`, `get_classification()` for scorecard data
- openpyxl `Workbook.move_sheet()` to reorder tabs

## Immediate Next Steps

1. Add `write_executive_summary()` function
2. Add new font/style constants for KPI tiles
3. Wire into `generate_workbook()`
4. Move sheet to position 0
