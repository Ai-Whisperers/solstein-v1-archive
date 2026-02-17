# FD-006: Eneve vs Market Comparison Sheet

## Objective

Add a dedicated "Eneve vs Market" sheet that answers the board's core question: **"Where do we stand?"** Side-by-side comparison of Eneve metrics against market average, median, and best-in-class. Green where Eneve leads, red where Eneve trails.

## Requirements

1. New "Eneve vs Market" worksheet added to the Excel workbook
2. Compare Eneve against competitors on 7 key metrics: Revenue CAGR (3yr), Employee CAGR, Composite Score, SaaS Maturity Score, Recurring Revenue %, Latest Revenue (EUR M), Latest Headcount
3. Market statistics computed per metric: average, median, best-in-class value and company name
4. Visual indicator (green/red fill) showing whether Eneve leads or trails the market average per metric
5. Grouped bar chart visualizing Eneve vs Market Average side-by-side
6. Graceful handling when Eneve data is absent from the dataset (display "N/A")

## Acceptance Criteria

- [ ] "Eneve vs Market" sheet present in workbook
- [ ] Metrics compared (one row per metric):
  - Revenue CAGR (3yr)
  - Employee CAGR
  - Composite Score
  - SaaS Maturity Score
  - Recurring Revenue %
  - Latest Revenue (EUR M)
  - Latest Headcount
- [ ] Columns: Metric, Eneve, Market Average, Market Median, Best-in-Class, Best Company Name
- [ ] Conditional formatting: Green fill on Eneve cell where it leads market average, Red fill where it trails
- [ ] Grouped bar chart showing Eneve vs Market Average for each metric
- [ ] Handles case where Eneve data is not found (shows "N/A")
- [ ] Script compiles clean

## Implementation Approach

### 1. `write_eneve_positioning()` Function

```python
def write_eneve_positioning(wb: Workbook, competitors: list[dict], link_base: Optional[Path] = None) -> None:
    """Eneve vs Market comparison sheet."""
    ws = wb.create_sheet("Eneve vs Market")
    
    eneve = next((c for c in competitors if is_eneve(c)), None)
    non_eneve = [c for c in competitors if not is_eneve(c)]
```

### 2. Metric Computation

For each metric, compute:

```python
import statistics

def compute_market_stats(values: list[float]) -> dict:
    """Compute average, median, max from a list of values."""
    clean = [v for v in values if v is not None]
    if not clean:
        return {"avg": None, "median": None, "best": None, "best_idx": None}
    return {
        "avg": statistics.mean(clean),
        "median": statistics.median(clean),
        "best": max(clean),
        "best_idx": clean.index(max(clean)),
    }
```

Define metrics to compare:

```python
metrics = [
    ("Revenue CAGR 3yr (%)", lambda c: c.get("revenue", {}).get("cagr_3yr_pct")),
    ("Employee CAGR (%)", lambda c: c.get("employees", {}).get("employee_cagr_pct")),
    ("Composite Score", lambda c: get_composite(c)),
    ("SaaS Maturity Score", lambda c: get_score(c, "SaaS Maturity")),
    ("Recurring Revenue (%)", lambda c: c.get("profitability", {}).get("recurring_revenue_pct")),
    ("Latest Revenue (EUR M)", lambda c: c.get("revenue", {}).get("latest_revenue_eur_m")),
    ("Latest Headcount", lambda c: c.get("employees", {}).get("latest_headcount")),
]
```

### 3. Layout

```
Row 1: Headers -- Metric | Eneve | Market Avg | Market Median | Best-in-Class | Best Company
Row 2-8: One row per metric
Row 10+: Grouped bar chart (Eneve vs Market Average)
```

### 4. Conditional Formatting

For each Eneve cell (column B), compare against Market Average (column C):

```python
# Green if Eneve >= Market Average
GREEN_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
RED_FILL = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")

if eneve_val is not None and avg_val is not None:
    if eneve_val >= avg_val:
        eneve_cell.fill = GREEN_FILL
    else:
        eneve_cell.fill = RED_FILL
```

### 5. Grouped Bar Chart

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.type = "col"
chart.grouping = "clustered"
chart.title = "Eneve vs Market Average"
# Data: columns B and C (Eneve and Market Avg)
# Categories: column A (Metric names)
```

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook and verify:
   - Eneve vs Market sheet exists
   - Values match manual calculation from raw data
   - Green/red formatting correctly indicates lead/trail
   - Chart renders with grouped bars
3. Test edge case: what happens if Eneve entry is missing from data

## Risks

- **Eneve not in dataset**: Handle with `if eneve is None: show all N/A` gracefully.
- **Metrics with different scales**: The bar chart may look odd with Revenue (hundreds) next to Scores (1-10). Consider normalizing or using separate charts per metric group.

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: New standalone sheet function following established patterns in the codebase. No modification of existing code required beyond wiring the new function into `generate_workbook()`.

**Criteria Met**:
- Root Cause: Single feature addition (new sheet)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~80-120 (new function + wiring)
- Risk Level: Low (additive change, no existing code modified)
- Solution Pattern: Known (follows existing `write_*()` sheet pattern)

**Note**: Lines exceed the 10-line threshold for "Simple Fix", but the low risk, single-file scope, and familiar pattern keep this straightforward. Effort estimate: 1-2 hours.

## Dependencies

None (uses existing extracted data). If run after FD-003, could also include EBITDA margin and Revenue per Employee in the comparison.

## Status

**Current**: Ready for Implementation
