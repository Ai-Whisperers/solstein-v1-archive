# FD-023: European Geographic Map Visualization

## Objective

Add an embedded European map image to the "Geographic Reach" sheet showing competitor operations geographically -- head offices, subsidiaries, and active/entering/planned markets. Transforms the FD-017 country matrix from a data table into a visual story that a board audience can absorb at a glance.

**Scope**: European-focused map visualization using data from FD-017's country-vs-competitor matrix. Does not include interactive/zoomable maps (static PNG embedded in Excel).

## Requirements

1. European map image generated via matplotlib + geopandas, embedded as a high-resolution PNG on the Geographic Reach sheet
2. Countries colored by competitor density (darker fill = more active competitors)
3. HQ locations shown as star markers (one per competitor, positioned at country centroid or city if available)
4. Subsidiary locations shown as circle markers
5. Active markets: solid country fill; Entering markets: lighter fill; Planned markets: dashed border or lightest fill
6. Clear legend explaining all marker types, fill levels, and color scales
7. Map positioned alongside or below the FD-017 matrix on the same sheet
8. NL highlighted as the home market (distinct border or annotation)

## Data Sources

- FD-017 country-vs-competitor matrix data (A/E/P/- per country per competitor)
- `deep-analysis.md` per competitor (HQ city/country, subsidiary locations)
- Natural Earth shapefiles (via geopandas built-in datasets) for European country boundaries

## Implementation Strategy

1. **Reuse FD-017 data**: Consume the geographic data structure built by FD-017 (country presence status per competitor)
2. **Extract location detail**: Parse each competitor's `deep-analysis.md` for HQ city/country and subsidiary locations; map to coordinates using a city-to-coordinate lookup or country centroids as fallback
3. **Render base map**: Use geopandas to plot European country boundaries from Natural Earth shapefiles, cropped to the European region
4. **Apply density coloring**: Color each country by the count of active competitors (choropleth style, sequential color scale)
5. **Overlay market status**: Distinguish active/entering/planned countries with fill opacity or hatching patterns
6. **Plot markers**: Overlay HQ locations (star markers) and subsidiary locations (circle markers) with appropriate sizing and colors
7. **Add legend and annotations**: Include a clear legend, highlight NL as home market, add title
8. **Export PNG**: Save as high-resolution PNG (300 DPI minimum for print quality in Excel)
9. **Embed in Excel**: Use openpyxl's `Image` class to place the map PNG on the Geographic Reach sheet, sized appropriately alongside the matrix
10. **Validate**: Verify map markers match FD-017 matrix data; spot-check 5+ competitors for correct HQ placement

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Introduces new dependencies (geopandas, matplotlib cartographic features) and requires coordinate data extraction from unstructured text. Map rendering logic is distinct from existing openpyxl chart generation.

**Criteria Met**:
- Root Cause: Multiple (new dependency chain, coordinate extraction from free text, cartographic rendering)
- Files Affected: 33 deep-analysis files (read) + report generator + new map generation module
- Lines Changed: >60 (map rendering + coordinate extraction + image embedding)
- Risk Level: Medium (geopandas dependency weight; coordinate accuracy depends on source data quality)
- Solution Pattern: Known (matplotlib/geopandas choropleth maps), but integration with openpyxl image embedding is new for this project

## Acceptance Criteria

- [ ] European map image embedded on the Geographic Reach sheet
- [ ] Countries colored by competitor density (choropleth, darker = more competitors)
- [ ] HQ locations displayed as star markers at correct country positions
- [ ] Subsidiary locations displayed as circle markers
- [ ] Active, entering, and planned markets visually distinguished on the map
- [ ] NL highlighted as home market on the map
- [ ] Legend clearly explains all marker types and color scales
- [ ] Map is high-resolution (readable when printed from Excel)
- [ ] Map data matches FD-017 matrix (spot-check 5+ competitors)
- [ ] geopandas and matplotlib added to requirements.txt

## Dependencies

- **FD-017**: Must be completed first -- FD-023 consumes FD-017's extracted geographic data structure

## Status

Planning
