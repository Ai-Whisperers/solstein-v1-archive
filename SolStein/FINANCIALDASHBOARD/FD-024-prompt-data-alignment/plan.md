# FD-024: Prompt-Dashboard Data Alignment Audit

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)

## Objective

Audit all 5 existing market analysis prompts against the data requirements of all dashboard sheets (Phase 1-3) and identify gaps where prompts do not collect data that the dashboard needs. Update existing prompts to close those gaps.

## Current State

Five prompts exist in `.cursor/prompts/analysis/market/`:

| Prompt | Collects |
|---|---|
| `research-competitor` | 8 categories: fundamentals, market position, product/tech, AI & innovation, growth, commodities, pricing, threat assessment |
| `research-financial-growth` | 6 categories: revenue, funding, employees, geographic expansion, M&A, SaaS transition + Growth Scorecard |
| `research-company-history` | Corporate genealogy: ownership, M&A timeline, name changes, investment events |
| `research-protocols` | Protocol-to-company mapping by country |
| `generate-financial-dashboard` | Synthesis: reads all data, generates dashboard |

Dashboard sheets that consume this data:

| Sheet | Data Source | Gap? |
|---|---|---|
| Executive Summary | Growth Scorecard composites | OK -- from `research-financial-growth` |
| Revenue Leaderboard | Revenue timeline, CAGR | OK |
| Funding Leaderboard | Funding rounds, total raised, valuation | OK |
| Employee Growth | Headcount timeline, open positions | OK |
| SaaS Maturity | Recurring revenue %, deployment model | OK |
| Classification Matrix | Composite scores | OK |
| Efficiency & Profitability | Revenue/employee, EBITDA margin | OK |
| Market Reach | Countries, exchanges, protocols | Partial -- protocols from `research-protocols` but not structured for Excel extraction |
| Eneve vs Market | All composites + Eneve estimates | OK |
| **AI Maturity Matrix (FD-012)** | AI features, AI team size, AI partnerships, AI maturity score | **GAP** -- `research-competitor` collects AI data but no structured scoring rubric |
| **Investment Efficiency (FD-013)** | Revenue/employee, capital efficiency, hiring efficiency | Partial -- ratios calculable but not explicitly scored |
| **M&A Vulnerability (FD-014)** | Acquisition history, war chest, PE backing | Partial -- data exists but no vulnerability classification |
| **Threat Timeline (FD-015)** | Milestone events with dates | Partial -- scattered across competitor files |
| **Competitive Overlap (FD-016)** | Pairwise product/market overlap | **GAP** -- no prompt collects overlap data |
| **Geographic Tracker (FD-017)** | Country-by-country presence | Partial -- geographic expansion in `research-financial-growth` but not structured as a matrix |
| **Confidence Dashboard (FD-018)** | Data quality scores per competitor | **GAP** -- no systematic confidence scoring |
| **Scenario Projections (FD-019)** | Current CAGR rates | OK -- calculable from existing data |
| **Portfolio Risk (FD-020)** | Aggregate risk factors | Partial -- needs synthesis of multiple dimensions |
| **Dynamic Filters (FD-021)** | All raw data with consistent schema | Partial -- schema consistency not enforced across prompts |

## Identified Gaps

1. **AI Maturity Scoring** -- `research-competitor` collects AI data qualitatively but lacks a 1-10 scoring rubric comparable to the Growth Scorecard. Dashboard FD-012 needs structured scores.
2. **Competitive Overlap Matrix** -- No prompt collects pairwise overlap between competitors. Dashboard FD-016 needs a 33x33 matrix.
3. **Data Confidence Scoring** -- No prompt systematically scores data quality/completeness per competitor. Dashboard FD-018 needs this.
4. **Market Trends / Regulatory** -- No prompt tracks macro trends (EU regulations, protocol convergence, AI adoption curves) that inform the Meteor Warning and scenario projections.
5. **Customer Intelligence** -- No prompt collects customer win/loss data, switching patterns, or reference client lists that would strengthen threat assessment.
6. **Perplexity Integration** -- All research is manual web search; Perplexity API could accelerate data collection across all prompts.

## Acceptance Criteria

- [ ] Gap analysis table complete (prompt vs dashboard sheet vs data point)
- [ ] Each gap has a corresponding ticket (FD-025 through FD-030)
- [ ] Existing prompts reviewed for schema consistency (field names, scoring rubrics match what extraction scripts expect)
- [ ] Recommendations documented for updating existing prompts (if minor changes suffice vs creating new prompts)
- [ ] No dashboard sheet left without a clear data collection pathway

## Complexity Assessment

- **Classification**: Simple Fix (analysis and documentation only, no code changes)
- **Effort**: 1-2 hours
- **Risk**: Low

## Implementation Strategy

1. Map every dashboard sheet column to its source prompt and data field
2. Identify mismatches (missing fields, inconsistent naming, no scoring rubric)
3. For each gap, determine: update existing prompt vs create new prompt
4. Create sub-tickets for new prompts (FD-025 through FD-029)
5. Create integration ticket for Perplexity (FD-030)
