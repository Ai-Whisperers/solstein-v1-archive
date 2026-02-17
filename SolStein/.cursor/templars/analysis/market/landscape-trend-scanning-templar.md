---
type: templar
artifact-type: prompt
applies-to: analysis, research, trend-scanning, regulatory-landscape, competitive-dynamics, market-forces
pattern-name: landscape-trend-scanning-with-impact-scoring
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-market-trends.prompt.md
---

# Landscape Trend Scanning with Impact Scoring - Templar

## Pattern Purpose

Provides a reusable framework for prompts that scan **macro-level landscape forces** (regulatory, technology, market structure, customer behavior) rather than individual entities, score each identified trend with a multi-dimensional rubric, and map trends to downstream consuming artifacts. The key distinction from per-entity research templars: this pattern researches **forces that affect all entities** and produces **scored trend inventories** with **downstream feed mapping**.

## Artifact Type

**For**: Prompts (analysis, research, trend scanning, landscape assessment)

## When to Use

- Scanning a domain for regulatory, technology, or market forces that affect competitive dynamics
- Producing scored trend inventories with Impact, Timeline, Subject-Specific Impact, and Confidence ratings
- Building regulatory or milestone timelines (Mermaid gantt) from institutional sources
- Connecting trend research to downstream dashboards, scenarios, or risk assessments
- Any prompt where the output is a **trend landscape file** (not per-entity, but per-force)

## Relationship to Other Analysis Templars

```text
Per-Entity Research (existing)          Landscape Scanning (this templar)
  structured-web-research-templar  ──┐
  multi-dimensional-scorecard      ──┤  (different axis: entities vs forces)
  systematic-mapping-research      ──┘
                                        landscape-trend-scanning-templar
                                              │
                                              ▼
  multi-source-synthesis-dashboard  ◄── (consumes landscape + entity data)
```

## Template Structure

### Frontmatter

```yaml
---
name: [PROMPT_SLUG]
description: "Please research [LANDSCAPE_DOMAIN] trends, [FORCE_TYPES], and [CHANGE_DRIVERS] in [SCOPE] that shape [DYNAMICS_TARGET]"
category: analysis
tags: [DOMAIN_TAGS]
argument-hint: "[ARGUMENT_DESCRIPTION_OR_NONE]"
agent: cursor-agent
model: GPT-4
tools:
  - web/*
  - search/codebase
  - fileSystem
---
```

### Section 1: Title and Purpose

```markdown
# Research [LANDSCAPE_DOMAIN] Trends & [SUPPLEMENTARY_DIMENSION]

Please perform a structured research session on [LANDSCAPE_DOMAIN] trends,
[FORCE_TYPES], and [CHANGE_DRIVERS] in [SCOPE]. This prompt captures
[SCOPE]-wide forces that shape [DYNAMICS_TARGET] -- forces that no
single [ENTITY_TYPE] prompt can cover. Output is a standalone
`[OUTPUT_FILE_PATH]` with scored trends, [VISUAL_TIMELINE_TYPE],
and [DOWNSTREAM_MAPPING_TYPE].

**Pattern**: Guided Analysis Pattern
**Effectiveness**: [EFFECTIVENESS_DESCRIPTION]
**Use When**: [TRIGGER_CONDITION]
```

### Section 2: Purpose

```markdown
## Purpose

Current [DOMAIN] research prompts focus on individual [ENTITY_TYPE_PLURAL].
No prompt captures the [SCOPE]-wide forces that shape [DYNAMICS_TARGET]:

- **[FORCE_CATEGORY_1]** [WHY_IT_MATTERS]
- **[FORCE_CATEGORY_2]** [WHY_IT_MATTERS]
- **[FORCE_CATEGORY_3]** [WHY_IT_MATTERS]
- **[FORCE_CATEGORY_N]** [WHY_IT_MATTERS]

This data feeds directly into:
- [DOWNSTREAM_ARTIFACT_1]
- [DOWNSTREAM_ARTIFACT_2]
- [DOWNSTREAM_ARTIFACT_N]
```

### Section 3: Required Context

```markdown
## Required Context

- **[SUBJECT_POSITIONING]**: Reference [POSITIONING_FILE] for [SUBJECT]'s
  current capabilities and vulnerabilities
- **[EXISTING_DATA]**: Reference [EXISTING_DATA_FOLDER] for context
  on individual [ENTITY_TYPE_PLURAL]
- **[DOWNSTREAM_SPEC]**: Reference [DOWNSTREAM_SPEC_FILE] for how
  trends feed into [DOWNSTREAM_OUTPUT]
```

### Section 4: Usage Modes

This is a key structural innovation -- allow multiple research depths:

```markdown
## Usage Modes

### Full Research Mode (Default)

Complete [N]-category research session for initial build or [REFRESH_CYCLE] refresh:

`` `
@[PROMPT_SLUG]
`` `

**Time**: [FULL_TIME_ESTIMATE] | **Scope**: All [N] categories |
**Output**: Full `[OUTPUT_FILENAME]`

### Quick Refresh Mode

Targeted update of 1-2 categories after specific events:

`` `
@[PROMPT_SLUG] -- quick refresh Category [X] after [TRIGGERING_EVENT]
`` `

**Time**: [QUICK_TIME_ESTIMATE] | **Scope**: Specified categories only |
**Output**: Updates relevant sections, preserves unchanged categories

### [PERIODIC_REVIEW] Mode

Re-score existing trends and add newly identified ones:

`` `
@[PROMPT_SLUG] -- [PERIODIC_REVIEW_SLUG], re-score existing trends and add new
`` `

**Time**: [REVIEW_TIME_ESTIMATE] | **Scope**: All [N] categories,
focus on changes since last research date |
**Output**: Updated file with change annotations
```

### Section 5: Process Steps

```markdown
## Process

### Step 1: Read [SUBJECT] Positioning
Read [POSITIONING_FILE] to understand [SUBJECT]'s current capabilities,
position, and vulnerabilities. Every trend must be assessed through the
lens of "what does this mean for [SUBJECT] specifically?"

### Step 2: Web Research by Category
For each of the [N] research categories below, perform targeted web
searches. Time allocation guidance:

| Category | Est. Time | Complexity |
|---|---|---|
| [CATEGORY_1] | [TIME] | [COMPLEXITY_NOTE] |
| [CATEGORY_N] | [TIME] | [COMPLEXITY_NOTE] |

Prioritize these source types:
- [SOURCE_TYPE_1]
- [SOURCE_TYPE_N]

### Step 3: Score Each Trend
For every trend identified, assign:
- **Impact Score** ([SCALE]): [IMPACT_DEFINITION]
- **Timeline Horizon**: [TIMELINE_BANDS]
- **[SUBJECT] Impact**: [SUBJECT_IMPACT_DEFINITION]
- **Confidence**: [CONFIDENCE_DEFINITION]

### Step 4: Build [VISUAL_TIMELINE_TYPE]
Create a Mermaid [DIAGRAM_TYPE] plotting key milestones chronologically.
Include [MILESTONE_TYPES].

### Step 5: Map to Downstream Feeds
For each trend, identify which downstream [ARTIFACT_TYPE](s) it feeds:
- **[DOWNSTREAM_1]**: Trends with [CRITERIA_1]
- **[DOWNSTREAM_N]**: Trends with [CRITERIA_N]

### Step 6: Write [OUTPUT_TYPE] File
Write output to `[OUTPUT_FILE_PATH]` as a standalone file. If the file
already exists, replace it with the updated version.
```

### Section 6: Research Categories

Repeat for each research dimension (4-6 categories typical for landscape scanning):

```markdown
## Research Categories

### Category [N]: [CATEGORY_NAME]

Track [WHAT_THIS_CATEGORY_COVERS].

| Research Question | Search Strategy |
|---|---|
| [QUESTION_1] | [SOURCES_AND_APPROACH] |
| [QUESTION_N] | [SOURCES_AND_APPROACH] |

**[SUBJECT]-Specific Focus**: [HOW_THIS_CATEGORY_SPECIFICALLY_AFFECTS_SUBJECT]
```

### Section 7: Impact Scoring Rubric

```markdown
## Impact Scoring Rubric

### Impact Score ([SCALE])

| Score | Definition | Example |
|---|---|---|
| [HIGHEST] | [TRANSFORMATIVE_DEFINITION] | [CONCRETE_EXAMPLE] |
| [HIGH] | [HIGH_IMPACT_DEFINITION] | [CONCRETE_EXAMPLE] |
| [MODERATE] | [MODERATE_DEFINITION] | [CONCRETE_EXAMPLE] |
| [LOW] | [LOW_DEFINITION] | [CONCRETE_EXAMPLE] |
| [MINIMAL] | [MINIMAL_DEFINITION] | [CONCRETE_EXAMPLE] |

### Timeline Horizon

| Horizon | Definition | Planning Implication |
|---|---|---|
| [NEAR] | [NEAR_DEFINITION] | [NEAR_PLANNING] |
| [MEDIUM] | [MEDIUM_DEFINITION] | [MEDIUM_PLANNING] |
| [FAR] | [FAR_DEFINITION] | [FAR_PLANNING] |

### [SUBJECT] Impact Assessment

| Rating | Definition |
|---|---|
| Positive | [POSITIVE_DEFINITION] |
| Neutral | [NEUTRAL_DEFINITION] |
| Negative | [NEGATIVE_DEFINITION] |

### Confidence Level

| Level | Criteria | Usage |
|---|---|---|
| Confirmed | [CONFIRMED_CRITERIA] | [CONFIRMED_USAGE] |
| Estimated | [ESTIMATED_CRITERIA] | [ESTIMATED_USAGE] |
| Speculative | [SPECULATIVE_CRITERIA] | [SPECULATIVE_USAGE] |
```

### Section 8: Output Format

```markdown
## Output Format

Structure output as a **standalone markdown file** saved to `[OUTPUT_FILE_PATH]`:

`` `markdown
# [LANDSCAPE_TITLE]

**Research Date**: YYYY-MM-DD
**Research Mode**: Full / Quick Refresh / [Periodic Review]
**Confidence Level**: High / Medium / Low
**Data Sources**: [count] sources consulted

---

## Executive Summary

[3-5 sentences capturing the most critical trends and their combined
implications for [SUBJECT].]

---

## [VISUAL_TIMELINE_TITLE]

`` `mermaid
[DIAGRAM_TYPE]
    title [TIMELINE_TITLE]
    [TIMELINE_CONTENT_PLACEHOLDER]
`` `

---

## [N]. [CATEGORY_NAME]

| Trend | Impact ([SCALE]) | Timeline | [SUBJECT] Impact | Confidence | Downstream Feed | Source |
|---|---|---|---|---|---|---|
| [Trend] | [score] | [horizon] | [rating]: [explanation] | [level] | [feeds] | [source] |

### Analysis

[2-3 paragraphs synthesising the category, not just repeating the table.]

---

[REPEAT per category]

---

## Downstream Feed Mapping

### [DOWNSTREAM_ARTIFACT_1]

| Trend | Category | Impact | Timeline | [MAPPING_DIMENSION] |
|---|---|---|---|---|

### [DOWNSTREAM_ARTIFACT_N]

| Trend | Category | [ARTIFACT_SPECIFIC_COLUMNS] |
|---|---|---|

---

## Quality Assessment

- Data completeness: [X/N categories with substantive data]
- Source quality: [primary/secondary/mixed]
- Key data gaps: [what couldn't be found and why]
- Recommended follow-up: [specific research to fill gaps]
`` `
```

### Section 9: Search Query Templates

```markdown
## Search Query Templates

Use current year. Replace `[YEAR]` with current, `[YEAR-1]` with previous.

| Category | Query Templates |
|---|---|
| [CATEGORY_1] | `[QUERY_1]`, `[QUERY_2]` |
| [CATEGORY_N] | `[QUERY_1]`, `[QUERY_2]` |
```

### Section 10: Reasoning Process

```markdown
## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read [SUBJECT] positioning**: Load [POSITIONING_FILE]
2. **Scan existing [ENTITY_TYPE] data**: Skim [DATA_FOLDER] for context
3. **Determine mode**: Full / Quick Refresh / [Periodic Review]
4. **Plan search strategy**: For each in-scope category, formulate queries
5. **Execute searches systematically**: Work through categories in order
6. **Score each trend**: Apply the scoring rubric consistently
7. **Assess [SUBJECT] impact**: Evaluate through [SUBJECT]-specific lens
8. **Build [VISUAL_TIMELINE]**: Extract concrete dates from sources
9. **Map to downstream feeds**: Classify each trend by downstream artifact
10. **Write executive summary**: Distill most critical trends
11. **Self-review before finalizing**: Verify completeness, scoring
    consistency, and analysis depth
12. **Format and write**: Structure findings and save to [OUTPUT_FILE_PATH]
```

### Section 11: Quality Criteria

```markdown
## Quality Criteria

### Critical (must pass)

- [ ] All [N] research categories addressed with trend tables
- [ ] Each category has [MIN]-[MAX] identified trends minimum
- [ ] Every trend has all scoring columns filled
- [ ] Every trend has source attribution
- [ ] [VISUAL_TIMELINE] included with real milestone dates
- [ ] Output saved to `[OUTPUT_FILE_PATH]`

### Important (should pass)

- [ ] Downstream feed mapping completed for all [DOWNSTREAM_ARTIFACTS]
- [ ] Executive summary captures the [TOP_N] most critical trends
- [ ] [SUBJECT]-specific analysis present in each category
- [ ] Analysis sections provide synthesis beyond table repetition
- [ ] Confidence levels appropriately distributed

### Nice-to-have

- [ ] Research date and source count in file header
- [ ] Per-category data gap notes where sources were limited
- [ ] Cross-category convergence patterns identified
```

## Customisation Points

| Placeholder | Guidance |
|---|---|
| `[LANDSCAPE_DOMAIN]` | The macro domain being scanned (energy regulation, fintech compliance, healthcare IT, etc.) |
| `[FORCE_CATEGORIES]` | The 4-6 categories of landscape forces (regulatory, technology, market structure, customer behavior, etc.) |
| `[SUBJECT]` | The entity whose perspective anchors the analysis (our company, our product, our market position) |
| `[SCOPE]` | Geographic or market scope (European, North American, global, sector-specific) |
| `[SCORING_RUBRIC]` | Impact scale (1-5 or 1-10), timeline bands (Near/Medium/Far), subject impact (Positive/Neutral/Negative), confidence levels |
| `[VISUAL_TIMELINE]` | Mermaid diagram type for regulatory/milestone timeline (gantt, timeline) |
| `[DOWNSTREAM_ARTIFACTS]` | Dashboard sheets, scenario models, or risk assessments that consume the trend data |
| `[USAGE_MODES]` | Research depth options (Full, Quick Refresh, Periodic Review) with time estimates |
| `[SOURCE_HIERARCHY]` | Ranked list of source types from most to least authoritative for this domain |
| `[RESEARCH_QUESTION_TABLES]` | Per-category tables of Research Question + Search Strategy pairs |

## Key Design Decisions

1. **Forces, not entities**: This templar scans landscape-level forces (trends, regulations, shifts) -- fundamentally different from per-entity research templars
2. **Multi-dimensional trend scoring**: Every trend gets Impact + Timeline + Subject Impact + Confidence, enabling prioritisation and filtering
3. **Usage modes**: Full/Quick Refresh/Periodic Review modes allow the same prompt to serve different research depths without duplication
4. **Downstream feed mapping**: Explicit connection from each trend to the dashboards/artifacts that consume it -- prevents research from becoming disconnected
5. **Subject-specific lens**: Every category includes a "what does this mean for US specifically" assessment, grounding abstract trends in concrete impact
6. **3-tier quality criteria**: Critical/Important/Nice-to-have prevents perfectionism while ensuring minimum quality bar
7. **Regulatory timeline via Mermaid gantt**: Visual synthesis of key milestone dates in a format that renders directly in markdown

## Example Usage

**For European energy software market** (see exemplar: `.cursor/exemplars/analysis/market/research-market-trends-exemplar.md`):
- Landscape: EU energy regulation, protocol convergence, technology shifts, market structure, customer behavior
- Subject: Eneve (NL-focused, EDSN specialist, on-premise)
- Scope: European energy software
- Scoring: Impact 1-5, Timeline Near/Medium/Far
- Visual: Mermaid gantt of EU regulatory milestones
- Downstream: FD-015 Threat Timeline, FD-019 Scenarios, FD-020 Portfolio Risk

**For fintech regulatory landscape**:
- Landscape: Payment regulation (PSD3, instant payments), open banking mandates, AML/KYC evolution, digital currency frameworks
- Subject: Our payment platform
- Scope: EU/UK fintech
- Scoring: Impact 1-5, Timeline Near/Medium/Far
- Visual: Mermaid gantt of payment regulation milestones
- Downstream: Risk register, product roadmap, compliance tracker

**For healthcare IT compliance landscape**:
- Landscape: EHR interoperability mandates, data privacy (GDPR health), AI-in-diagnostics regulation, telehealth frameworks
- Subject: Our EHR platform
- Scope: EU/US healthcare
- Scoring: Impact 1-5, Timeline Near/Medium/Far
- Visual: Mermaid gantt of compliance deadlines
- Downstream: Product risk matrix, certification roadmap

## Related Templars

- `.cursor/templars/analysis/market/structured-web-research-templar.md` -- Per-entity research; this templar researches forces instead
- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- Per-entity scoring; this templar scores trends
- `.cursor/templars/analysis/market/multi-source-synthesis-dashboard-templar.md` -- Downstream consumer; aggregates entity + landscape data
- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- Generic research scaffold; this templar specialises for landscape scanning

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-market-trends-exemplar.md` -- Full implementation showing this pattern applied to European energy software market trends

---

**Extracted From**: `.cursor/prompts/analysis/market/research-market-trends.prompt.md`
**Created**: 2026-02-17
