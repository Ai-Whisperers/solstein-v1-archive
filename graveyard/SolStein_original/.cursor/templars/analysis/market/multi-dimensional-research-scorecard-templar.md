---
type: templar
artifact-type: prompt
applies-to: analysis, research, assessment, competitive-intelligence, due-diligence
pattern-name: multi-dimensional-research-scorecard
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-financial-growth.prompt.md
---

# Multi-Dimensional Research with Scoring Rubric - Templar

## Pattern Purpose

Provides a reusable framework for prompts that drive structured, multi-dimensional research on a subject, collect evidence from ranked sources, and produce a composite scorecard with named classification bands. Eliminates gut-feel assessments in favour of explicit, rubric-based scoring.

## Artifact Type

**For**: Prompts (analysis, research, assessment, evaluation)

## When to Use

- Researching entities across multiple dimensions (financial, technology, compliance, etc.)
- Comparing multiple subjects on a common scorecard (competitors, vendors, markets)
- Assessments requiring explicit evidence, source tracking, and confidence levels
- Any research task where data availability varies widely between subjects
- Building dashboards or comparison matrices from individual deep-dives

## Template Structure

### Frontmatter

```yaml
---
name: research-[DOMAIN_SLUG]
description: "Please perform a structured [DOMAIN] research analysis on [SUBJECT_TYPE]"
category: analysis
tags: [DOMAIN_TAGS]
argument-hint: "[SUBJECT_NAME] and path or identifier"
---
```

### Section 1: Title and Purpose

```markdown
# Research [DOMAIN] - Per-[SUBJECT_TYPE] Deep-Dive

Please perform a structured [DOMAIN] research session on [SUBJECT_TYPE].
This prompt drives systematic research focused on [DIMENSIONS_SUMMARY],
then produces a `[OUTPUT_FILENAME]` in the subject's folder.

**Pattern**: Guided Analysis Pattern
**Use When**: [TRIGGER_CONDITION]
```

**Customise**: Replace `[DOMAIN]`, `[SUBJECT_TYPE]`, `[DIMENSIONS_SUMMARY]`, and `[TRIGGER_CONDITION]`.

### Section 2: Required Context

```markdown
## Required Context

- **[SUBJECT_NAME_LABEL]**: The [SUBJECT_TYPE] to research (e.g., "[EXAMPLE_SUBJECT]")
- **[SUBJECT_LOCATION_LABEL]**: Path or identifier for existing data
- **[REFERENCE_CONTEXT]**: Baseline or comparison reference
```

### Section 3: Process Steps

```markdown
## Process

### Step 1: Read Existing Data
Read the subject's existing files. Extract any [DOMAIN] data already captured. Note gaps.

### Step 2: Read Reference Baseline
Read [REFERENCE_FILE] for comparison context.

### Step 3: Research by Category
For each of the [N] research categories below, perform targeted searches.
Prioritise these source types (in order of reliability):

1. [SOURCE_RANK_1] (most reliable)
2. [SOURCE_RANK_2]
3. ...
N. [SOURCE_RANK_N] (least reliable)

### Step 4: Build Timelines
Construct multi-year timelines for key metrics. For each data point record:
- Value (in original units AND normalised equivalent)
- Source and confidence level
- Period-over-period growth rate

### Step 5: Score Dimensions
Using the **Scoring Rubric** below, assign a score (1-10) per dimension. Follow the rubric criteria.

### Step 6: Write Output File
Write findings to `[OUTPUT_PATH]/[OUTPUT_FILENAME]` as a standalone file.

### Step 7: Update Status Tracker
Update [STATUS_TRACKER_FILE] to reflect analysis complete for this subject.
```

### Section 4: Research Categories

Repeat this block for each research dimension:

```markdown
## Research Categories

### Category [N]: [DIMENSION_NAME]

| Data Point | Search Strategy |
| --- | --- |
| [DATA_POINT_1] | [HOW_TO_FIND_IT] |
| [DATA_POINT_2] | [HOW_TO_FIND_IT] |
| ... | ... |
```

**Guidance**: 4-8 categories is the sweet spot. Each category should have 5-15 specific data points with concrete search strategies.

### Section 5: Scoring Rubric

Repeat this block for each scored dimension:

```markdown
## Scoring Rubric

### [DIMENSION_NAME] (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | [EXCEPTIONAL_THRESHOLD] |
| 7-8 | [STRONG_THRESHOLD] |
| 5-6 | [MODERATE_THRESHOLD] |
| 3-4 | [MODEST_THRESHOLD] |
| 1-2 | [MINIMAL_THRESHOLD] |
```

**Guidance**: Each level must have a measurable criterion (numbers, percentages, counts) -- never vague adjectives. Scores must be comparable across subjects.

### Section 6: Composite Score and Classification

```markdown
### Composite Score

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| [DIMENSION_1] | [X] | [1-line justification] |
| [DIMENSION_2] | [X] | [1-line justification] |
| ... | ... | ... |
| **COMPOSITE** | **[avg]** | **[CLASSIFICATION_LABEL]** |

**Classification Thresholds**:

- **[BAND_1_NAME]** (avg [RANGE]): [BAND_1_DESCRIPTION]
- **[BAND_2_NAME]** (avg [RANGE]): [BAND_2_DESCRIPTION]
- **[BAND_3_NAME]** (avg [RANGE]): [BAND_3_DESCRIPTION]
- **[BAND_4_NAME]** (avg [RANGE]): [BAND_4_DESCRIPTION]
```

**Guidance**: Use 3-5 classification bands. Name them memorably (evocative labels stick better than generic ones like "Level 1-4").

### Section 7: Output Format

```markdown
## Output Format

Structure the output as a **standalone markdown file** saved to `[OUTPUT_PATH]/[OUTPUT_FILENAME]`:

```markdown
# [DOMAIN] Deep-Dive - [SUBJECT_NAME]

**Research Date**: YYYY-MM-DD
**Data Availability**: High / Medium / Low

### [TIMELINE_METRIC_1] Timeline

| Year | Value | Units | Normalised | YoY Growth | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| [YEAR] | [value] | [units] | [normalised] | [%] | [source] | Confirmed/Estimated |

#### [METRIC_1] Trend Chart

```mermaid
xychart-beta
    title "[SUBJECT] [METRIC_1] Trend"
    x-axis [year1, year2, ...]
    y-axis "[UNITS]" 0 --> [max]
    line [val1, val2, ...]
```

### Scoring Summary

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| [DIMENSION] | [X] | [1-line justification] |
| **COMPOSITE** | **[avg]** | **[Classification]** |
```
```

**Guidance**: Include Mermaid chart templates for any timeline with 3+ data points. Charts provide immediate visual impact.

### Section 8: Subject-Type Decision Tree

```markdown
## Reasoning Process

### Subject-Type Decision Tree

```text
[CLASSIFICATION_QUESTION]?
|-- [TYPE_A] --> Path A
|   |-- Search: [PRIMARY_SOURCES_A]
|   |-- Expected data quality: [HIGH/MEDIUM/LOW]
|   |-- Start with: "[INITIAL_QUERY_A]"
|
|-- [TYPE_B] --> Path B
|   |-- Search: [PRIMARY_SOURCES_B]
|   |-- Expected data quality: [HIGH/MEDIUM/LOW]
|   |-- Start with: "[INITIAL_QUERY_B]"
|
|-- [TYPE_C] --> Path C
    |-- Search: [PRIMARY_SOURCES_C]
    |-- Expected data quality: [HIGH/MEDIUM/LOW]
    |-- Start with: "[INITIAL_QUERY_C]"
```
```

**Guidance**: Route research approach based on subject characteristics that affect data availability. This prevents wasted effort searching sources that won't have data for a given subject type.

### Section 9: Search Query Templates

```markdown
## Search Query Templates

**[CATEGORY_1]**:

- `"[SUBJECT]" [KEYWORD_1] [KEYWORD_2] [YEAR_RANGE]`
- `"[SUBJECT]" [KEYWORD_3] [SOURCE_NAME]`

**[CATEGORY_2]**:

- `"[SUBJECT]" [KEYWORD_4] [KEYWORD_5]`
```

### Section 10: Few-Shot Examples

```markdown
## Examples (Few-Shot)

### Example: [TYPE_A_SUBJECT] (Data-Rich)

[Brief description of expected output quality and key metrics]

### Example: [TYPE_B_SUBJECT] (Data-Scarce)

[Brief description, highlighting estimation approach and confidence handling]

### Example: [TYPE_C_SUBJECT] (Data-Minimal)

[Brief description, highlighting honest gap reporting and proxy metrics]
```

**Guidance**: Provide 2-3 examples spanning the data-availability spectrum (rich, scarce, minimal). This calibrates the AI's approach for different subject types.

### Section 11: Troubleshooting

```markdown
## Troubleshooting

### Problem: [COMMON_DATA_CHALLENGE_1]

**Symptoms**: [OBSERVABLE_INDICATORS]

**Solution**:

1. [PROXY_APPROACH]
2. [ALTERNATIVE_SOURCE]
3. [ESTIMATION_METHOD]
4. Mark derived figures as "Estimated ([method])" with explanation
5. Score conservatively -- lack of data is itself a signal
```

### Section 12: Quality Criteria

```markdown
## Quality Criteria

- [ ] All [N] research categories addressed (no sections skipped)
- [ ] Timelines have minimum [M] years of data (or explicit "Unknown" entries)
- [ ] Every data point has a source attribution
- [ ] Every data point has a confidence level (Confirmed/Estimated/Unknown)
- [ ] Values include both original units AND normalised equivalent
- [ ] Scorecard scores follow the explicit rubric
- [ ] Composite score calculated as average of [N] dimensions
- [ ] Classification matches composite score thresholds
- [ ] Output saved to designated file path
- [ ] Status tracker updated
```

## Customisation Points

| Placeholder | Guidance |
| --- | --- |
| `[DOMAIN]` | The research domain (Financial, Technology, Compliance, Market, etc.) |
| `[SUBJECT_TYPE]` | What is being researched (competitor, vendor, market, product, etc.) |
| `[DIMENSIONS]` | The 4-8 scoring dimensions (e.g., Revenue Growth, Funding, Employee Growth) |
| `[SCORING_RUBRIC]` | Numeric criteria per score level per dimension -- must be measurable |
| `[CLASSIFICATION_BANDS]` | Named bands with score ranges (e.g., Rocket 7-10, Dinosaur 1-3) |
| `[SOURCE_HIERARCHY]` | Ranked list of source types from most to least reliable |
| `[DECISION_TREE]` | Subject-type routing for different research approaches |
| `[OUTPUT_FORMAT]` | Tables, timelines, charts, and scorecard for the output file |
| `[SEARCH_TEMPLATES]` | Ready-to-use search queries with `[SUBJECT]` placeholders |
| `[FEW_SHOT_EXAMPLES]` | 2-3 examples spanning data-availability spectrum |

## Example Usage

**For Financial Research** (see exemplar: `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md`):
- Domain: Financial & Growth
- Dimensions: Revenue Growth, Funding Momentum, Employee Growth, Geographic Expansion, M&A Activity, SaaS Maturity
- Classification: Rocket / Riser / Steady / Dinosaur
- Subject Types: Public Company, PE-Acquired, VC-Funded Startup, Private/Bootstrapped

**For Technology Maturity Assessment**:
- Domain: Technology Maturity
- Dimensions: Architecture Modernity, CI/CD Maturity, Test Coverage, API Design, Cloud Readiness, AI/ML Adoption
- Classification: Cutting-Edge / Modern / Legacy / Obsolete
- Subject Types: SaaS-native, Migrating, On-premise, Mainframe

**For Vendor Evaluation**:
- Domain: Vendor Assessment
- Dimensions: Product Fit, Financial Stability, Support Quality, Integration Ease, Security Posture, Pricing Value
- Classification: Strategic Partner / Preferred / Acceptable / Avoid
- Subject Types: Enterprise Vendor, Mid-Market, Startup, Open-Source

## Related Templars

- Ticket templars (`.cursor/templars/ticket/`) -- for structuring research as ticket work
- General task template (`.cursor/templars/general-task-template.md`) -- simpler task structure

## Related Exemplars

- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` -- Full implementation showing this pattern applied to financial competitor research

---

**Extracted From**: `.cursor/prompts/analysis/market/research-financial-growth.prompt.md`
**Created**: 2026-02-15
