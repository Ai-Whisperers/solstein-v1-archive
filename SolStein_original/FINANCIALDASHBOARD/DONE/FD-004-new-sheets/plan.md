# FD-004: New Sheets -- Efficiency & Profitability, Market Reach

## Objective

Add two new data sheets to the workbook that leverage the additional data extracted in FD-003. These sheets address metrics that boards care deeply about: unit economics (revenue per employee, EBITDA margin) and geographic footprint.

## Requirements

1. Create an "Efficiency & Profitability" sheet displaying unit-economics metrics (Revenue per Employee, EBITDA Margin, Recurring Revenue %, SaaS Score) sorted by Revenue per Employee descending
2. Create a "Market Reach" sheet displaying geographic-expansion metrics (International Revenue %, Countries Active, Deployment Model, Cloud Revenue %, Geographic Score) sorted by International Revenue % descending
3. Both sheets must include a bar chart visualizing the primary metric (Revenue per Employee and International Revenue % respectively)
4. Both sheets must follow the existing styling conventions: header fill, borders, Eneve highlight row, classification color coding
5. Both sheets must include auto-filter, frozen header rows, and company hyperlinks consistent with existing sheets
6. Functions must handle missing/null data gracefully (empty cells, no errors) since many competitors lack EBITDA or geographic data
7. New sheet functions must be wired into `generate_workbook()` between Classification Matrix and Raw Data sheets

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: Both new sheets follow the exact same pattern as 7 existing `write_*` functions. No architectural changes, no new libraries, no cross-cutting concerns. The work is additive and isolated.

**Criteria Met**:
- Root Cause: N/A (feature addition, not defect)
- Files Affected: 1 (`generate_excel_report.py`)
- Lines Changed: ~120 (two new functions + wiring)
- Risk Level: Low (follows established pattern, no existing functionality changed)
- Solution Pattern: Well-understood (copy-and-adapt from existing sheet functions)

## Prerequisites

- **FD-003 must be completed first** -- this ticket uses the new extracted fields (`ebitda_margin_pct`, `revenue_per_employee_eur_k`, `international_revenue_pct`, `cloud_revenue_pct`, `deployment_model`)

## Acceptance Criteria

- [ ] **"Efficiency & Profitability"** sheet present with columns:
  - Rank, Company, Tier, Revenue per Employee (EUR K), EBITDA Margin (%), Recurring Revenue (%), SaaS Score, Classification
  - Sorted by Revenue per Employee descending
  - Bar chart showing Revenue per Employee
- [ ] **"Market Reach"** sheet present with columns:
  - Rank, Company, Tier, International Revenue (%), Countries Active, Deployment Model, Cloud Revenue (%), Geographic Score, Classification
  - Sorted by International Revenue % descending
  - Bar chart showing International Revenue %
- [ ] Both sheets have same styling as existing sheets (header fill, borders, Eneve highlight, classification colors)
- [ ] Auto-filter and frozen headers on both sheets
- [ ] Company hyperlinks work on both sheets
- [ ] Script compiles clean

## Implementation Strategy

### 1. `write_efficiency_sheet()` Function

Follow the exact pattern of `write_revenue_leaderboard()`:

```python
def write_efficiency_sheet(wb: Workbook, competitors: list[dict], link_base: Optional[Path] = None) -> None:
    """Efficiency & Profitability leaderboard."""
    ws = wb.create_sheet("Efficiency & Profitability")

    headers = [
        "Rank", "Company", "Tier", "Revenue/Employee (EUR K)",
        "EBITDA Margin (%)", "Recurring Revenue (%)", "SaaS Score", "Classification",
    ]
    # ... standard header setup, freeze panes ...
    
    sorted_comps = sorted(
        competitors,
        key=lambda c: c.get("profitability", {}).get("revenue_per_employee_eur_k") or 0,
        reverse=True,
    )
    
    for row_idx, comp in enumerate(sorted_comps, 2):
        # ... standard row writing with style_data_cell and add_company_link ...
    
    # Add bar chart for Revenue/Employee
    # ... standard chart pattern ...
```

### 2. `write_market_reach_sheet()` Function

```python
def write_market_reach_sheet(wb: Workbook, competitors: list[dict], link_base: Optional[Path] = None) -> None:
    """Market Reach & Geographic Expansion."""
    ws = wb.create_sheet("Market Reach")

    headers = [
        "Rank", "Company", "Tier", "International Revenue (%)",
        "Countries Active", "Deployment Model", "Cloud Revenue (%)",
        "Geographic Score", "Classification",
    ]
    
    sorted_comps = sorted(
        competitors,
        key=lambda c: c.get("geographic", {}).get("international_revenue_pct") or 0,
        reverse=True,
    )
    # ... standard row writing + chart ...
```

### 3. Wire into `generate_workbook()`

Add calls between Classification Matrix and Raw Data:

```python
log.info("Writing Efficiency & Profitability...")
write_efficiency_sheet(wb, competitors, link_base)

log.info("Writing Market Reach...")
write_market_reach_sheet(wb, competitors, link_base)
```

### 4. Import New Accessors

Import the new accessor functions from `competitor_utils.py` added in FD-003.

## Testing Strategy

1. `python -m py_compile generate_excel_report.py`
2. Generate workbook with data extracted by updated FD-003 pipeline
3. Verify Efficiency sheet sorts correctly and EBITDA/Revenue-per-employee values are populated
4. Verify Market Reach sheet shows geographic data where available
5. Verify null/missing data shows as empty cells (not errors)

## Risks

- **Sparse data**: Many competitors may lack EBITDA or geographic data. Sheets may have many blank cells. This is expected -- the data availability tells its own story.
- **Sorting with nulls**: Ensure the `or 0` fallback in sort keys doesn't misrank competitors with missing data.

## Status

**Current**: Planning (blocked by FD-003)

## Dependencies

- **FD-003** (Extract Additional Data) must be completed first
