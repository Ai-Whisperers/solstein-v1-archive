# FD-028: Market Trends & Regulatory Research Prompt

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Feeds**: [FD-015](../FD-015-threat-timeline/plan.md) (Threat Convergence Timeline), [FD-019](../FD-019-scenario-projections/plan.md) (Scenario Projections), [FD-020](../FD-020-portfolio-risk/plan.md) (Portfolio Risk Dashboard)

## Objective

Create a new prompt `research-market-trends.prompt.md` that tracks macro-level market trends, regulatory changes, and technology shifts in European energy software. This data feeds the Meteor Warning narrative, scenario projections, and risk assessment -- all areas where the dashboard currently relies on ad-hoc knowledge rather than structured research.

## Why a Separate Prompt

Current prompts focus on individual competitors. No prompt captures the market-wide forces that shape competitive dynamics:

- **EU regulatory changes**: Clean Energy Package, Electricity Balancing Guideline, MARI/PICASSO/TERRE platforms, network code harmonization
- **Protocol convergence**: ENTSO-E standardization eroding national moats (directly threatens Eneve's NL-only EDSN position)
- **Technology shifts**: AI adoption curves in energy, cloud migration patterns, API-first architectures
- **Market structure changes**: Consolidation waves, PE/VC investment trends in energy software, new entrant patterns
- **Customer behavior shifts**: Buyer preferences moving to SaaS, multi-market solutions, AI-enabled tools

These trends contextualize individual competitor moves and strengthen the dashboard's strategic narrative.

## Requirements

1. Create a `.prompt.md` file with YAML frontmatter compliant with Prompt Registry standards (name, description, tags, argument-hint)
2. Define 5 research categories -- Regulatory, Protocol Convergence, Technology Shifts, Market Structure, Customer Behavior -- each with 3-5 specific research questions
3. Define an impact scoring rubric: Impact (1-5 scale) and Timeline horizon (Near <1yr / Medium 1-3yr / Far 3+yr)
4. Include an Eneve-specific impact assessment column so each trend is evaluated against Eneve's current position
5. Produce output as a standalone `tickets/COMPETITION/market-trends.md` file with structured trend tables per category
6. Include a Mermaid timeline template for plotting regulatory milestones chronologically
7. Map each output section to the downstream dashboard sheet it feeds (FD-015 Threat Timeline, FD-019 Scenario Projections, FD-020 Portfolio Risk)
8. Include a quality criteria checklist within the prompt so the research output can self-validate

**Out of Scope**: Competitor-specific research (covered by existing per-competitor prompts), dashboard UI implementation, data ingestion automation.

## Acceptance Criteria

- [ ] Prompt file created at `.cursor/prompts/analysis/market/research-market-trends.prompt.md`
- [ ] YAML frontmatter follows Prompt Registry standards
- [ ] 5 research categories defined: Regulatory, Protocol Convergence, Technology Shifts, Market Structure, Customer Behavior
- [ ] Each category has 3-5 specific research questions
- [ ] Output format produces `tickets/COMPETITION/market-trends.md` as standalone file
- [ ] Each trend scored on Impact (1-5) and Timeline (Near/Medium/Far)
- [ ] Eneve-specific impact assessment per trend
- [ ] Mermaid timeline template for regulatory milestones
- [ ] Data feeds clearly mapped to dashboard sheets (FD-015, FD-019, FD-020)
- [ ] Quality criteria checklist included in prompt

## Implementation Strategy

1. Define 5 trend categories with specific research questions per category
2. Define impact scoring rubric (1-5 scale + timeline horizon)
3. Define output format with trend tables and Eneve impact column
4. Include Mermaid timeline template for regulatory milestones
5. Map each output section to the dashboard sheet it feeds
6. Test with current EU regulatory landscape as first category

## Complexity Assessment

- **Track**: Complex Implementation
- **Rationale**: Broad research scope spanning 5 distinct domains, requires designing a new analytical framework (scoring rubric + timeline template + feed mapping) with no existing prompt to extend
- **Criteria**:
  - Root Cause: N/A (feature ticket, not defect)
  - Files Affected: 1 new prompt file + 1 new output file (2 files)
  - Lines Changed: ~150-250 lines (new prompt content)
  - Risk Level: Low -- no existing code modified, additive only
  - Solution Pattern: Partially known (prompt structure is established, but scoring framework and trend taxonomy are new)
- **Decision Principle**: When in doubt, prefer Complex track
- **Effort**: 2-3 hours

## Status

Complete
