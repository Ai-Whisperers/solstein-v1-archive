# FD-027: Data Confidence Assessment Prompt

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Feeds**: [FD-018](../FD-018-confidence-dashboard/plan.md) (Confidence Dashboard sheet)

## Objective

Create a new prompt `assess-data-confidence.prompt.md` that systematically scores the data quality, completeness, and research depth for each competitor. The dashboard's FD-018 needs per-competitor confidence scores to help decision-makers understand which data points are reliable and where further research is needed.

## Why a Separate Prompt

Individual research prompts mark data points as Confirmed/Estimated/Unknown, but no prompt aggregates these into an overall confidence score per competitor. Without this, the dashboard presents all competitors as equally well-researched, which is misleading.

## Requirements

1. Score **Completeness**: percentage of data fields filled vs Unknown per competitor
2. Score **Source Quality**: percentage of data points from primary sources (annual reports) vs estimates
3. Score **Recency**: how current the data is (2026 data vs 2023 data)
4. Score **Consistency**: whether different research files agree or contain contradictions
5. Score **Research Depth**: which research prompts have been run (identification only vs full deep-dive)
6. Produce a **Composite Confidence Score** per competitor (average of the 5 dimensions)
7. Classify each competitor with a **traffic-light** rating: High (7-10), Medium (4-6), Low (1-3)
8. Generate **prioritized action items**: which competitors need more research and which prompts to run next

## Acceptance Criteria

- [ ] Prompt file created at `.cursor/prompts/analysis/market/assess-data-confidence.prompt.md`
- [ ] YAML frontmatter follows Prompt Registry standards
- [ ] 5-dimension confidence scoring rubric defined with 1-10 scale
- [ ] Dimensions: Completeness, Source Quality, Recency, Consistency, Research Depth
- [ ] Output format produces `tickets/COMPETITION/data-confidence.md` with per-competitor scores
- [ ] Composite Confidence Score per competitor (average of 5 dimensions)
- [ ] Traffic-light classification: High (7-10), Medium (4-6), Low (1-3)
- [ ] Action items generated: which competitors need more research and which prompts to run
- [ ] Quality criteria checklist included

## Complexity Assessment

**Track**: Simple Fix

**Rationale**: Single deliverable (one prompt file), reads existing competitor research data without modifying it, well-understood prompt authoring pattern.

**Criteria Met**:
- Root Cause: Single (missing aggregation prompt)
- Files Affected: 1 (new prompt file)
- Lines Changed: ~100-150 (prompt content)
- Risk Level: Low (read-only analysis, no side effects on existing data)
- Solution Pattern: Known (follows established prompt authoring standards)

**Effort**: 1-2 hours

## Implementation Strategy

1. Define confidence dimensions and 1-10 scoring rubric
2. Define which files to check per competitor (identification, deep-analysis, financial-growth, corporate-history, protocol-map, ai-maturity)
3. Define output format with per-competitor table and composite scores
4. Include prioritized action list (which competitors need research first)
5. Test against full competitor set

## Status

Complete
