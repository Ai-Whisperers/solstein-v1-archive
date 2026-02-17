# FD-029: Customer Intelligence Research Prompt

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Feeds**: [FD-014](../FD-014-mna-vulnerability/plan.md) (M&A Vulnerability), [FD-016](../FD-016-competitive-overlap/plan.md) (Competitive Overlap), [FD-020](../FD-020-portfolio-risk/plan.md) (Portfolio Risk)

## Objective

Create a new prompt `research-customer-intelligence.prompt.md` that collects customer win/loss data, reference client lists, switching patterns, and implementation case studies per competitor. This strengthens the threat assessment by showing where competitors actually win deals (not just where they theoretically compete).

## Why a Separate Prompt

The existing `research-competitor` prompt has a "Notable Customers" field under Market Position, but it collects names without context. Customer intelligence needs:

- **Reference client inventory**: Named customers by segment (TSO, DSO, supplier, trader, BRP, industrial)
- **Win/loss signals**: Press releases announcing new customer wins, contract renewals, expansions
- **Switching patterns**: Evidence of customers migrating from one vendor to another (especially relevant for customers leaving legacy vendors)
- **Implementation case studies**: Timeline, scope, and success metrics from published case studies
- **Customer concentration risk**: How dependent is a competitor on a few large accounts?
- **Eneve customer overlap**: Are any Eneve customers also evaluating or using competitor products?

## Requirements

1. Create a reusable prompt file that guides AI research into competitor customer bases using only public sources
2. Collect **reference client inventory** per competitor, categorized by segment (TSO, DSO, supplier, trader, BRP, industrial)
3. Collect **win/loss signals**: press releases, contract announcements, renewals, and expansions
4. Document **switching patterns**: evidence of customers migrating between vendors, especially away from legacy platforms
5. Gather **implementation case studies**: published timelines, scope, and success metrics
6. Assess **customer concentration risk**: determine how dependent each competitor is on a small number of large accounts
7. Include an **Eneve customer overlap** assessment to identify customers evaluating or using competitor products alongside Eneve
8. Enforce **data quality constraints**: public sources only, source attribution required, no speculation on private contracts

## Acceptance Criteria

- [ ] Prompt file created at `.cursor/prompts/analysis/market/research-customer-intelligence.prompt.md`
- [ ] YAML frontmatter follows Prompt Registry standards
- [ ] 5 research categories: Reference Clients, Win/Loss Signals, Switching Patterns, Case Studies, Customer Concentration
- [ ] Output format produces `tickets/COMPETITION/[company-slug]/customer-intelligence.md` as standalone file
- [ ] Customer count and segment distribution table included
- [ ] Switching pattern evidence documented with source attribution
- [ ] Eneve customer overlap assessment included
- [ ] Quality criteria checklist included

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: This prompt requires careful design across 5 distinct research categories, each with unique search strategies and structured output tables. Source attribution and data quality constraints (public-only) add sensitivity that demands careful prompt engineering. The output format must integrate with multiple downstream tickets (FD-014, FD-016, FD-020).

**Criteria Met**:
- Root Cause: Multiple (5 research categories with distinct data needs)
- Files Affected: 1 prompt file + output template design
- Lines Changed: >50 (full prompt with frontmatter, categories, output format, quality guidelines)
- Risk Level: Medium (customer data often proprietary; must rely on public sources only)
- Solution Pattern: Known (follows existing research-competitor prompt pattern, but extended)

**Decision Principle Applied**: When in doubt, prefer Complex track

**Effort**: 2-3 hours

## Status

Complete

## Implementation Strategy

1. Define 5 customer intelligence categories with search strategies
2. Define output format with structured tables per category
3. Include guidance on public source identification (press releases, case studies, conference talks)
4. Include Eneve overlap assessment section
5. Add data quality guidelines (public sources only, no speculation on private contracts)
6. Test on one well-documented competitor (suggest Hansen Technologies -- public company with disclosed customer data)
