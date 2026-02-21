---
type: templar
artifact-type: prompt
applies-to: analysis, research, competitive-intelligence, due-diligence, market-research
pattern-name: guided-web-research-prompt
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-company-history.prompt.md
---

# Guided Web Research Prompt Templar

## Pattern Purpose

Provides a reusable structure for prompts that drive **systematic web research** with structured output. Ensures consistent, auditable research across any domain by enforcing research categories, search strategies, output templates, and quality gates.

## Artifact Type

**For**: Prompts (`.prompt.md` files that drive AI-assisted web research)

## When to Use

- Researching companies, technologies, markets, or regulatory landscapes
- Any prompt requiring systematic multi-source web research with structured output
- When research must be auditable (sources, confidence levels, contradictions)
- When output needs visual diagrams (Mermaid) alongside tabular data
- When multiple similar research sessions will be run with different subjects

## Template Structure

```markdown
---
name: [PROMPT_SLUG]
description: "[BRIEF_DESCRIPTION]"
category: [CATEGORY]
tags: [COMMA_SEPARATED_TAGS]
argument-hint: "[ARGUMENT_DESCRIPTION]"
---

# [RESEARCH_TITLE]

[1-2 sentence description of what this research prompt does and what it produces.]

**Pattern**: Guided Discovery Pattern
**Effectiveness**: [WHY_THIS_IS_VALUABLE]
**Use When**: [TRIGGER_CONDITIONS]

---

## Purpose

[2-4 sentences explaining WHY this research matters. What decisions does it inform?
What would be missed without it? Connect to business value.]

---

## Required Context

- **[PRIMARY_SUBJECT]**: [Description of the main research subject]
- **[SUBJECT_FOLDER]** (optional): [Path to existing files for context]
- **[REFERENCE_CONTEXT]**: [Baseline document for comparison/positioning]

---

## Process

**Estimated Time**: [TIME_ESTIMATE] per [SUBJECT_UNIT]

### Step 1: Read Existing Data (if available)

[How to load and leverage existing knowledge before researching.]

### Step 2: Research [CATEGORY_1_NAME]

[Instructions for the first research category. Reference the matching
Research Categories table below.]

### Step 3: Research [CATEGORY_2_NAME]

[Instructions for the next category. Repeat for each category.]

### Step N: Build Visual Diagrams

Synthesize findings into Mermaid diagrams:

**Required diagrams:**
- **[DIAGRAM_1_TYPE]** ([MERMAID_TYPE]): [What it shows]
- **[DIAGRAM_2_TYPE]** ([MERMAID_TYPE]): [What it shows]

### Step N+1: Assess [STRATEGIC_DIMENSION]

[How to synthesize all findings into strategic assessment.
What questions should the assessment answer?]

### Step N+2: Write Output File

Write the research output to: `[OUTPUT_FILE_PATH]`
- Create the folder if it doesn't exist
- Keep as standalone file (don't append to other files)
- Replace existing file if re-running research

---

## Research Categories

### Category 1: [CATEGORY_NAME]

| Data Point | Search Strategy |
|---|---|
| [DATA_POINT_1] | [WHERE_TO_FIND_IT] |
| [DATA_POINT_2] | [WHERE_TO_FIND_IT] |

### Category 2: [CATEGORY_NAME]

| Data Point | Search Strategy |
|---|---|
| [DATA_POINT_1] | [WHERE_TO_FIND_IT] |
| [DATA_POINT_2] | [WHERE_TO_FIND_IT] |

[Repeat for each research category. 4-8 categories is typical.
Each table should have 4-10 data points with concrete search strategies.]

---

## Output Format

Structure the output as a **standalone markdown file** saved to `[OUTPUT_PATH]`:

```markdown
# [OUTPUT_TITLE] - [SUBJECT_NAME]

**Research Date**: YYYY-MM-DD
**Confidence Level**: High / Medium / Low

### [SECTION_1_NAME]

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| [data_point] | [value] | [source] | Confirmed/Estimated/Unknown |

### [SECTION_2_NAME]

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| [data_point] | [value] | [source] | Confirmed/Estimated/Unknown |

[Include Mermaid diagram placeholders where visual synthesis adds value:]

```mermaid
[DIAGRAM_TYPE]
    title [SUBJECT] - [DIAGRAM_DESCRIPTION]
    [DIAGRAM_CONTENT_PLACEHOLDER]
`` `

### [STRATEGIC_ASSESSMENT_SECTION]

[Free-form strategic analysis synthesized from all categories.]
`` `

---

## Quality Criteria

- [ ] All [N] research categories addressed (no sections skipped)
- [ ] Each data point has source attribution
- [ ] Each data point has confidence level (Confirmed/Estimated/Unknown)
- [ ] Mermaid diagrams generated for visual synthesis
- [ ] Contradictions between sources noted explicitly
- [ ] Strategic assessment is evidence-based, not speculative
- [ ] Output saved to correct file path as standalone file
- [ ] [DOMAIN_SPECIFIC_QUALITY_CHECK]

---

## Usage

### [USAGE_SCENARIO_1]

`` `
@[PROMPT_SLUG] [SUBJECT_1] @[CONTEXT_PATH]
`` `

### [USAGE_SCENARIO_2]

`` `
@[PROMPT_SLUG] [SUBJECT_2]
`` `

### [USAGE_SCENARIO_3_FOCUSED]

`` `
@[PROMPT_SLUG] [SUBJECT_3] -- [FOCUS_INSTRUCTION]
`` `

---

## Search Query Templates

**[CATEGORY_1]:**
- `"[SUBJECT]" [KEYWORD_1] [KEYWORD_2]`
- `"[SUBJECT]" "[PHRASE_TO_MATCH]" OR "[ALTERNATIVE_PHRASE]"`
- `site:[AUTHORITATIVE_SITE] "[SUBJECT]"`

**[CATEGORY_2]:**
- `"[SUBJECT]" [KEYWORD_1] [KEYWORD_2] [YEAR_RANGE]`
- `"[SUBJECT]" "[PHRASE_TO_MATCH]"`

[Provide 2-4 query templates per research category.
Use [SUBJECT] as placeholder for the research subject name.]

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read existing data**: Load any existing files for the subject to avoid duplicating known information
2. **Establish baseline**: Confirm current state before researching historical/detailed data
3. **Research systematically**: Work through categories in order, recording findings with sources
4. **Cross-reference sources**: When sources contradict, note discrepancy and pick the most authoritative
5. **Build visual outputs**: Generate Mermaid diagrams to make findings scannable at a glance
6. **Identify patterns**: Once data is collected, look for strategic patterns across categories
7. **Assess implications**: Form evidence-based strategic assessment
8. **Format and output**: Structure findings using the output template and write to the designated file

---

## Related Prompts

- [COMPANION_PROMPT_1] - [How it relates]
- [COMPANION_PROMPT_2] - [How it relates]

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: [DATE]
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
```

## Customization Points

- **`[RESEARCH_CATEGORIES]`**: Define 4-8 research categories as tables with "Data Point | Search Strategy" columns. Each category should have 4-10 specific data points with concrete search strategies.
- **`[OUTPUT_FORMAT]`**: Define the complete markdown template for research output. Always include "Data Point | Value | Source | Confidence" tables for structured data, and Mermaid diagrams for visual synthesis.
- **`[SEARCH_QUERY_TEMPLATES]`**: Provide 2-4 search query templates per category using `[SUBJECT]` as placeholder. Include `site:` queries for authoritative sources.
- **`[MERMAID_DIAGRAMS]`**: Choose diagram types that best visualize the research domain (graph TD for hierarchies, timeline for chronological data, graph LR for flow/relationships).
- **`[REASONING_PROCESS]`**: Customize the AI agent's reasoning steps to match the research domain. Always include: read existing data, research systematically, cross-reference, synthesize, and output.
- **`[QUALITY_CRITERIA]`**: Define 8-12 quality checkboxes. Always require: all categories addressed, source attribution, confidence levels, and evidence-based assessment.

## Key Structural Principles

1. **Research Categories as data tables**: Every data point paired with where to find it. This makes search systematic rather than ad-hoc.
2. **Source + Confidence on every finding**: Baked into the output template, not an afterthought. Enables audit trail.
3. **Visual diagrams alongside tables**: Mermaid diagrams make complex relationships scannable at a glance. Choose diagram types that match your data shape.
4. **Search query templates**: Pre-built queries reduce research friction and ensure consistency across sessions.
5. **Reasoning process for AI**: Explicit step-by-step guidance prevents the agent from skipping categories or producing unstructured output.

## Example Usage

**For competitive intelligence** (corporate history):
See exemplar: `.cursor/exemplars/analysis/market/research-company-history-exemplar.md`

**For technology evaluation** (adapting this templar):
- Research Categories: Architecture, Ecosystem, Performance, Community, Enterprise Features, Licensing
- Output Format: Comparison matrix tables + radar chart description
- Mermaid Diagrams: Component diagram, adoption timeline
- Quality: Coverage of all evaluation criteria, benchmark data cited

**For market landscape** (adapting this templar):
- Research Categories: Market Size, Key Players, Regulatory Environment, Technology Trends, Customer Segments
- Output Format: Market map + player profiles
- Mermaid Diagrams: Market segmentation diagram, competitive positioning map
- Quality: Market sizing methodology documented, multiple analyst sources cross-referenced

## Related Templars

- Ticket templars (`.cursor/templars/ticket/`) - Different domain, but similar structured-output pattern
- Prompt collection validation templar - Similar quality-gate pattern

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-company-history-exemplar.md` - Full implementation showing this pattern applied to corporate genealogy research
