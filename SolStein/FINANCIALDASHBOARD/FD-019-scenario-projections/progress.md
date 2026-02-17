# FD-019: Scenario Projections -- Progress

## Session: 2026-02-16

### Completed

1. Added `build_scenario_projections()` function to `generate_markdown_dashboard.py`
   - Projects revenue and employees forward 1, 2, 3 years using CAGR compound growth formula
   - Handles missing CAGR gracefully (displays "N/A")
   - Applies threshold markers (🔺) for revenue > EUR 100M and employees > 500
   - Highlights Eneve rows with bold formatting (consistent with other sections)
2. Registered section in `generate_dashboard()` pipeline (after Meteor Warning)
3. Added helper functions: `_project_value()`, `_fmt_proj_eur()`, `_fmt_proj_emp()`
4. Generated and validated output with full 33-competitor dataset
5. Inserted Scenario Projections section into `tickets/COMPETITION/financial-dashboard.md`
6. Verified script compiles cleanly (`py_compile`)

### Deliverables

- `generate_markdown_dashboard.py` -- new `build_scenario_projections()` function (~120 lines)
- `tickets/COMPETITION/financial-dashboard.md` -- new "Scenario Projections (3-Year Extrapolation)" section

### Key Data Points

- Eneve: EUR 32M → EUR 97M revenue by 2029 (44% CAGR), 135 → 251 employees (23% CAGR)
- Octopus Energy: EUR 14.5B → EUR 90.3B by 2029 (84% CAGR) -- the meteor
- Dexter Energy: EUR 14M → EUR 54M by 2029 (55% CAGR) -- fast-growing disruptor
- 8 competitors without CAGR data show "N/A" projections (no formula errors)

### Decisions

- Chart scoped to mid-market competitors (< EUR 1B current revenue) for readability
  - Mega-corps (Hitachi, CGI, ION, etc.) would make chart unreadable due to scale dominance
  - Table includes all 33 competitors for completeness
- Used bar+line chart: bars = current revenue, line = 2029 projected (shows trajectory divergence)
- Threshold markers use 🔺 (consistent with visual hierarchy in markdown)

### Acceptance Criteria Validation

- [x] Projections sheet present
- [x] 3-year projections for revenue and employees
- [x] Line chart showing trajectory convergence
- [x] Threshold highlighting applied
- [x] Disclaimer present
- [x] Handle missing CAGR gracefully (show "N/A" not errors)
