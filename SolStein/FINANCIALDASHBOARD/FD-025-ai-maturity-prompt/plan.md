# FD-025: AI Maturity Research Prompt

**Parent**: [FINANCIALDASHBOARD](../plan.md) -- Phase 4 (Data Collection Completeness)
**Feeds**: [FD-012](../FD-012-ai-maturity-matrix/plan.md) (AI Maturity Matrix sheet)

## Objective

Create a new prompt `research-ai-maturity.prompt.md` that produces a structured, scoreable AI maturity assessment per competitor. The existing `research-competitor` prompt collects AI data qualitatively (features, hiring signals, partnerships) but lacks a numeric scoring rubric that the dashboard extraction scripts can consume.

## Why a Separate Prompt

The `research-competitor` prompt covers 8 broad categories. AI maturity needs deeper, more structured investigation:

- **Feature inventory**: Specific AI/ML features in production vs announced vs roadmap
- **Team composition**: AI/ML headcount, seniority distribution, hiring velocity
- **Technology stack**: ML frameworks, cloud AI services, data infrastructure
- **Data strategy**: Training data access, data partnerships, proprietary datasets
- **AI product integration**: Embedded AI vs bolt-on vs standalone AI products
- **AI maturity level**: Experimenting / Implementing / Scaling / AI-Native

## Acceptance Criteria

- [ ] Prompt file created at `.cursor/prompts/analysis/market/research-ai-maturity.prompt.md`
- [ ] YAML frontmatter follows Prompt Registry standards (`name`, `description`, `category`, `tags`)
- [ ] 6-dimension AI Maturity Scorecard defined with explicit 1-10 rubric (comparable to Growth Scorecard)
- [ ] Dimensions: AI Features in Production, AI Team & Hiring, AI Technology Stack, Data Strategy, AI Product Integration, AI Maturity Level
- [ ] Output format produces `tickets/COMPETITION/[company-slug]/ai-maturity.md` as standalone file
- [ ] Output includes composite AI Maturity Score that extraction scripts can parse
- [ ] Mermaid chart template included for per-competitor AI maturity radar
- [ ] Quality criteria checklist included
- [ ] Prompt tested on at least 1 competitor before committing

## Complexity Assessment

- **Classification**: Complex Implementation (new prompt with scoring rubric design)
- **Effort**: 2-3 hours
- **Risk**: Low

## Implementation Strategy

1. Study Growth Scorecard rubric in `research-financial-growth` as the pattern to follow
2. Define 6 AI maturity dimensions with explicit 1-10 criteria tables
3. Define research categories and search strategies per dimension
4. Define output format with structured tables and composite score
5. Add Mermaid chart template
6. Test on one competitor (suggest Octopus/Kraken as highest expected scorer)
