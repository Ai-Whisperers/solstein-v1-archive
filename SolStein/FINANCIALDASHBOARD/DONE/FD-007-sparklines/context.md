# FD-007: Context

## Status: IMPLEMENTED

## Current State

Revenue and employee timelines are already extracted by `extract_competitor_data.py` into the JSON output. The `revenue.timeline` array has entries with `year` and `eur_millions`. The `employees.timeline` array has entries with `year` and `headcount`. This data is currently unused in the Excel output.

## Key Code Locations

- `generate_excel_report.py` line 118: `write_summary_sheet()` -- add sparkline columns
- `generate_excel_report.py` line 399: `write_raw_data()` -- add sparkline columns
- openpyxl: `openpyxl.worksheet.sparkline` module for native sparklines
- openpyxl: `ws.column_dimensions[col].hidden = True` to hide helper columns

## Data Structure

```json
"revenue": {
    "timeline": [
        {"year": "2019", "eur_millions": 120.0, "yoy_growth_pct": null, "confidence": "Medium"},
        {"year": "2020", "eur_millions": 135.0, "yoy_growth_pct": 12.5, "confidence": "Medium"},
        ...
    ]
}
```

## Immediate Next Steps

1. Determine max timeline length across all competitors
2. Add helper columns for timeline data
3. Create sparkline groups (or text sparklines as fallback)
4. Hide helper columns
