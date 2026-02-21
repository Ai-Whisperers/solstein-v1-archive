# FINANCIALDASHBOARD: Context

## Status: ACTIVE -- Phase 2 (Advanced Quality Level)

## Current State

The Excel report generator (`generate_excel_report.py`) produces a functional 7-sheet workbook with basic formatting. It was recently upgraded to Standard quality level (shebang, error handling, exit codes, shared utilities, hyperlinks). The extraction pipeline (`extract_competitor_data.py`) pulls data from 25+ competitor `financial-growth.md` files in `tickets/COMPETITION/`.

## Key Files

- `.cursor/scripts/analysis/market/generate_excel_report.py` -- Main report generator (548 lines)
- `.cursor/scripts/analysis/market/extract_competitor_data.py` -- Data extraction
- `.cursor/scripts/analysis/market/competitor_utils.py` -- Shared utilities
- `.cursor/scripts/analysis/market/generate_markdown_dashboard.py` -- Markdown version
- `.cursor/scripts/analysis/market/requirements.txt` -- Dependencies (openpyxl>=3.1.0)
- `tickets/COMPETITION/*/financial-growth.md` -- Source data (25+ competitors)

## Technical Context

- **Python 3.10+**, **openpyxl >= 3.1.0**
- All scripts follow Standard quality level (logging, argparse, type hints, sys.exit)
- Competitor data includes: revenue timeline, employee timeline, funding rounds, profitability metrics, scorecard dimensions, classification
- Un-extracted data available: EBITDA margin, revenue/employee, lead investors, geographic expansion, SaaS deployment model, cloud revenue %

## Immediate Focus

Phase 1 (FD-001 to FD-008) is complete. Phase 2 targets Advanced quality level:
- **FD-009**: Unit tests (pytest, 50%+ coverage) -- execute first
- **FD-010**: Progress reporting + smart caching -- execute second
- **FD-011**: Performance measurement & optimization -- execute last
