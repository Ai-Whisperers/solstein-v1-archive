# FD-034: Context

**Last Updated**: 2026-02-17

## Technical Background

FD-020 (Portfolio Risk Dashboard) aggregates threat dimensions across all competitors into a single risk matrix with KPI tiles and bubble chart. The script `write_portfolio_risk_sheet()` currently derives risk data algorithmically from competitor classification and proximity data. There's no dedicated prompt that produces a structured risk register with explicit probability/severity scoring.

## Current Focus

Define risk assessment framework compatible with FD-020's existing data consumption patterns.

## Key Components

- `.cursor/templars/analysis/market/multi-source-synthesis-dashboard-templar.md` -- Pattern to follow
- `.cursor/scripts/analysis/market/generate_excel_report.py` -- `write_portfolio_risk_sheet()` function
- `tickets/COMPETITION/market-trends.md` -- Regulatory/market risk source
- `tickets/COMPETITION/competitive-overlap.md` -- Competitive proximity risk source

## Outstanding Issues

- Need to define risk categories that map cleanly to FD-020 visualization
- Risk scoring rubric must be reproducible across updates

## Next Steps

1. Read FD-020 plan.md and `write_portfolio_risk_sheet()` for exact data needs
2. Draft risk assessment framework
3. Create prompt file
