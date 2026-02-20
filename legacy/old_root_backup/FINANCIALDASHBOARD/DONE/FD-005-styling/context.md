# FD-005: Context

## Status: PENDING

## Current State

Current color palette uses `#2F5496` (header), `#FFF2CC` (Eneve), `#C6EFCE` (Rocket), `#FFC7CE` (Dinosaur). No alternating row shading. No number formatting beyond default. No print layout configured.

## Key Code Locations

- `generate_excel_report.py` lines 47-59: Color/style constants to update
- `generate_excel_report.py` line 72: `style_data_cell()` function to enhance
- Every `write_*()` function: Add `row_idx` parameter passing and print layout call
- openpyxl `ws.page_setup`, `ws.page_margins`, `ws.oddFooter` for print layout

## Design Decision: Trend Arrows

Prefixing cell values with Unicode arrows (e.g., "^ 15.3") converts numbers to text. This breaks sorting and conditional formatting. **Recommendation**: Use a separate narrow "Trend" column with just the arrow, or use conditional formatting icon sets instead of modifying cell values.

## Immediate Next Steps

1. Update color constants
2. Add `ALT_ROW_FILL` constant
3. Enhance `style_data_cell()` with row_idx parameter
4. Add `apply_number_format()`, `format_value()`, `setup_print_layout()` helpers
5. Update all `write_*()` functions to use new helpers
