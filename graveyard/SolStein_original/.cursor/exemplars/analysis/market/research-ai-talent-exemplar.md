---
type: exemplar
artifact-type: prompt
demonstrates: multi-dimensional research scorecard pattern + structured web research pattern applied to human-capital intelligence
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-ai-talent.prompt.md
implements:
  - .cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md
  - .cursor/templars/analysis/market/structured-web-research-templar.md
  - .cursor/templars/analysis/market/guided-research-prompt-templar.md
---

# Research AI Talent Prompt - Exemplar

## Artifact Type

**Type**: Prompt (`.prompt.md`)

## Why This is Exemplary

This prompt demonstrates best-in-class application of the multi-dimensional research scorecard and structured web research patterns to a sensitive, people-focused research domain (AI talent intelligence). It introduces several novel elements not present in other prompts in the research family, making it a valuable reference for creating similar human-capital or sensitive-domain research prompts.

## Key Quality Elements

1. **Ethical Guardrails Section**: First prompt in the research family to include explicit ethical boundary-setting. Lists 12 concrete rules (6 allowed, 6 prohibited) with a safety default ("If in doubt, skip it"). This pattern is essential for any research touching personal or sensitive data.

2. **4-Tier Data Confidence Framework**: Extends the family standard of 3 tiers (Confirmed/Estimated/Unknown) to 4 by adding "Speculated" -- for single weak signals or indirect inference. Includes conflict resolution guidance ("When sources disagree, state both values and note the discrepancy"). Applicable to any research domain with variable data quality.

3. **Dual Scoring Rubrics with Weighted Inputs**: Two independent 1-10 scoring dimensions (Talent Concentration Risk, Acqui-Hire Attractiveness) with 5-level rubric tables and 5 explicitly named scoring inputs for the second dimension. More rigorous than single-dimension scoring in other prompts.

4. **Key-Person Vulnerability Analysis**: Novel "What Happens If Key People Leave" table (Person/Role | Impact If Lost | Replacement Difficulty | Mitigation). Unique analytical output not seen in other research prompts. Directly actionable for strategic decision-making.

5. **Usage Modes (Quick vs Full)**: Formalizes two execution modes with explicit scope differences (Quick: Categories 1-2 only, ~15-20 min; Full: all 5 categories, ~45-60 min). First prompt in the family to offer tiered execution depth.

6. **Archetype-Spanning Few-Shot Examples**: Three examples covering the data-availability spectrum mapped to company archetypes (Rocket with deep AI bench, AI-first Startup, Legacy Dinosaur). Each shows different scoring patterns, output density, and data-gap handling.

7. **Comprehensive Search Query Templates**: 5 categories of pre-built search queries (AI Leadership, Team Composition, Publications & Patents, Key Hires, Open Source) with site-specific operators and year placeholders.

8. **5-Category Research Framework**: 5 research categories with "Data Point | Search Strategy" tables totalling 40+ specific data points. Categories progress logically: Leadership -> Team Size -> Key Hires -> Publications/Patents -> Infrastructure Signals.

9. **Subject-Type Decision Tree**: Explicit reasoning tree classifying targets (Rocket >100 employees, Startup <50, Dinosaur/Steady) to calibrate research expectations and search approach.

10. **NUCLEAR Classification Handling**: Demonstrates how to mark sensitive research output for restricted audiences ("CTO/Board eyes only") and carry CONFIDENTIAL headers into the output template.

## Patterns Demonstrated

### Primary: Multi-Dimensional Research Scorecard (from `multi-dimensional-research-scorecard-templar.md`)

- Dual scoring dimensions with 5-level rubrics
- Composite scorecard table
- Classification thresholds with named bands
- Evidence-based scoring ("Use the rubric, not gut feeling")

### Secondary: Structured Web Research (from `structured-web-research-templar.md`)

- Research categories with "Data Point | Search Strategy" tables
- Output format with "Data Point | Value | Source | Confidence" tables
- 4-tier confidence system (extended from standard 3-tier)
- Search query templates with year-agnostic placeholders
- Troubleshooting section for domain-specific challenges
- Separate output file per subject

### Tertiary: Guided Research Prompt (from `guided-research-prompt-templar.md`)

- Step-by-step process (9 steps)
- Read existing data first
- Read baseline reference second
- Reasoning process for AI agent
- Self-correction step before writing output

## Novel Elements Worth Adopting

These elements are unique to this prompt and could be adopted by other research prompts:

| Novel Element | Where in Prompt | Reuse Potential |
| --- | --- | --- |
| Ethical Guardrails | Dedicated section after Purpose | High -- any people-focused or sensitive research |
| 4-Tier Confidence (adds "Speculated") | Data Confidence Framework section | Medium -- useful when single weak signals are common |
| Key-Person Vulnerability Analysis | Output template section | Medium -- any assessment of organizational resilience |
| Usage Modes (Quick/Full) | Usage Modes section | High -- any time-intensive research that benefits from tiered depth |
| NUCLEAR/Confidential marking | Header + Output template | Medium -- any research with audience restrictions |

## Full Exemplar Content

Below is the complete prompt as it exists in production. This is the reference implementation of multi-dimensional scoring + structured web research patterns applied to talent intelligence.

---

### Frontmatter

```yaml
---
name: research-ai-talent
description: "Please perform a deep AI talent intelligence research on an energy software competitor"
category: analysis
tags: competition, ai, talent, acqui-hire, personnel, leadership, nuclear
argument-hint: "Company name and path to company folder (e.g., Volue ASA @tickets/COMPETITION/volue/)"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
  - .cursor/rules/prompts/prompt-registry-integration-rule.mdc
---
```

### Structure Overview

The prompt is organized into these major sections (with approximate line counts):

| Section | Lines | Purpose |
| --- | --- | --- |
| Title + Purpose | ~40 | Context and strategic value |
| Ethical Guardrails | ~20 | Boundary-setting for sensitive research |
| Required Context | ~10 | Inputs and optional parameters |
| Reasoning Process | ~25 | Subject-type decision tree + research approach |
| Process (9 steps) | ~70 | Step-by-step execution instructions |
| Usage Modes | ~20 | Quick vs Full execution depth |
| Research Categories (5) | ~60 | Data Point / Search Strategy tables |
| Talent Scorecard Criteria | ~30 | Dual scoring rubrics (1-10) |
| Data Confidence Framework | ~15 | 4-tier confidence definitions |
| Search Query Templates | ~25 | Pre-built search queries by category |
| Output Format | ~100 | Complete markdown template for output file |
| Few-Shot Examples (3) | ~65 | Rocket, Startup, Dinosaur archetypes |
| Troubleshooting (5) | ~30 | Common challenges with solutions |
| Quality Criteria | ~15 | 14-item validation checklist |

### Exemplary Sections (Highlighted)

**Ethical Guardrails** (novel pattern):

```markdown
## Ethical Guardrails

This research MUST stay within public information boundaries:

- LinkedIn public profiles and job postings only
- Published conference papers, patents, and academic citations (public record)
- Press releases and company announcements
- GitHub/open-source contributions (public repositories)
- Company careers pages and job descriptions
- Conference speaker lists and presentation recordings
- NO scraping private data
- NO purchasing data broker lists
- NO social engineering or pretexting
- NO salary data or compensation estimates
- NO personal contact details (email, phone, home address)
- NO information from private/locked social media profiles

**If in doubt about a data source, skip it.**
```

**4-Tier Confidence Framework** (extends standard 3-tier):

```markdown
| Level | Definition | When to Use |
| --- | --- | --- |
| **Confirmed** | Directly stated in an authoritative source | Official announcements, company About page |
| **Estimated** | Inferred from multiple signals that agree | Team size from LinkedIn + job posting volume |
| **Speculated** | Based on a single weak signal or indirect inference | One blog post mention, inferred from tech stack |
| **Unknown** | No data found despite searching | Always prefer "Unknown" over guessing |
```

**Key-Person Vulnerability Table** (novel output element):

```markdown
## What Happens If Key People Leave

| Person/Role | Impact If Lost | Replacement Difficulty | Mitigation |
| --- | --- | --- | --- |
| [Name/Role] | [impact on AI capability] | [Easy/Medium/Hard/Critical] | [what company could do] |
```

**Dual Scoring with Weighted Inputs** (Acqui-Hire dimension):

```markdown
**Scoring inputs** (weight approximately equally):
- **Talent quality**: Leadership caliber, publication record, industry recognition
- **Team cohesion**: How long has team worked together, cultural fit signals
- **Company vulnerability**: Growth classification (Dinosaur > Steady > Riser > Rocket)
- **Acquisition cost**: Revenue, funding, valuation relative to talent value
- **Domain specificity**: Energy/commodity domain expertise (harder to replicate)
```

**Usage Modes** (tiered execution depth):

```markdown
### Quick Mode (15-20 min)
Focus on Categories 1-2 only.
**Covers**: AI leadership + team size estimate + scores
**Skips**: Key hires tracking, publications/patents, infrastructure signals

### Full Mode (45-60 min, default)
Complete deep-dive across all 5 categories.
**Covers**: All 5 research categories, all output sections
```

## Learning Points

- **Ethical guardrails belong in the prompt, not just in documentation** -- when research touches people data, explicit boundaries prevent scope creep and protect the organization.
- **4-tier confidence works better than 3-tier for scarce-data domains** -- the "Speculated" tier acknowledges weak signals without overstating certainty.
- **Key-person vulnerability analysis transforms talent research from descriptive to strategic** -- moves beyond "who works there" to "what happens if they leave."
- **Usage modes reduce prompt abandonment** -- when a 45-minute research session isn't feasible, a 15-minute Quick mode keeps the prompt useful.
- **Subject-type decision trees calibrate expectations** -- telling the agent upfront that a Dinosaur may have zero AI titles prevents wasted search effort and honest "Unknown" reporting.

## When to Reference

Use this exemplar when:
- Creating a new research prompt that touches sensitive or people-focused data
- Adding ethical guardrails to any existing research prompt
- Implementing a 4-tier confidence framework
- Adding key-person or organizational vulnerability analysis to a research output
- Designing tiered execution modes (quick/full) for any time-intensive prompt
- Building dual or multi-dimensional scoring rubrics with explicit weighted inputs

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-competitor-exemplar.md` -- Structured web research pattern applied to broader competitive intelligence
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` -- Multi-dimensional scorecard pattern applied to financial/growth analysis
- `.cursor/exemplars/analysis/market/research-company-history-exemplar.md` -- Guided research pattern applied to corporate genealogy
- `.cursor/exemplars/analysis/market/research-protocols-exemplar.md` -- Structured research applied to energy protocol analysis

## Related Templars

- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- Scoring rubric pattern this prompt implements
- `.cursor/templars/analysis/market/structured-web-research-templar.md` -- Web research pattern this prompt implements
- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- General guided research pattern

---

**Extracted From**: `.cursor/prompts/analysis/market/research-ai-talent.prompt.md`
**Created**: 2026-02-17
**Context**: Templar/exemplar extraction for market research prompt family
