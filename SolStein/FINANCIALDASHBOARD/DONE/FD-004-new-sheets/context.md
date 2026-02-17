# FD-004: Context

## Status: IMPLEMENTED (data pending FD-003)

## Current State

Both new sheet functions are implemented and wired into the workbook generation pipeline. They produce fully-styled sheets with headers, auto-filter, frozen panes, company hyperlinks, classification color coding, Eneve highlight rows, and bar charts. Metric columns will populate once FD-003 extracts the underlying data.

## Key Code Locations

- `generate_excel_report.py` line 687: `write_efficiency_sheet()` -- Efficiency & Profitability sheet
- `generate_excel_report.py` line 748: `write_market_reach_sheet()` -- Market Reach sheet
- `generate_excel_report.py` line 907-911: wiring in `generate_workbook()`

## Remaining Dependency

FD-003 must populate these data dict fields before sheets show meaningful metrics:
- `profitability.revenue_per_employee_eur_k`
- `profitability.ebitda_margin_pct`
- `geographic.international_revenue_pct`
- `geographic.countries_count`
- `saas.deployment_model`
- `saas.cloud_revenue_pct`
