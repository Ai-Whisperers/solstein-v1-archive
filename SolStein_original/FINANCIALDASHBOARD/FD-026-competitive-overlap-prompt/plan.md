# FD-026: Competitive Overlap Research Prompt

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Feeds**: [FD-016](../FD-016-competitive-overlap/plan.md) (Competitive Overlap Heatmap sheet)

## Objective

Create a new prompt `research-competitive-overlap.prompt.md` that produces a pairwise competitive overlap assessment between all tracked competitors. The dashboard's FD-016 needs a 33x33 matrix showing where competitors overlap in market segments, geographies, product capabilities, and customer base.

## Why a Separate Prompt

No existing prompt collects pairwise overlap data. The `research-competitor` prompt profiles individual companies; the `generate-financial-dashboard` prompt synthesizes per-competitor scores. Neither compares competitors against each other.

Overlap analysis requires:

- **Product capability overlap**: Which competitors offer the same module types?
- **Geographic overlap**: Which competitors operate in the same countries?
- **Market segment overlap**: Wholesale trading vs retail billing vs grid balancing vs nominations
- **Customer base overlap**: Competing for the same buyer persona (TSOs, suppliers, traders, BRPs)
- **Technology overlap**: Similar tech stacks enabling competitive switching

## Requirements

- R1: Prompt must define 5 overlap dimensions (Product, Geography, Market Segment, Customer Base, Technology)
- R2: Scoring rubric must use a 0-3 integer scale per dimension (0 = no overlap, 1 = adjacent, 2 = partial overlap, 3 = direct competitor)
- R3: Output must include a full N x N pairwise matrix for all tracked competitors
- R4: Composite overlap score per pair must be the sum of all 5 dimensions (0-15 range)
- R5: Eneve must be included as a row/column with explicit self-assessment on each dimension
- R6: Prompt must follow `.prompt.md` format with YAML frontmatter per Prompt Registry standards
- R7: Process must reference existing competitor profiles from `research-competitor` prompt output as input data source

## Acceptance Criteria

- [ ] Prompt file created at `.cursor/prompts/analysis/market/research-competitive-overlap.prompt.md`
- [ ] YAML frontmatter follows Prompt Registry standards
- [ ] Overlap scoring rubric defined: 0 (no overlap), 1 (adjacent), 2 (partial overlap), 3 (direct competitor)
- [ ] 5 overlap dimensions defined: Product, Geography, Market Segment, Customer Base, Technology
- [ ] Output format produces `tickets/COMPETITION/competitive-overlap.md` with full N x N matrix
- [ ] Composite overlap score per pair (sum of 5 dimensions, 0-15 scale)
- [ ] Top-N most overlapping pairs highlighted
- [ ] Eneve's overlap with each competitor explicitly scored
- [ ] Quality criteria checklist included

## Complexity Assessment

- **Track**: Complex Implementation
- **Rationale**: New prompt creation with combinatorial (N x N) analysis pattern; no existing prompt to extend

**Criteria**:
- Root Cause: N/A (new feature, not a fix)
- Files Affected: 1 (new prompt file)
- Lines Changed: ~150-250 (full prompt with rubric, process, output format, validation)
- Risk Level: Low-Medium (matrix size grows quadratically; no existing code affected)
- Solution Pattern: Partially known (prompt structure is established; pairwise scoring is novel)

- **Effort**: 2-3 hours
- **Decision Principle**: When in doubt, prefer Complex track

## Implementation Strategy

1. Define overlap dimensions and scoring rubric
2. Design output format (N x N matrix in markdown table)
3. Define process: read all competitor profiles, score pairwise overlaps
4. Include step for Eneve self-assessment on each dimension
5. Include Mermaid heatmap or chord diagram template
6. Test with a subset of 5-6 competitors first

## Status

Complete
