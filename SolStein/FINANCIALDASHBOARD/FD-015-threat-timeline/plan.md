# FD-015: Threat Convergence Timeline Sheet

## Objective

Add a "Threat Timeline" sheet showing when each competitive threat arrives or intensifies. Visual urgency -- the sheet that makes PE firms understand why action is needed now, not next year.

## Requirements

1. Timeline spanning 2024-2029 with key events per competitor:
   - Funding rounds (dated)
   - Market entries (dated or estimated)
   - Acquisition events (dated)
   - Regulatory changes (harmonization milestones)
2. Include rows for: Dexter (NL now), Kraken (Rotterdam hub Dec 2025), Hansen (EDSN already embedded), Volue (delisted, aggressive M&A), tem ($94M Feb 2026), Engrate (NL entry est. 2025-2026), EU harmonization (MARI, PICASSO, TERRE dates)
3. Visual format: Gantt-style timeline with color-coded threat levels
4. Conditional formatting: cells turn progressively redder as threats approach
5. Summary row: "Number of active threats in NL market" per year

## Data Sources

- `deep-analysis.md` and `corporate-history.md` for dated events
- `financial-dashboard.md` Meteor Warning section for narrative
- EU regulatory calendar for harmonization dates

## Acceptance Criteria

- [ ] Threat Timeline sheet present in the workbook
- [ ] At least 7 competitors with timeline events plotted
- [ ] EU harmonization milestones included (MARI, PICASSO, TERRE)
- [ ] Gantt-style visual formatting with color-coded threat levels
- [ ] Summary row showing "Number of active threats in NL market" per year
- [ ] Conditional formatting: cells progressively redder as threats approach current date

## Implementation Strategy

1. **Event curation**: Extract dated events from `deep-analysis.md` and `corporate-history.md` for each competitor (funding rounds, market entries, acquisitions)
2. **Regulatory calendar**: Collect EU harmonization milestones (MARI, PICASSO, TERRE go-live dates) from regulatory sources
3. **Sheet layout**: Create "Threat Timeline" sheet with rows per competitor/threat and columns per year (2024-2029), subdivided by quarter
4. **Gantt bars**: Add horizontal bars representing threat presence/activity periods using Excel cell formatting
5. **Conditional formatting**: Apply gradient color scale (green-to-red) based on proximity to current date
6. **Summary row**: Add formula row counting active threats per year column
7. **Review**: Cross-check all events against source documents for accuracy

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires manual event curation from multiple source documents combined with non-trivial Excel timeline visualization (Gantt-style formatting, conditional color scales)

**Criteria Met**:
- Root Cause: Multiple (data gathering + visualization + formatting)
- Files Affected: 1 Excel workbook + multiple source markdown files for reference
- Lines Changed: N/A (Excel sheet creation, not code)
- Risk Level: Low (new sheet, no impact on existing sheets)
- Solution Pattern: Known (Excel Gantt charts with conditional formatting)

**Effort**: ~2h

## Status

Complete
