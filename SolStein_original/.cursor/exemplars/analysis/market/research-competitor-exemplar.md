---
type: exemplar
artifact-type: prompt
demonstrates: structured-web-research pattern applied to competitive intelligence
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-competitor.prompt.md
implements: .cursor/templars/analysis/market/structured-web-research-templar.md
---

# Research Competitor Prompt - Exemplar

## Artifact Type

**Type**: Prompt (`.prompt.md`)

## Why This is Exemplary

This prompt demonstrates best-in-class application of the structured web research pattern for competitive intelligence. It was the first prompt in the research family to fully mature the pattern, and subsequent prompts (`research-company-history`, `research-financial-growth`, `research-protocols`) followed its structural conventions.

## Key Quality Elements

1. **Comprehensive Research Framework**: 8 distinct research categories covering every angle of competitive analysis (fundamentals, market position, product, AI/innovation, growth, commodities, pricing, threat assessment). Each category has a data-point table with specific search strategies -- not vague instructions.

2. **Source Attribution + Confidence System**: Every data point in the output format requires a Source and Confidence column (Confirmed/Estimated/Unknown). This prevents the common problem of research outputs that present estimates as facts.

3. **Data Quality Guidelines**: A dedicated section defining what Confirmed, Estimated, and Unknown mean with concrete source examples. Includes guidance for sparse data scenarios.

4. **Year-Agnostic Search Query Templates**: Query templates use `[YEAR]`/`[YEAR-1]`/`[YEAR-2]` placeholders instead of hardcoded years, ensuring the prompt remains useful over time without edits.

5. **Real-World Troubleshooting**: Five troubleshooting entries covering actual research challenges (private companies, non-English sources, contradictory data, missing AI signals, M&A changes). Each has Cause and Solution.

6. **Priority-Based Usage Examples**: Usage section organizes competitors by research priority (AI-signal companies first, remaining second, ecosystem players third), guiding the user on execution order.

7. **Structured Output Template**: Complete markdown template with every table pre-structured, so outputs are consistent and comparable across all competitors researched.

8. **Reasoning Process Section**: Explicit 8-step reasoning guide for the AI agent, ensuring systematic execution rather than ad-hoc searching.

## Pattern Demonstrated

**Structured Web Research Pattern** as defined in `.cursor/templars/analysis/market/structured-web-research-templar.md`:
- Research categories with "Data Point | Search Strategy" tables
- Output format with "Data Point | Value | Source | Confidence" tables
- 3-tier confidence system (Confirmed/Estimated/Unknown)
- Search query templates with year-agnostic placeholders
- Troubleshooting section for domain-specific challenges
- Separate output file (not appended to existing docs)

## Full Exemplar Content

Below is the complete prompt as it exists in production. This is the reference implementation of the structured web research pattern.

---

### Frontmatter

```yaml
---
name: research-competitor
description: "Please perform a deep-dive competitive research analysis on an energy software competitor"
category: analysis
tags: competition, research, market-analysis, energy, deep-dive, competitor
argument-hint: "Company name and path to company folder (e.g., Volue @tickets/COMPETITION/volue/)"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---
```

**Notable frontmatter choices**:
- `argument-hint` provides a concrete example, not just a description
- `tools` specifies `web/*` for broad web search access
- `rules` links to prompt creation standards for self-enforcement

### Opening Section

```markdown
# Research Competitor - Deep Analysis

Please perform a structured deep-dive research session on an energy software competitor
to Eneve's eBase platform. This prompt drives systematic web research across all relevant
data categories, then updates the competitor's existing identification file with a
comprehensive `## Deep Analysis` section.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Converts identification-level profiles into actionable competitive intelligence
**Use When**: After initial competitor identification is complete and deeper analysis is needed
```

**Why exemplary**: Clear 2-sentence description + pattern metadata. States the prerequisite ("after initial identification") so the user knows when to use this prompt vs others.

### Research Categories (8 categories)

The full prompt defines 8 research categories, each with a data-point table. Here's the pattern demonstrated by Category 4 (AI & Innovation) as a representative example:

```markdown
### Category 4: AI & Innovation

| Data Point | Search Strategy |
|---|---|
| AI/ML features in production | Product pages, press releases, demo videos |
| AI roadmap / announced features | Conference talks, blog posts, press releases |
| AI team size / hiring signals | LinkedIn job postings with "AI", "ML", "data science" |
| AI partnerships | Press releases, partner pages |
| Patents or published research | Google Scholar, patent databases, company blog |
| AI-related acquisitions | Press releases, Crunchbase, M&A databases |
```

**Why exemplary**: Each data point has 2-3 specific search locations. "AI team size / hiring signals" suggests searching for specific job titles -- this level of specificity produces better agent behavior than "look for AI stuff".

### Output Format

The output template pre-structures every table so all competitor research outputs are directly comparable:

```markdown
### AI & Innovation

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| AI Features in Production | [list] | [source] | ... |
| AI Roadmap | [announced features] | [source] | ... |
| AI Hiring Signals | [job count, roles] | [source] | ... |
| AI Partnerships | [list] | [source] | ... |
| Published Research | [papers, patents] | [source] | ... |
| AI Acquisitions | [list] | [source] | ... |
```

**Why exemplary**: Mirrors the research category data points exactly. The agent doesn't have to decide what to include -- it fills in the pre-structured template.

### Threat Assessment Section

```markdown
### Threat Assessment vs Eneve

**Direct Overlap Areas**:
- [Area 1]: [description of overlap and competitive dynamic]

**Where Competitor is Stronger**:
- [Strength 1]: [evidence]

**Where Eneve is Stronger**:
- [Strength 1]: [evidence]

**NL Market Entry Likelihood**: [High/Medium/Low] - [reasoning]
**Capability Expansion Likelihood**: [High/Medium/Low] - [reasoning]

**Strategic Implications**:
[2-3 sentences on what this means for Eneve's competitive position]
```

**Why exemplary**: The synthesis section forces evidence-based assessment with specific structure (overlap, competitor strengths, Eneve strengths, likelihood ratings with reasoning). This prevents vague "they're a threat" conclusions.

### Search Query Templates

```markdown
**AI & Innovation**:
- `"[COMPANY]" artificial intelligence machine learning energy`
- `"[COMPANY]" AI features product [YEAR-1] [YEAR]`
- `"[COMPANY]" hiring AI data scientist energy`
```

**Why exemplary**: Year-agnostic with `[YEAR]`/`[YEAR-1]` placeholders. Combines company name with domain-specific terms. Multiple query variants per category increase search coverage.

### Troubleshooting

```markdown
**Issue**: No AI/innovation data found for a competitor
**Cause**: Company may genuinely lack AI features, or may use different terminology
**Solution**: Search for adjacent terms: "automation", "forecasting", "optimization",
"machine learning", "predictive", "smart". Check job postings for data science or ML roles.
If nothing found, mark as "No visible AI signal" with confidence "Confirmed"
(absence of evidence is still evidence when search was thorough).
```

**Why exemplary**: Addresses a real research challenge. Provides alternative search terms. Critically, it explains that "nothing found" IS a valid finding when the search was thorough -- this prevents the agent from fabricating results to fill gaps.

### Data Quality Guidelines

```markdown
| Confidence Level | Criteria | Example Sources |
|---|---|---|
| **Confirmed** | Data from official primary source, verifiable | Annual report, SEC filing, company press release, official website |
| **Estimated** | Data from credible secondary source or reasonable inference | LinkedIn count, Crunchbase, analyst report, industry publication |
| **Unknown** | No reliable data found after thorough search | Mark explicitly -- do not guess or leave blank |
```

**Why exemplary**: Clear 3-tier system with concrete source examples. The "Unknown" row explicitly says "do not guess or leave blank" -- this prevents the agent from filling gaps with hallucinated data.

## Learning Points

1. **Specificity in search strategies produces better agent behavior**: "LinkedIn job postings with 'AI', 'ML', 'data science'" is far more effective than "search for AI hiring"
2. **Pre-structured output templates ensure comparability**: When researching 12+ competitors, consistent table structure makes cross-comparison possible
3. **Confidence levels prevent false certainty**: The 3-tier system forces the agent to distinguish facts from estimates
4. **Troubleshooting anticipates real problems**: Domain-specific troubleshooting (private companies, non-English sources) prevents the agent from getting stuck
5. **Year-agnostic query templates extend prompt lifespan**: Using `[YEAR]` instead of `2026` means the prompt works next year without edits
6. **Separate output files prevent bloat**: Writing to `deep-analysis.md` instead of appending to the main file keeps each artifact focused
7. **Priority-based usage guides execution order**: Grouping competitors by priority (AI-signal first) ensures the most strategically important research happens first

## When to Reference

Use this exemplar when:
- Creating a new research prompt in the `analysis/market/` family
- Building any prompt that requires systematic web research with source attribution
- Designing a data-collection prompt that must produce comparable outputs across subjects
- Looking for examples of effective troubleshooting and data quality sections
- Understanding how to structure "Research Categories" with data-point tables

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-customer-intelligence-exemplar.md` - Customer intelligence research with tiered usage modes (Quick/Standard/Deep)
- `.cursor/exemplars/analysis/market/research-company-history-exemplar.md` - Corporate genealogy research
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` - Financial metrics and growth analysis
- Ticket exemplars under `.cursor/exemplars/ticket/` demonstrate similar structured-output patterns in a different domain

---

**Extracted from**: `.cursor/prompts/analysis/market/research-competitor.prompt.md` (2026-02-15)
**Implements**: `.cursor/templars/analysis/market/structured-web-research-templar.md`
