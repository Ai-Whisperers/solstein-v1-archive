# FD-006: Context

## Status: PENDING

## Current State

No Eneve-specific positioning sheet exists. Eneve data is present in the competitor list and identified by `is_eneve()` from `competitor_utils.py`. The Summary sheet highlights Eneve rows with yellow fill, but there's no head-to-head comparison.

## Key Code Locations

- `competitor_utils.py`: `is_eneve()` function identifies Eneve entries
- `generate_excel_report.py`: Pattern functions to follow
- Python `statistics` module for median computation (stdlib, no new dependency)

## Immediate Next Steps

1. Add `write_eneve_positioning()` function
2. Add `compute_market_stats()` helper
3. Wire into `generate_workbook()`
