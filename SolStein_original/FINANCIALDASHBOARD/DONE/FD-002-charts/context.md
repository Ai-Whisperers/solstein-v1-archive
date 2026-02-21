# FD-002: Context

## Status: PENDING

## Current State

Only `write_revenue_leaderboard()` has a chart (BarChart, lines ~193-209). All other 6 sheets are table-only. The chart pattern is well-established and straightforward to replicate.

## Key Code Locations

- `generate_excel_report.py` lines 193-209: Existing Revenue CAGR chart (pattern to follow)
- openpyxl imports at line 32-36: Need to add `DoughnutChart`
- Each `write_*()` function ends with `auto_fit_columns()` and `add_autofilter()` -- add chart code before these or after

## Immediate Next Steps

1. Add `DoughnutChart` to imports
2. Add bar charts to Employee Growth, Funding, Summary, SaaS sheets (copy Revenue pattern)
3. Add doughnut chart to Classification Matrix (needs helper cells for counts)
