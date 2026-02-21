# FD-002: Charts for All Sheets

## Objective

Add native Excel charts to 5 additional sheets (currently only Revenue Leaderboard has a chart). Boards prefer charts over tables -- every data sheet should have a visual summary.

**In Scope**: Bar charts for Employee Growth, Funding, Summary, SaaS Maturity sheets; doughnut chart for Classification Matrix; professional titles and axis labels.

**Out of Scope**: Interactive/dynamic charts, custom color themes, chart animations, sparklines (separate ticket FD-007), changes to the existing Revenue CAGR chart.

## Requirements

1. Each of the 5 data sheets without a chart must receive a native openpyxl chart summarizing its key metric
2. Chart types must match the data shape: bar charts for ranked scores/percentages, doughnut chart for categorical distribution
3. All charts must have descriptive titles, axis labels, and professional sizing consistent with the existing Revenue CAGR chart
4. The Classification Matrix doughnut chart must aggregate row data into category counts using helper cells
5. Chart placement must not overlap existing data columns on any sheet

## Status

Ready for implementation.

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: Repeating an established chart pattern (Revenue CAGR) across 5 additional sheets. The DoughnutChart introduces minor novelty but uses the same openpyxl API surface.

**Criteria Met**:
- Root Cause: Single, clear goal (add missing charts)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~80-100 (5 chart blocks averaging 15-20 lines each)
- Risk Level: Low (additive changes, no modification of existing logic)
- Solution Pattern: Known (replicating existing Revenue chart pattern)

**Effort**: 1-2 hours

## Acceptance Criteria

- [ ] Employee Growth sheet has a bar chart showing Employee CAGR by company
- [ ] Funding Leaderboard sheet has a horizontal bar chart showing Funding Score by company
- [ ] Classification Matrix sheet has a doughnut/pie chart showing classification distribution (count of Rockets, Risers, Steady, Dinosaurs)
- [ ] Summary sheet has a bar chart showing Composite Score by company (sorted)
- [ ] SaaS Maturity sheet has a bar chart showing SaaS Score by company
- [ ] All charts have proper titles, axis labels, and professional sizing
- [ ] Existing Revenue CAGR chart remains unchanged
- [ ] Script compiles clean

## Implementation Strategy

### Pattern to Follow

The Revenue Leaderboard already has a chart (lines 193-209 in current file). Replicate this pattern:

```python
if len(sorted_comps) >= 2:
    chart = BarChart()
    chart.type = "col"
    chart.title = "Chart Title"
    chart.y_axis.title = "Y Axis"
    chart.x_axis.title = "Company"
    chart.style = 10

    data_ref = Reference(ws, min_col=DATA_COL, min_row=1, max_row=len(sorted_comps) + 1)
    cats_ref = Reference(ws, min_col=COMPANY_COL, min_row=2, max_row=len(sorted_comps) + 1)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.shape = 4
    chart.width = 25
    chart.height = 14

    ws.add_chart(chart, "H2")  # Placement cell
```

### Chart Specifications

#### 1. Employee Growth Bar Chart
- **Sheet**: Employee Growth
- **Data column**: 5 (Employee CAGR %)
- **Company column**: 2
- **Title**: "Employee CAGR (%) - All Competitors"
- **Y-axis**: "CAGR %"
- **Placement**: `H2`

#### 2. Funding Bar Chart
- **Sheet**: Funding Leaderboard
- **Data column**: 4 (Funding Score)
- **Company column**: 2
- **Title**: "Funding Momentum Score - All Competitors"
- **Y-axis**: "Score (1-10)"
- **Placement**: `I2`

#### 3. Classification Doughnut Chart
- **Sheet**: Classification Matrix
- **Type**: `DoughnutChart` (from `openpyxl.chart import DoughnutChart`)
- **Data**: Count per classification (compute from data, write to helper cells)
- **Title**: "Competitor Classification Distribution"
- **Placement**: `L2`
- **Implementation note**: Requires computing counts and writing them to hidden helper cells (e.g., columns M-N) since DoughnutChart needs cell references

#### 4. Composite Score Bar Chart
- **Sheet**: Summary
- **Data column**: 10 (Composite Score, column J)
- **Company column**: 1
- **Title**: "Composite Growth Score - All Competitors"
- **Y-axis**: "Score (1-10)"
- **Placement**: `N2` (after the last data column)

#### 5. SaaS Maturity Bar Chart
- **Sheet**: SaaS Maturity
- **Data column**: 4 (SaaS Score)
- **Company column**: 2
- **Title**: "SaaS Maturity Score - All Competitors"
- **Y-axis**: "Score (1-10)"
- **Placement**: `H2`

### Import Addition

Add `DoughnutChart` to the openpyxl chart import:

```python
from openpyxl.chart import BarChart, DoughnutChart, Reference
```

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook and verify all 6 charts render (1 existing + 5 new)
3. Verify chart data matches the table data on each sheet

## Risks

- **DoughnutChart complexity**: Requires helper cells for aggregated counts. Place these in columns far to the right to avoid interfering with data.
- **Chart placement**: Charts may overlap with data if sheets have many columns. Adjust `H2` offset as needed.

## Dependencies

None. Uses only existing data columns.
