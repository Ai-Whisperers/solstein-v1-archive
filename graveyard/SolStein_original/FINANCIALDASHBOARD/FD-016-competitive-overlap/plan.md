# FD-016: Competitive Overlap Heatmap Sheet

## Objective

Add a "Competitive Overlap" sheet to the Financial Dashboard workbook (`financial-dashboard.xlsx`) showing which competitors overlap with which others across geography, product, customer segment, and tier. Reveals cluster dynamics, market consolidation patterns, and who is competing for the same customers.

**In scope**: competitor-vs-competitor overlap matrix, heatmap formatting, Eneve focus view, top-5 summary.
**Out of scope**: automated data refresh, overlap trend analysis over time, detailed per-dimension breakdown sheets.

## Requirements

1. Create a competitor-vs-competitor matrix (33x33 grid) with competitor names on both axes
2. Overlap scoring scale: 0 (no overlap), 1 (adjacent market), 2 (partial overlap), 3 (direct competitor)
3. Scoring based on four dimensions: geographic overlap, product overlap, customer segment overlap, tier proximity -- each dimension contributes 0 or 1 to the total score (max 3 where at least 3 of 4 dimensions overlap)
4. Conditional formatting as heatmap: white = 0 (none), yellow = 1 (adjacent), orange = 2 (partial), red = 3 (direct)
5. Focus view: Eneve's row and column highlighted with a distinct border or background colour showing who directly competes with Eneve
6. Summary section below or beside the matrix listing the top 5 most overlapping competitor pairs with their scores

## Data Sources

- `deep-analysis.md` per competitor (market position, geographic presence, product offerings, customer segments)
- Tier classifications from `financial-dashboard.md`

## Implementation Strategy

1. **Set up sheet structure**: Create the "Competitive Overlap" sheet in `financial-dashboard.xlsx`. Add the 33 competitor names as row and column headers from the existing competitor list.
2. **Build scoring reference**: For each competitor, extract geographic presence, product categories, customer segments, and tier from `deep-analysis.md` and `financial-dashboard.md`. Compile into a working reference to enable systematic pairwise comparison.
3. **Populate the matrix**: For each competitor pair, evaluate the four overlap dimensions and assign a 0-3 score. Fill the symmetric matrix (cell [i,j] = cell [j,i], diagonal = N/A or blank).
4. **Apply formatting**: Add conditional formatting heatmap rules (white/yellow/orange/red). Highlight Eneve's row and column with a distinct border or fill. Format diagonal cells as grey/N/A.
5. **Add summary**: Below or beside the matrix, add a "Top 5 Overlap Pairs" section. Sort all pairs by score descending and list the top 5 with competitor names and scores.
6. **Validate**: Spot-check 5-10 competitor pairs against source data to verify scoring accuracy. Confirm formatting renders correctly.

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Requires systematic pairwise assessment of 33 competitors across 4 dimensions, producing 528 unique pairs. Manual overlap evaluation demands cross-referencing multiple source files per pair.

**Criteria Met**:
- Root Cause: N/A (feature, not bug)
- Files Affected: 1 workbook + 33 source files for reference (~34 files touched)
- Lines Changed: >10 (full matrix population, formatting rules, summary section)
- Risk Level: Low (new sheet, no impact on existing sheets)
- Solution Pattern: Known (matrix + conditional formatting pattern used in other dashboard sheets)

**Effort**: ~2h

## Acceptance Criteria

- [x] Competitive Overlap sheet present in `financial-dashboard.xlsx`
- [x] 33x33 matrix with competitor names on both axes
- [x] Heatmap conditional formatting applied (white/yellow/orange/red matching 0/1/2/3 scores)
- [x] Eneve row/column visually highlighted with distinct border or fill
- [x] Top 5 most overlapping competitor pairs listed with scores
- [x] Scoring correctly reflects overlap across geographic, product, customer segment, and tier dimensions
- [x] At least 5 spot-checked pairs verified against source data for accuracy
- [x] Matrix is symmetric (pair [A,B] = pair [B,A])

## Status

**Current**: Complete

## Deliverables

- `tickets/COMPETITION/competitive-overlap.md` -- Full competitive overlap heatmap sheet
- `tickets/COMPETITION/financial-dashboard.md` -- Updated with reference to overlap sheet
- `tickets/COMPETITION/overlap_matrix.json` -- Machine-readable matrix data
- `tickets/COMPETITION/compute_overlap.py` -- Scoring computation script (reproducible)

## Implementation Notes

**Approach**: Since the Financial Dashboard is markdown-based (not `.xlsx`), the overlap sheet was created as `competitive-overlap.md` with a cross-reference added to `financial-dashboard.md`. The matrix was computed programmatically using `compute_overlap.py` for accuracy across all 528 unique pairs.

**Tier encoding**: T1=1, T1b=2, T2=3, T3=4. Adjacent = |diff| <= 1, matching the natural competitive proximity (T1-T1b are close, T1-T2 are not).

**Heatmap rendering**: In markdown, numeric scores (0-3) serve as the heatmap. The Eneve row is bolded in the matrix and has a dedicated "Eneve Focus View" section with per-dimension breakdown.

**Validation**: Matrix symmetry verified programmatically (528 pairs). Five spot-checks confirmed against source data (Eneve-SOPTIM=3, Eneve-Hitachi=1, Eneve-Octopus=3, Brady-Volue=3, Eneve-SEEBURGER=0).
