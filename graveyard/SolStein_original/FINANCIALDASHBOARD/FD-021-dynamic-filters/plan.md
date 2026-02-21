# FD-021: Dynamic Filters / Slicers

## Objective

Add Excel pivot table(s) with slicers for interactive exploration of competitor data. Let the PE analyst explore the data themselves -- interactive means sticky, and sticky means they keep coming back.

**In scope**: Pivot table creation, slicer configuration, styling, reset instructions on a dedicated "Data Explorer" sheet.
**Out of scope**: VBA macros, external data connections, dashboard-level charting from pivot data.

## Requirements

1. Create a "Data Explorer" sheet with pivot table sourced from Raw Data
2. Add slicers for: Tier, Classification (Rocket/Riser/Steady/Dinosaur), Country/Region, AI Score Range, Revenue Range
3. Pivot table dimensions: Company (rows), Metrics (columns: Revenue, CAGR, Composite, AI Score, SaaS Score, Employees)
4. Default view: all competitors, sorted by composite score
5. Slicer styling: match workbook color palette
6. Include a "Reset Filters" instruction note

## Data Sources

- Raw Data sheet (already exists, needs AI Score and geographic columns added)

## Dependencies

- FD-012 (AI Maturity data must be in Raw Data)
- FD-017 (Geographic data must be in Raw Data)

## Implementation Strategy

1. **Verify Raw Data readiness**: Confirm Raw Data sheet contains all required columns (Tier, Classification, Country/Region, AI Score, Revenue, CAGR, Composite, SaaS Score, Employees) after FD-012 and FD-017 are complete
2. **Create pivot table**: Use openpyxl to insert a pivot table on a new "Data Explorer" sheet, with Company as row field and the 6 metric columns as data fields; set default sort by Composite score descending
3. **Add slicers**: Programmatically add slicer objects for Tier, Classification, Country/Region, AI Score Range, and Revenue Range; connect each slicer to the pivot table cache
4. **Style slicers and sheet**: Apply workbook color palette to slicer buttons and headers; format the Data Explorer sheet header and layout to match the overall workbook theme
5. **Add reset instructions**: Insert a text box or cell note near the slicers explaining how to clear all filters (e.g., "Right-click any slicer > Clear Filter, or press Alt+C on each slicer")
6. **Validate in Excel**: Open the generated workbook in Excel and manually verify each slicer filters the pivot table correctly and that the reset instructions are visible

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Pivot tables and slicers require specific openpyxl handling that is not straightforward; the API for pivot caches, slicer connections, and slicer styling is less commonly documented.

**Criteria Met**:
- Root Cause: Multiple interconnected components (pivot cache, slicer objects, styling, sheet layout)
- Files Affected: 1-2 (main workbook generation script + possibly a helper/utility module)
- Lines Changed: ~50-100 lines of new pivot/slicer generation code
- Risk Level: Medium (openpyxl pivot/slicer support has limitations; may need workarounds)
- Solution Pattern: Partially known (openpyxl pivot tables documented, but slicer API is less mature)

**Effort**: 2-3h

## Acceptance Criteria

- [ ] Data Explorer sheet present with pivot table showing Company rows and 6 metric columns
- [ ] At least 4 slicers functional and connected to the pivot table
- [ ] Slicers styled to match workbook color palette
- [ ] Each slicer correctly filters the pivot table rows when a value is selected in Excel
- [ ] Clearing a slicer restores the full dataset in the pivot table
- [ ] Reset instructions visible near the slicers

## Status

Complete
