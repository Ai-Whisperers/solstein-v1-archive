# FD-032: Context

**Last Updated**: 2026-02-17

## Technical Background

The `generate-financial-dashboard.prompt.md` was written during Phase 1 when the workbook had 7 sheets. The dashboard has since grown to 18+ sheets across Phase 1-3. The prompt still describes only the original scope, which makes it misleading for anyone invoking it. The companion `financial-dashboard-exemplar.md` has the same gap.

## Current Focus

Identify all discrepancies between prompt/exemplar and actual dashboard scope, then update both files.

## Key Components

- `.cursor/prompts/analysis/market/generate-financial-dashboard.prompt.md` -- Main prompt file
- `.cursor/exemplars/analysis/market/financial-dashboard-exemplar.md` -- Companion exemplar
- `.cursor/scripts/analysis/market/generate_excel_report.py` -- Source of truth for sheet list (~3000 lines)
- `.cursor/scripts/analysis/market/generate_markdown_dashboard.py` -- Markdown dashboard generator

## Outstanding Issues

- Prompt only references 7 original sheets; 11+ new sheets missing
- Exemplar output template is incomplete
- No data source mapping for Phase 3 sheets
- Script integration section references outdated function names

## Next Steps

1. Diff current prompt against `generate_excel_report.py` sheet list
2. Build complete sheet-to-data-source mapping table
3. Update prompt and exemplar files
