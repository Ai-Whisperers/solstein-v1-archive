---
type: templar
artifact-type: prompt
applies-to: analysis, research, market-intelligence, competitive-intelligence
pattern-name: structured-web-research
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-competitor.prompt.md
---

# Structured Web Research Prompt Templar

## Pattern Purpose

Provides a reusable scaffold for creating prompts that drive systematic web research sessions. The pattern ensures consistent, comparable, source-attributed research outputs across any research domain.

## Artifact Type

**For**: Prompts (`.cursor/prompts/**/*.prompt.md`)

## When to Use

- Creating a new research prompt that requires structured web research across multiple categories
- Building a research prompt that must produce source-attributed, confidence-rated findings
- Adding a new dimension to an existing research family (e.g., a new competitor analysis angle)
- Any prompt where the agent must systematically search the web, collect data points, and synthesize findings

## Template Structure

```markdown
---
name: [PROMPT-SLUG]
description: "[ONE-LINE-PURPOSE]"
category: [CATEGORY]
tags: [COMMA-SEPARATED-TAGS]
argument-hint: "[ARGUMENT-DESCRIPTION]"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# [RESEARCH-TITLE] - [QUALIFIER]

[1-2 sentence description of what this research prompt does and what output it produces.]

**Pattern**: Guided Analysis Pattern
**Effectiveness**: [EFFECTIVENESS-DESCRIPTION]
**Use When**: [WHEN-TO-USE]

---

## Purpose

[2-4 sentences explaining WHY this research matters and what decisions it enables.]

---

## Required Context

- **[PRIMARY-INPUT]**: [Description] (e.g., "Company Name")
- **[SECONDARY-INPUT]**: [Description] (e.g., "Path to existing data folder")
- **[BASELINE-REFERENCE]**: [Description] (e.g., "Reference file for comparison context")

---

## Process

**Estimated Time**: [TIME-RANGE] per [UNIT] ([VARIATION-NOTES])

### Step 1: Read Existing Data

Read any existing files in [CONTEXT-FOLDER] to understand current state of knowledge. Note data gaps or unverified claims.

### Step 2: Read Baseline Reference

Read [BASELINE-FILE] to refresh understanding of comparison context and positioning.

### Step 3: Web Research by Category

For each research category below, perform targeted web searches. Prioritize:
- [SOURCE-PRIORITY-1] (e.g., official company websites, press releases)
- [SOURCE-PRIORITY-2] (e.g., industry publications)
- [SOURCE-PRIORITY-3] (e.g., job postings, conference appearances)

### Step 4: Synthesize Findings

Organize findings into the structured output template. For each data point:
- Record the finding with source attribution
- Mark confidence as "Confirmed", "Estimated", or "Unknown"
- Note contradictions between sources
- Prefer primary sources over secondary sources

### Step 5: [SYNTHESIS-STEP]

[Domain-specific synthesis, e.g., threat assessment, pattern analysis, strategic implications.]

### Step 6: Write Output File

Write the output to a **separate file**:
- **File path**: `[OUTPUT-PATH]/[SLUG]/[OUTPUT-FILENAME].md`
- Create the folder if it doesn't exist
- Do NOT append to existing files -- keep research outputs in dedicated files
- Replace if the file already exists

### Step 7: Update Status Tracking

Update [STATUS-TRACKING-FILE] to reflect research completion for this subject.

---

## Research Categories

### Category 1: [CATEGORY-NAME]

[Brief description of what this category covers.]

| Data Point | Search Strategy |
|---|---|
| [DATA-POINT-1] | [WHERE-TO-SEARCH] |
| [DATA-POINT-2] | [WHERE-TO-SEARCH] |
| [DATA-POINT-3] | [WHERE-TO-SEARCH] |

### Category 2: [CATEGORY-NAME]

| Data Point | Search Strategy |
|---|---|
| [DATA-POINT-1] | [WHERE-TO-SEARCH] |
| [DATA-POINT-2] | [WHERE-TO-SEARCH] |

[REPEAT for each research category. Typical count: 4-8 categories.]

---

## Output Format

Structure the output as a **standalone markdown file** saved to `[OUTPUT-PATH]`:

```markdown
# [OUTPUT-TITLE] - [SUBJECT-NAME]

**Research Date**: YYYY-MM-DD
**Confidence Level**: High / Medium / Low (based on data availability)

### [CATEGORY-1-NAME]

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| [data point] | [value] | [source] | Confirmed/Estimated/Unknown |

### [CATEGORY-2-NAME]

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| [data point] | [value] | [source] | Confirmed/Estimated/Unknown |

[REPEAT for each category]

### [SYNTHESIS-SECTION-NAME]

[Structured synthesis output specific to this research domain.]
```

---

## Quality Criteria

- [ ] All research categories addressed (no sections skipped)
- [ ] Each data point has a source attribution
- [ ] Each data point has a confidence level (Confirmed/Estimated/Unknown)
- [ ] [SYNTHESIS-SECTION] is evidence-based, not speculative
- [ ] Existing data verified or corrected
- [ ] [DOMAIN-SPECIFIC-QUALITY-CHECK]
- [ ] Output saved to [OUTPUT-PATH] (standalone file)
- [ ] Status tracking updated

---

## Usage

### [PRIORITY-GROUP-1]

```
@[PROMPT-SLUG] [ARGUMENT-1] [CONTEXT-PATH-1]
```

### [PRIORITY-GROUP-2]

```
@[PROMPT-SLUG] [ARGUMENT-2] [CONTEXT-PATH-2]
```

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read existing data**: Load any existing files to understand current knowledge state
2. **Read baseline**: Load comparison/positioning context
3. **Plan search strategy**: For each category, formulate 2-3 specific web queries
4. **Execute searches systematically**: Work through categories in order, recording findings with sources
5. **Cross-reference data**: Note discrepancies between sources, pick the most authoritative
6. **Synthesize**: Form evidence-based conclusions from all collected data
7. **Format and write**: Structure findings in the output template and write to file
8. **Update status**: Mark research as complete in tracking file

---

## Search Query Templates

Use these as starting points. Replace `[YEAR]` with current year, `[YEAR-1]`/`[YEAR-2]` with previous years.

**[CATEGORY-1]**:
- `"[SUBJECT]" [KEYWORD-1] [KEYWORD-2] [YEAR-1] [YEAR]`
- `"[SUBJECT]" [KEYWORD-3]`

**[CATEGORY-2]**:
- `"[SUBJECT]" [KEYWORD-4] [KEYWORD-5]`

[REPEAT for each category]

---

## Troubleshooting

**Issue**: [COMMON-PROBLEM-1]
**Cause**: [ROOT-CAUSE]
**Solution**: [SPECIFIC-RESOLUTION]. Mark affected data points as "[CONFIDENCE-LEVEL]" and note the limitation.

**Issue**: [COMMON-PROBLEM-2]
**Cause**: [ROOT-CAUSE]
**Solution**: [SPECIFIC-RESOLUTION].

---

## Data Quality Guidelines

| Confidence Level | Criteria | Example Sources |
|---|---|---|
| **Confirmed** | Data from official primary source, verifiable | [PRIMARY-SOURCE-EXAMPLES] |
| **Estimated** | Data from credible secondary source or reasonable inference | [SECONDARY-SOURCE-EXAMPLES] |
| **Unknown** | No reliable data found after thorough search | Mark explicitly -- do not guess or leave blank |

**Handling sparse data**: If fewer than 50% of data points in a category can be filled, add a note explaining why and what additional research methods could help.

---

## Related Prompts

- [RELATED-PROMPT-1]
- [RELATED-PROMPT-2]

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: [DATE]
**Context**: [RESEARCH-CONTEXT]
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
```

## Customization Points

| Placeholder | Guidance |
|---|---|
| `[PROMPT-SLUG]` | Hyphenated lowercase name for slash command (e.g., `research-competitor`) |
| `[ONE-LINE-PURPOSE]` | Quoted string for frontmatter description field |
| `[RESEARCH-TITLE]` | H1 title describing the research focus |
| `[PRIMARY-INPUT]` | Main subject to research (company, product, market, etc.) |
| `[SECONDARY-INPUT]` | Supporting context (folder path, existing data, etc.) |
| `[BASELINE-REFERENCE]` | File providing comparison baseline (README, positioning doc) |
| `[CATEGORY-NAME]` | Name for each research category (4-8 categories typical) |
| `[DATA-POINT]` / `[SEARCH-STRATEGY]` | Specific data items and where to find them |
| `[OUTPUT-PATH]` | Where the research output file should be saved |
| `[OUTPUT-FILENAME]` | Name of the output file (e.g., `deep-analysis.md`, `corporate-history.md`) |
| `[SYNTHESIS-SECTION]` | Domain-specific synthesis section (threat assessment, strategic implications, etc.) |
| `[SOURCE-PRIORITY-1..3]` | Ordered list of preferred source types for this domain |
| `[STATUS-TRACKING-FILE]` | File where research completion status is tracked |
| `[COMMON-PROBLEM]` / `[SOLUTION]` | Domain-specific troubleshooting entries |

## Key Design Decisions

1. **Research Categories with Data Point Tables**: Each category gets its own table with "Data Point | Search Strategy" -- this guides the agent to search systematically rather than ad-hoc
2. **Output Format with Source + Confidence**: Every finding has attribution and a confidence level, making the output auditable and trust-calibrated
3. **Search Query Templates**: Pre-built query patterns reduce agent guesswork and improve search quality
4. **Data Quality Guidelines**: The 3-tier confidence system (Confirmed/Estimated/Unknown) prevents false certainty
5. **Troubleshooting Section**: Anticipates real-world research challenges specific to the domain
6. **Separate Output Files**: Research outputs go to dedicated files, not appended to existing docs (prevents file bloat)

## Example Usage

**Applied to competitive research**: See `.cursor/exemplars/analysis/market/research-competitor-exemplar.md`
**Applied to corporate history**: See `.cursor/prompts/analysis/market/research-company-history.prompt.md`

## Related Templars

- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- Similar pattern extracted from `research-company-history.prompt.md`. Consider consolidating if both templars serve the same use case; they share the same core pattern (research categories + data tables + source/confidence + search query templates) but were extracted from different source artifacts
- Ticket templars under `.cursor/templars/ticket/` (different domain, but similar structured-output pattern)

---

**Extracted from**: `.cursor/prompts/analysis/market/research-competitor.prompt.md`
**Referenced by**: Research prompt family in `.cursor/prompts/analysis/market/`
