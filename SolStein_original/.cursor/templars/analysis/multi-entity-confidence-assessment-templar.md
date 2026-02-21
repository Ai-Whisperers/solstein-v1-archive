---
type: templar
artifact-type: prompt
applies-to: analysis, assessment, quality, confidence, maturity, readiness, evaluation
pattern-name: multi-entity-confidence-assessment
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/assess-data-confidence.prompt.md
---

# Multi-Entity Confidence / Quality Assessment - Templar

## Pattern Purpose

Provides a reusable framework for prompts that assess quality, confidence, or maturity across a **collection** of already-inventoried entities. Produces per-entity scores on N dimensions, composite scores, traffic-light classifications, and a prioritized action list for gap-filling. Eliminates subjective "feels about right" assessments in favour of explicit, rubric-based scoring.

**Distinct from** `multi-dimensional-research-scorecard-templar`: that templar drives research *and* scoring for a single entity; this templar operates on an **existing body of work** for multiple entities and evaluates *data quality / readiness / maturity*, not entity properties.

## Artifact Type

**For**: Prompts (analysis, assessment, quality, confidence, maturity, readiness)

## When to Use

- Evaluating data quality across previously researched subjects (e.g., competitors, vendors, modules)
- Scoring documentation maturity across multiple repos or projects
- Assessing code quality or test coverage across multiple components
- Vendor evaluation across N candidates on a shared rubric
- Migration readiness assessment across modules
- Compliance readiness checks across teams or systems
- Any scenario where you have multiple entities with varying depth of information and need to answer "how confident / ready / mature are we?"

## Template Structure

### Frontmatter

```yaml
---
name: assess-[DOMAIN_SLUG]
description: "Please assess [DOMAIN] [QUALITY_NOUN] across all [ENTITY_TYPE_PLURAL] and produce per-[ENTITY_TYPE] quality scores"
category: analysis
tags: [DOMAIN_TAGS]
argument-hint: "[ARGUMENT_HINT_OR_NONE]"
---
```

### Section 1: Title and Purpose

```markdown
# Assess [DOMAIN] [QUALITY_NOUN] - Per-[ENTITY_TYPE] Quality Scoring

Please perform a systematic [QUALITY_NOUN] assessment across all [ENTITY_TYPE_PLURAL] in `[ENTITY_ROOT_PATH]`. For each [ENTITY_TYPE], score [QUALITY_NOUN] on [N] dimensions, compute a composite [QUALITY_NOUN] score, and generate a prioritised action list showing where further work is needed.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: [ONE_SENTENCE_VALUE_PROPOSITION]
**Use When**: [TRIGGER_CONDITION]
```

**Customise**: Replace `[DOMAIN]`, `[QUALITY_NOUN]` (confidence / maturity / readiness / quality), `[ENTITY_TYPE]`, `[ENTITY_ROOT_PATH]`, and `[TRIGGER_CONDITION]`.

### Section 2: Purpose

```markdown
## Purpose

[WHY_THIS_ASSESSMENT_MATTERS -- 2-3 paragraphs explaining:
 1. What signals exist but are not aggregated
 2. What goes wrong without this assessment (misleading dashboards, uninformed decisions, etc.)
 3. What gap this prompt closes]

This prompt closes that gap by producing a single `[OUTPUT_PATH]/[OUTPUT_FILENAME]` report.
```

### Section 3: Required Context

```markdown
## Required Context

- **[ENTITY_LOCATION_LABEL]**: `[ENTITY_ROOT_PATH]/[entity-slug]/` -- each folder may contain:
  - `[FILE_1]` -- [description]
  - `[FILE_2]` -- [description]
  - `[FILE_N]` -- [description]
- **[REFERENCE_CONTEXT]**: [baseline or index file]

[ARGUMENT_OR_NO_ARGUMENT_NOTE]
```

### Section 4: Process Steps

```markdown
## Process

### Step 1: Enumerate [ENTITY_TYPE_PLURAL]
Read [INDEX_FILE] and list all [ENTITY_TYPE_PLURAL] in `[ENTITY_ROOT_PATH]`.

### Step 2: Inventory Files Per [ENTITY_TYPE]
For each [ENTITY_TYPE], check which expected files exist:

| File | Source / Prompt |
|---|---|
| `[FILE_1]` | [ORIGIN_DESCRIPTION] |
| `[FILE_2]` | [ORIGIN_DESCRIPTION] |
| `[FILE_N]` | [ORIGIN_DESCRIPTION] |

Record presence/absence.

### Step 3: Score Each [ENTITY_TYPE] on [N] Dimensions
Read all available files and assign a score from 1-10 on each dimension using the rubric below.

### Step 4: Compute Composite Score
Calculate **Composite [QUALITY_NOUN] Score** = simple average of [N] dimension scores, rounded to one decimal.

### Step 5: Classify Traffic Light
Apply traffic-light classification:

| Range | Label | Meaning |
|---|---|---|
| [HIGH_RANGE] | **[HIGH_LABEL]** | [HIGH_MEANING] |
| [MEDIUM_RANGE] | **[MEDIUM_LABEL]** | [MEDIUM_MEANING] |
| [LOW_RANGE] | **[LOW_LABEL]** | [LOW_MEANING] |

### Step 6: Generate Action Items
For each [ENTITY_TYPE] scoring [MEDIUM_LABEL] or [LOW_LABEL], recommend:
- Which specific actions or prompts to run next
- Which dimensions are weakest and why
- Priority order (lowest-scoring entities first)

### Step 7: Write Output
Write the full report to `[OUTPUT_PATH]/[OUTPUT_FILENAME]`.
```

**Guidance**: 3-5 classification bands is the sweet spot. Use evocative or domain-appropriate labels.

### Section 5: Scoring Rubric

Repeat this block for each scored dimension:

```markdown
## Scoring Rubric (1-10 Scale)

### Dimension [N]: [DIMENSION_NAME]

[ONE_SENTENCE_DESCRIPTION_OF_WHAT_THIS_MEASURES]

| Score | Criteria |
|---|---|
| 9-10 | [EXCEPTIONAL_THRESHOLD -- measurable, no vague adjectives] |
| 7-8 | [STRONG_THRESHOLD] |
| 5-6 | [MODERATE_THRESHOLD] |
| 3-4 | [MODEST_THRESHOLD] |
| 1-2 | [MINIMAL_THRESHOLD] |

**[SUPPORTING_DEFINITIONS]**: [list concrete things to check, e.g., standard data fields, source types, date ranges]
```

**Guidance**: Each score band must have a measurable criterion (numbers, percentages, counts). 4-7 dimensions is optimal. Scores must be comparable across entities.

### Section 6: Output Format

```markdown
## Output Format

Write the output to `[OUTPUT_PATH]/[OUTPUT_FILENAME]`:

# [DOMAIN] [QUALITY_NOUN] Assessment

**Assessment Date**: YYYY-MM-DD
**[ENTITY_TYPE_PLURAL] Assessed**: [count]
**Methodology**: [N]-dimension scoring (1-10 scale), composite average, traffic-light classification

## Summary

| [QUALITY_NOUN] Level | Count | [ENTITY_TYPE_PLURAL] |
|---|---|---|
| [HIGH_LABEL] ([HIGH_RANGE]) | [n] | [list] |
| [MEDIUM_LABEL] ([MEDIUM_RANGE]) | [n] | [list] |
| [LOW_LABEL] ([LOW_RANGE]) | [n] | [list] |

## Per-[ENTITY_TYPE] Scores

| [ENTITY_TYPE] | [DIM_1] | [DIM_2] | ... | [DIM_N] | Composite | [QUALITY_NOUN] |
|---|---|---|---|---|---|---|
| [Entity 1] | [1-10] | [1-10] | ... | [1-10] | [avg] | [LABEL] |

## Dimension Analysis

### Strongest Dimension Across All [ENTITY_TYPE_PLURAL]
[Which dimension scores highest on average and why]

### Weakest Dimension Across All [ENTITY_TYPE_PLURAL]
[Which dimension scores lowest on average and what to do about it]

### Distribution
- Average Composite Score: [value]
- Highest: [entity] ([score])
- Lowest: [entity] ([score])
- Standard Deviation: [value]

## Action Items (Prioritised)

### Priority 1: Critical Gaps ([LOW_LABEL])

| [ENTITY_TYPE] | Composite | Weakest Dimension | Recommended Action |
|---|---|---|---|
| [Entity] | [score] | [dimension] | [SPECIFIC_ACTION_OR_PROMPT] |

### Priority 2: Moderate Gaps ([MEDIUM_LABEL])

| [ENTITY_TYPE] | Composite | Weakest Dimension | Recommended Action |
|---|---|---|---|
| [Entity] | [score] | [dimension] | [SPECIFIC_ACTION_OR_PROMPT] |

### Priority 3: Refresh Needed ([HIGH_LABEL] but aging)

| [ENTITY_TYPE] | Composite | [STALENESS_DIM] Score | Recommended Action |
|---|---|---|---|
| [Entity] | [score] | [score] | [SPECIFIC_ACTION_OR_PROMPT] |

## Scoring Notes
[Per-entity notes explaining non-obvious scores or special circumstances]
```

### Section 7: Few-Shot Examples

```markdown
## Examples (Few-Shot)

### Example: Scoring a Well-[ASSESSED] [ENTITY_TYPE] ([HIGH_LABEL])

**[ENTITY_TYPE]**: `[entity-slug]/`
**Files present**: [list] ([M] of [N])

**Scoring Walkthrough**:

| Dimension | Score | Rationale |
|---|---|---|
| [DIM_1] | [X] | [1-line justification referencing rubric band] |
| [DIM_N] | [X] | [1-line justification] |

**Composite**: ([sum]) / [N] = **[avg]** -- **[LABEL]**

**Scoring Note**: "[explanation of any non-obvious rating]"

### Example: Scoring a Thinly-[ASSESSED] [ENTITY_TYPE] ([LOW/MEDIUM_LABEL])

[Same structure but showing a weaker entity with different scores and action items]
```

**Guidance**: Provide 2 examples spanning the quality spectrum (strong vs weak). This calibrates the AI's scoring consistency.

### Section 8: Reasoning Process and Self-Correction

```markdown
## Reasoning Process (for AI Agent)

1. **Enumerate**: List all [ENTITY_TYPE_PLURAL] in `[ENTITY_ROOT_PATH]`
2. **Inventory**: Check which files exist per entity
3. **Read**: Read all available files per entity
4. **Score**: Apply rubric systematically -- dimension by dimension, entity by entity
5. **Compute**: Calculate composite scores and assign traffic-light levels
6. **Prioritise**: Sort action items by composite score ascending (worst first)
7. **Write**: Produce output file in specified format
8. **Cross-check**: Verify every entity has a row and every low-scorer has an action item

### Self-Correction (before finalising output)

- **Rubric adherence**: Re-read each dimension score and confirm it falls within the rubric's criteria band.
- **Arithmetic**: Recalculate every composite score. Confirm traffic-light label matches composite range.
- **Coverage**: Count rows in per-entity table and compare to enumeration in Step 1.
- **Action item completeness**: Every [MEDIUM/LOW_LABEL] entity must have at least one action item. [HIGH_LABEL] entities with low [STALENESS_DIM] scores should appear in Priority 3.
- **Internal consistency**: If you scored a dimension high but noted contradictions, re-examine and adjust.
```

### Section 9: Quality Criteria

```markdown
## Quality Criteria

- [ ] All [ENTITY_TYPE] [LOCATIONS] scanned
- [ ] Each entity scored on all [N] dimensions with 1-10 values
- [ ] Every score justified against the rubric criteria (not arbitrary)
- [ ] Composite score correctly computed as simple average, rounded to 1 decimal
- [ ] Traffic-light classification applied per defined ranges
- [ ] Summary table counts match per-entity table row count
- [ ] Action items specify what to do and what gap it fills
- [ ] Action items sorted by priority (lowest [QUALITY_NOUN] first)
- [ ] Scoring notes provided for non-obvious ratings
- [ ] Output written to `[OUTPUT_PATH]/[OUTPUT_FILENAME]`
```

### Section 10: Troubleshooting

```markdown
## Troubleshooting

| Issue | Solution |
|---|---|
| [ENTITY_TYPE] folder exists but is empty | Score [DEPTH_DIM] as 1. Note in Scoring Notes. |
| Inherently limited data availability | Score based on what's available, not theoretical maximum. Add note. |
| Contradictions found during assessment | Score [CONSISTENCY_DIM] low. Document specifics in Scoring Notes. |
| Unsure whether item is a valid [ENTITY_TYPE] | Check [INDEX_FILE]. Skip non-[ENTITY_TYPE] items. |
| Large number of entities (20+) | Process in batches. All must appear in final output. |
| File exists but contains only stub/template | Treat as absent for scoring. Note in Scoring Notes. |
```

## Customisation Points

| Placeholder | Guidance |
|---|---|
| `[DOMAIN]` | The assessment domain (Data Confidence, Code Quality, Documentation Maturity, etc.) |
| `[QUALITY_NOUN]` | What is being assessed (confidence, quality, maturity, readiness, compliance) |
| `[ENTITY_TYPE]` | What is being scored (competitor, module, repository, vendor, team, system) |
| `[ENTITY_ROOT_PATH]` | Where entities live (folder path or data source) |
| `[DIMENSIONS]` | The 4-7 scoring dimensions with rubric criteria per band |
| `[CLASSIFICATION_BANDS]` | Named traffic-light bands with score ranges (High/Medium/Low or custom) |
| `[OUTPUT_FILENAME]` | Name of the output report file |
| `[FEW_SHOT_EXAMPLES]` | 2 examples spanning the quality spectrum (strong + weak) |

## Example Usage

**For Competitive Intelligence Data Confidence** (see exemplar: `.cursor/exemplars/analysis/market/data-confidence-assessment-exemplar.md`):
- Domain: Data Confidence
- Dimensions: Completeness, Source Quality, Recency, Consistency, Research Depth
- Classification: High (7-10) / Medium (4-6.9) / Low (1-3.9)
- Entity Type: Competitor

**For Documentation Maturity Assessment**:
- Domain: Documentation Maturity
- Dimensions: Coverage, Accuracy, Freshness, Accessibility, Discoverability
- Classification: Mature / Developing / Nascent
- Entity Type: Repository or Module

**For Migration Readiness Assessment**:
- Domain: Migration Readiness
- Dimensions: Code Complexity, Test Coverage, Dependency Health, Documentation, Risk Profile
- Classification: Ready / Needs Work / Blocked
- Entity Type: Module or Component

**For Vendor Evaluation**:
- Domain: Vendor Suitability
- Dimensions: Product Fit, Financial Stability, Support Quality, Integration Ease, Security Posture
- Classification: Strategic Partner / Acceptable / Avoid
- Entity Type: Vendor

## Related Templars

- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- For prompts that *research AND score* a single entity (complementary, not overlapping)
- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- For prompts that guide step-by-step research on a subject

## Related Exemplars

- `.cursor/exemplars/analysis/market/data-confidence-assessment-exemplar.md` -- Full implementation showing this pattern applied to competitive intelligence data confidence

---

**Extracted From**: `.cursor/prompts/analysis/market/assess-data-confidence.prompt.md`
**Created**: 2026-02-17
