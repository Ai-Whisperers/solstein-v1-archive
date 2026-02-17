# FD-019: Scenario Projections Sheet

## Objective

Add a "Projections" sheet showing where competitors will be in 2-3 years at current growth rates. Extrapolation makes the abstract concrete: "By 2028, Dexter at 200+ employees, Kraken at $1B ARR."

## Requirements

1. Project forward 1, 2, and 3 years for each competitor using current CAGR:
   - Revenue projection (current * (1 + CAGR)^years)
   - Employee projection (current * (1 + employee CAGR)^years)
2. Include columns: Company, Current Revenue, 2027 Projected, 2028 Projected, 2029 Projected, Current Employees, 2027 Emp, 2028 Emp, 2029 Emp
3. Conditional formatting: cells that cross key thresholds highlighted (e.g., revenue > EUR 100M, employees > 500)
4. Chart: line chart showing revenue trajectory convergence/divergence for top 10 competitors + Eneve
5. Disclaimer row: "Projections based on historical CAGR, not forecasts"

## Data Sources

- Existing revenue and employee CAGR data from prior sheets (FD-002 through FD-011)
- Current headcount and revenue figures from competitor profile sheets

## Implementation Strategy

1. Create a new "Projections" sheet in the financial dashboard workbook
2. Set up column headers: Company, Current Revenue, 2027/2028/2029 Revenue, Current Employees, 2027/2028/2029 Employees
3. Pull current revenue and employee figures from existing competitor data
4. Implement CAGR projection formulas: `current * (1 + CAGR)^years` for each year horizon
5. Add graceful handling for missing CAGR: display "N/A" instead of formula errors
6. Apply conditional formatting rules for key thresholds (revenue > EUR 100M, employees > 500)
7. Create line chart showing revenue trajectory for top 10 competitors + Eneve over the 3-year horizon
8. Add disclaimer row at bottom: "Projections based on historical CAGR, not forecasts"
9. Validate all projections against source data for correctness

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: This is a straightforward mathematical extrapolation using existing CAGR data. The formulas are well-defined, the data sources already exist in earlier sheets, and the task is isolated to a single new sheet with no impact on existing content.

**Criteria Met**:
- Root Cause: Single (add one new projections sheet)
- Files Affected: 1 (financial dashboard workbook)
- Lines Changed: ~50-80 cells/formulas (within Simple Fix scope for spreadsheet work)
- Risk Level: Low (new sheet, no modification of existing data)
- Solution Pattern: Known (CAGR compound growth formula, Excel charting, conditional formatting)

**Effort**: ~2h

## Acceptance Criteria

- [ ] Projections sheet present
- [ ] 3-year projections for revenue and employees
- [ ] Line chart showing trajectory convergence
- [ ] Threshold highlighting applied
- [ ] Disclaimer present
- [ ] Handle missing CAGR gracefully (show "N/A" not errors)

## Status

Done
