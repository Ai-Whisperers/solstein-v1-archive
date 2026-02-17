# FD-017: Geographic Expansion Tracker Sheet

## Objective

Add a "Geographic Reach" sheet showing which competitors operate in which countries, with expansion trajectories. Shows who's entering your portfolio company's markets and how dense each market is competitively.

**Scope**: Country-level presence mapping for 33 analyzed competitors across European energy markets. Does not include historical presence tracking or sub-national regional detail.

## Requirements

1. Country-vs-Competitor matrix for key European markets: NL, DE, BE, UK, NO, SE, DK, FI, FR, ES, IT, AT, CH, PL + Rest of World
2. Cell values: Active (A), Entering (E), Planned (P), None (-)
3. Conditional formatting: Active=green, Entering=yellow, Planned=light yellow, None=no fill
4. Summary row: number of active competitors per country
5. Summary column: number of countries per competitor
6. Chart: bar chart of "competitors per country" showing market density
7. Highlight NL column as the home market focus

## Data Sources

- `deep-analysis.md` per competitor (geographic presence section)
- `financial-growth.md` (geographic expansion scores)

## Implementation Strategy

1. **Extract geographic data**: Parse each competitor's `deep-analysis.md` for geographic presence mentions; cross-reference with `financial-growth.md` Geo Expand scores to infer A/E/P status where explicit data is sparse
2. **Build data structure**: Create a Python dictionary mapping each competitor to their country-level presence status (A/E/P/-)
3. **Generate sheet**: Use openpyxl to create the "Geographic Reach" sheet with the country-vs-competitor matrix
4. **Apply formatting**: Add conditional formatting rules (green/yellow/light yellow), highlight NL column with distinct border or background
5. **Add summaries**: Insert COUNTIF formulas for competitor-per-country row and country-per-competitor column
6. **Create chart**: Add a bar chart on the same sheet (or adjacent) visualizing competitors-per-country density
7. **Validate**: Spot-check 5+ competitors against source data to confirm accuracy

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Geographic presence data is not systematically structured in source files -- requires NLP-style parsing of free-text geographic sections across 33 competitor files, plus cross-referencing with financial growth scores. New extraction logic needed.

**Criteria Met**:
- Root Cause: Multiple (data scattered across 33+ files, no standard format)
- Files Affected: 33 deep-analysis files + 1 financial-growth file + 1 output workbook
- Lines Changed: >50 (new extraction + sheet generation logic)
- Risk Level: Medium (parsing accuracy depends on source data quality)
- Solution Pattern: Known (openpyxl matrix generation), but extraction logic is novel

## Acceptance Criteria

- [ ] Geographic Reach sheet present in output workbook
- [ ] At least 15 countries tracked (NL, DE, BE, UK, NO, SE, DK, FI, FR, ES, IT, AT, CH, PL + Rest of World)
- [ ] All 33 competitors mapped with a row per competitor
- [ ] Cell values use correct codes: Active (A), Entering (E), Planned (P), None (-)
- [ ] Conditional formatting applied: A=green, E=yellow, P=light yellow
- [ ] NL column visually highlighted as home market
- [ ] Summary row shows competitor count per country
- [ ] Summary column shows country count per competitor
- [ ] Bar chart of market density (competitors per country) present
- [ ] Spot-check of 5 competitors confirms data accuracy against source files

## Status

Planning
