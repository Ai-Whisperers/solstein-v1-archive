# FD-032: Update Financial Dashboard Prompt + Exemplar to Full 18-Sheet Scope

## Objective

Update `generate-financial-dashboard.prompt.md` and `financial-dashboard-exemplar.md` to reflect the full 18-sheet workbook scope (Phase 1-3 sheets) instead of the original 7-sheet Phase 1 scope. The prompt and exemplar are outdated -- they describe the initial dashboard but the workbook has grown to include AI Maturity, M&A Landscape, Investment Efficiency, Threat Timeline, Competitive Overlap, Confidence Dashboard, Scenario Projections, Portfolio Risk, and Data Explorer sheets.

## Requirements

- Update `generate-financial-dashboard.prompt.md` to reference all 18+ sheets
- Add data source mapping for each Phase 3 sheet (which prompt produces its input data)
- Update script references to reflect current `generate_excel_report.py` capabilities (~3000 lines, 18 sheets)
- Update `financial-dashboard-exemplar.md` output format template from 7-sheet to 18-sheet scope
- Add Phase 3 sheet templates to exemplar (AI Maturity, M&A, Investment Efficiency, etc.)
- Update Mermaid chart references to include all new chart types (heatmap, bubble, scatter)
- Ensure downstream data flow from Phase 4 prompts is documented

## Acceptance Criteria

- [ ] `generate-financial-dashboard.prompt.md` lists all 18+ sheets with data source mapping
- [ ] Prompt references all Phase 4 data collection prompts as upstream dependencies
- [ ] `financial-dashboard-exemplar.md` output template covers all sheet types
- [ ] Exemplar includes new chart types (heatmap, bubble, scatter, timeline)
- [ ] Script integration section updated with current function names and capabilities
- [ ] No broken references to old sheet names or missing sheets
- [ ] Prompt passes quality criteria from `prompt-creation-rule.mdc`

## Implementation Strategy

1. Read current `generate-financial-dashboard.prompt.md` and identify all outdated references
2. Read `generate_excel_report.py` to extract current sheet list and data requirements
3. Map each sheet to its upstream data source (prompt or script-computed)
4. Update prompt Required Context, Process, Output Format, and Script Integration sections
5. Read current `financial-dashboard-exemplar.md` and identify scope gaps
6. Update exemplar with full output template covering all 18 sheets
7. Validate against prompt-creation-rule quality criteria

## Complexity Assessment

**Track**: Simple Fix
**Rationale**: Content update to two existing files, no new code, no architectural changes. Focused editing of known artifacts.
- Root Cause: Prompt drift -- dashboard evolved but prompt/exemplar weren't updated
- Files Affected: 2 (prompt + exemplar)
- Lines Changed: ~100-200 (content additions)
- Risk Level: Low
- Solution Pattern: Known (document update)

## Status

Planning

## Testing Strategy

- Verify prompt invocation still produces valid output
- Check all sheet names match `generate_excel_report.py` function names
- Validate exemplar Mermaid charts render correctly

## Notes

- This is the highest-priority prompt improvement because it affects how the entire dashboard is described
- Depends on: No code dependencies, but should reference FD-025 through FD-029 prompts as data sources
- Related: FD-024 (gap analysis that identified this need)
