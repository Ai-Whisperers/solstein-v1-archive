# FD-008: Context

## Status: PENDING

## Current State

No methodology or data quality sheet exists in the workbook. The metadata is available in the extracted JSON under `data["metadata"]` with fields: `total_folders`, `with_financial_data`, `without_financial_data`, `source_directory`.

## Key Code Locations

- `generate_excel_report.py` line 459: `generate_workbook()` -- add call (pass `data` dict, not just `competitors`)
- Methodology content is static text, no complex logic needed

## Design Note

This is the only sheet function that takes `data` (full dict) instead of just `competitors` list, because it needs `metadata` for the Data Freshness section.

## Immediate Next Steps

1. Add `write_methodology_sheet()` function
2. Wire into `generate_workbook()` as the last sheet
