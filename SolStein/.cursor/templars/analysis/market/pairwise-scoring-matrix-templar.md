---
type: templar
artifact-type: prompt
applies-to: analysis, comparison, overlap, pairwise, matrix, due-diligence, M&A
pattern-name: pairwise-scoring-matrix
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-competitive-overlap.prompt.md
---

# Pairwise Scoring Matrix - Templar

## Pattern Purpose

Provides a reusable framework for prompts that compare N entities against each other in pairs, score overlap/similarity/fit across K dimensions using fixed rubrics, assemble a symmetric N x N matrix, rank the most significant pairs, identify clusters, and derive strategic implications.

Fundamentally different from the per-entity scorecard pattern (`multi-dimensional-research-scorecard-templar.md`) which scores each entity independently. This pattern scores **relationships between entities**.

## Artifact Type

**For**: Prompts (analysis, comparison, overlap, pairwise evaluation)

## When to Use

- Comparing N entities pairwise across multiple dimensions (overlap, similarity, compatibility)
- Building symmetric N x N matrices where Score(A,B) = Score(B,A)
- Identifying clusters of entities with mutual high scores
- Answering "which pairs are most alike/overlapping/compatible?"
- Any analysis where the relationship between entities matters more than individual entity scores

## When NOT to Use

- Scoring entities independently (use `multi-dimensional-research-scorecard-templar.md` instead)
- Comparing entities against a single reference/baseline
- Ranking entities on a leaderboard (no pairwise relationship needed)

## Template Structure

### Frontmatter

```yaml
---
name: [ACTION]-[DOMAIN_SLUG]
description: "Please produce a pairwise [ANALYSIS_TYPE] assessment matrix across [ENTITY_SET]"
category: analysis
tags: [DOMAIN_TAGS]
argument-hint: "[OPTIONAL_ARGUMENTS]"
---
```

### Section 1: Title, Purpose and Pattern

```markdown
# [ANALYSIS_TYPE] - Pairwise Assessment Matrix

Please produce a pairwise [ANALYSIS_TYPE] assessment across all [ENTITY_TYPE_PLURAL]
in [ENTITY_SOURCE]. For every pair, score [ANALYSIS_FOCUS] on [K] dimensions,
compute a composite score, and generate a full N x N matrix plus a ranked list of
the most [SIGNIFICANT_ADJECTIVE] pairs.

**Pattern**: Guided Analysis Pattern
**Use When**: [TRIGGER_CONDITION]
```

**Customise**: Replace `[ANALYSIS_TYPE]`, `[ENTITY_TYPE_PLURAL]`, `[ENTITY_SOURCE]`, `[K]`, and `[SIGNIFICANT_ADJECTIVE]`.

### Section 2: Required Context

```markdown
## Required Context

- **[ENTITY_LIST_SOURCE]**: [Where to find the roster of entities]
- **[REFERENCE_ENTITY]**: [Optional self-assessment entity, e.g., "our company"]
- **[SUPPORTING_DATA]**: [Per-entity profiles, reports, or data files]
```

### Section 3: Usage Modes (Optional but Recommended)

```markdown
## Usage Modes

### Full Matrix (Default)
Score every pair. Produces the complete N x N matrix.

### [REFERENCE]-Only Focus
Score only [REFERENCE_ENTITY]'s overlap with each entity. Single ranked column.

### [FILTER]-Filtered
Score only entities matching [FILTER_CRITERIA]. Reduces matrix size.

### Delta Update
Re-score only pairs involving newly added or updated entities. Merge into existing output.
```

### Section 4: Scoring Dimensions (K dimensions)

Repeat this block for each dimension:

```markdown
## Scoring Dimensions ([K])

### Dimension [N]: [DIMENSION_NAME]

[DIMENSION_QUESTION -- what does this dimension measure between a pair?]

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | [NO_OVERLAP_LABEL] | [CRITERIA_0] |
| 1 | [ADJACENT_LABEL] | [CRITERIA_1] |
| 2 | [PARTIAL_LABEL] | [CRITERIA_2] |
| 3 | [DIRECT_LABEL] | [CRITERIA_3] |
```

**Guidance**:
- 3-7 dimensions is the sweet spot. Each must measure a distinct aspect of the pairwise relationship.
- Use a fixed scale (e.g., 0-3) across ALL dimensions for consistent compositing.
- Each level must have measurable criteria -- never vague adjectives.
- Criteria should be symmetric: Score(A,B) must equal Score(B,A) under the rubric.

### Section 5: Composite Score

```markdown
## Composite Score

For each pair (A, B):

Composite = [DIMENSION_1] + [DIMENSION_2] + ... + [DIMENSION_K]

- **Range**: 0 - [K * MAX_PER_DIMENSION]
- **Interpretation**:
  - [BAND_1_RANGE]: [BAND_1_LABEL] -- [BAND_1_DESCRIPTION]
  - [BAND_2_RANGE]: [BAND_2_LABEL] -- [BAND_2_DESCRIPTION]
  - [BAND_3_RANGE]: [BAND_3_LABEL] -- [BAND_3_DESCRIPTION]
  - [BAND_4_RANGE]: [BAND_4_LABEL] -- [BAND_4_DESCRIPTION]
```

**Guidance**: Use 3-5 interpretation bands. Simple sum (not weighted average) keeps the model auditable. Document why weighting is not used or, if used, document the weights and rationale.

### Section 6: Process Steps

```markdown
## Process

### Step 1: Build Entity Roster
Read [ENTITY_SOURCE] and build the full list. Include [REFERENCE_ENTITY] as row/column 0.

### Step 2: Read All Entity Profiles
For each entity, extract data points relevant to each scoring dimension.

### Step 3: Score [REFERENCE_ENTITY] Self-Assessment
Document [REFERENCE_ENTITY]'s own profile on each dimension before scoring pairs.

### Step 4: Score Pairwise [ANALYSIS_TYPE]
For each unique pair (A, B) where A < B in the roster:
1. Score each of the [K] dimensions (0-[MAX]) using the rubrics
2. Compute composite (sum)
3. Record rationale for any maximum score

Score based on evidence, not speculation. Where data is sparse, score conservatively.

### Step 5: Assemble N x N Matrix
Build the symmetric matrix. Only compute upper triangle. Diagonal is N/A (self).

### Step 6: Rank Top Pairs
Extract all pairs sorted by composite descending. Highlight top [TOP_N].

### Step 7: Extract [REFERENCE_ENTITY] Profile
Dedicated section showing [REFERENCE_ENTITY]'s score with every entity, sorted descending.

### Step 8: Identify Clusters
Group entities with mutual composite >= [CLUSTER_THRESHOLD].

### Step 9: Derive Strategic Implications
Extract actionable insights from the patterns.

### Step 10: Write Output
Save to [OUTPUT_PATH].

### Step 11: Self-Correction Validation
Re-read output and verify:
1. Matrix symmetry: Score(A,B) = Score(B,A)
2. Arithmetic: Every composite = sum of dimension scores
3. Completeness: Every entity from roster appears
4. Rubric compliance: No score exceeds max or falls below 0
5. Evidence for max scores: Cited rationale
6. Ranking consistency: Rankings match matrix values
```

### Section 7: Output Format

```markdown
## Output Format

### Header
- Generated date, entity count, data source, scoring summary

### [REFERENCE_ENTITY] Self-Assessment Table
| Dimension | [REFERENCE_ENTITY] Profile |

### [REFERENCE_ENTITY] Rankings
| Rank | Entity | [Dim1] | [Dim2] | ... | Composite | [SIGNIFICANCE_LABEL] |

### Top [TOP_N] Most [SIGNIFICANT_ADJECTIVE] Pairs
| Rank | Entity A | Entity B | [Dim1] | [Dim2] | ... | Composite |

### Full N x N Matrix (Composite Scores)
Symmetric table with entities on both axes. Diagonal = --.

### Clusters
Groups of 3+ entities with mutual composite >= [CLUSTER_THRESHOLD].

### Dimension Heatmaps (Optional)
Mermaid quadrant charts or other visualisations per dimension.

### Strategic Implications
Actionable insights derived from the overlap/similarity patterns.

### Data Confidence Notes
Low-confidence scores, data gaps, assumptions.

### Methodology
Dimensions, scale, composite formula, data sources, symmetry rule.
```

### Section 8: Few-Shot Examples

```markdown
## Examples (Few-Shot)

### Example 1: [PAIR_HIGH_SCORE] (Expected High [ANALYSIS_TYPE])

| Dimension | Score | Rationale |
| --- | --- | --- |
| [Dim1] | [score] | [evidence] |
| ...
| **Composite** | **[total]** | **[interpretation]** |

### Example 2: [PAIR_LOW_SCORE] (Expected Low [ANALYSIS_TYPE])

| Dimension | Score | Rationale |
| ... |
| **Composite** | **[total]** | **[interpretation]** |

### Example 3: [PAIR_MODERATE_SCORE] (Expected Moderate)

| Dimension | Score | Rationale |
| ... |
| **Composite** | **[total]** | **[interpretation]** |
```

**Guidance**: Provide 2-3 examples spanning the score range (high, low, moderate). Include rationale to calibrate scoring consistency.

### Section 9: Troubleshooting

```markdown
## Troubleshooting

### Problem: Too Many Entities for a Readable Matrix
[Solution: sub-matrices, filtered views, separate ranked tables]

### Problem: Sparse Data for Some Entities
[Solution: score conservatively, mark low-confidence, note in Data Confidence]

### Problem: Asymmetric Information
[Solution: score based on best available, don't inflate, note asymmetry]

### Problem: Scores Feel Wrong After Assembly
[Solution: re-read profiles side-by-side, check rubric consistency, verify correct dimension]

### Problem: Delta Mode Merging
[Solution: read existing, re-score affected pairs only, re-rank, update date]
```

### Section 10: Quality Criteria

```markdown
## Quality Criteria

### Completeness
- [ ] All entities from roster included
- [ ] [REFERENCE_ENTITY] included with self-assessment
- [ ] All [K] dimensions scored for every pair
- [ ] Top [TOP_N] pairs ranked
- [ ] [REFERENCE_ENTITY] rankings separate
- [ ] Clusters identified
- [ ] Strategic implications completed

### Correctness
- [ ] Rubric consistently applied
- [ ] Composites computed correctly (sum, correct range)
- [ ] Matrix is symmetric
- [ ] Every max-score has cited rationale
- [ ] No speculative high scores without evidence

### Output Quality
- [ ] At least one visualisation included
- [ ] Data confidence notes present
- [ ] Output saved to designated path
- [ ] Self-correction validation passed
```

## Customisation Points

| Placeholder | Guidance |
| --- | --- |
| `[ANALYSIS_TYPE]` | What relationship is being measured (Overlap, Similarity, Compatibility, Fit) |
| `[ENTITY_TYPE_PLURAL]` | What is being compared (competitors, teams, products, vendors, services) |
| `[ENTITY_SOURCE]` | Where to find the roster (folder, file, database, API) |
| `[REFERENCE_ENTITY]` | Optional anchor entity for focused analysis (e.g., "our company") |
| `[K]` | Number of scoring dimensions (3-7 recommended) |
| `[DIMENSIONS]` | The K dimensions with rubrics (0-N scale per dimension) |
| `[COMPOSITE_FORMULA]` | How to combine dimension scores (sum, weighted sum) |
| `[INTERPRETATION_BANDS]` | Named bands for composite score ranges |
| `[CLUSTER_THRESHOLD]` | Minimum composite for cluster membership |
| `[TOP_N]` | Number of top pairs to highlight (10-20) |
| `[OUTPUT_PATH]` | Where to save the output file |

## Example Usages

**For Competitive Overlap** (see exemplar: `.cursor/exemplars/analysis/market/competitive-overlap-exemplar.md`):
- Analysis Type: Competitive Overlap
- Entities: Competitors + own company
- Dimensions: Product, Geography, Market Segment, Customer Base, Technology (K=5, 0-3 scale)
- Composite: 0-15, bands: Minimal/Moderate/Significant/Direct
- Reference Entity: Eneve (own company)

**For Technology Stack Overlap across Microservices**:
- Analysis Type: Technology Overlap
- Entities: Microservices in the system
- Dimensions: Language, Database, Messaging, Deployment, Shared Libraries (K=5, 0-3)
- Use: Identify services that can share infrastructure or teams

**For Team Skill Overlap (Resource Planning)**:
- Analysis Type: Skill Overlap
- Entities: Development teams
- Dimensions: Frontend, Backend, DevOps, Domain Knowledge, Testing (K=5, 0-3)
- Use: Identify teams that could cover for each other or merge

**For Feature Overlap across Product Lines**:
- Analysis Type: Feature Overlap
- Entities: Product lines or modules
- Dimensions: Core Features, UX Patterns, Data Model, Integration Points, Target Users (K=5, 0-3)
- Use: Identify consolidation opportunities or cannibalization risks

**For Vendor Pairwise Comparison**:
- Analysis Type: Vendor Similarity
- Entities: Candidate vendors
- Dimensions: Product Fit, Pricing Model, Support, Integration, Geography (K=5, 0-3)
- Use: Identify which vendors are interchangeable vs. differentiated

## Key Design Decisions

- **Symmetric matrix**: Overlap/similarity is bidirectional -- halves computation
- **Fixed 0-N rubric per dimension**: Prevents score inflation, enables consistent cross-pair comparison
- **Composite sum (not weighted average)**: Keeps model simple and auditable
- **Self-correction step**: Catches arithmetic and symmetry errors before output
- **Cluster identification**: Groups emerge naturally from mutual high scores
- **Strategic implications section**: The matrix is a means, not an end -- always derive actionable insights

## Related Templars

- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- Per-entity scoring (complementary, not overlapping)
- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- General guided research structure

## Related Exemplars

- `.cursor/exemplars/analysis/market/competitive-overlap-exemplar.md` -- Full implementation showing this pattern applied to competitive intelligence

---

**Extracted From**: `.cursor/prompts/analysis/market/research-competitive-overlap.prompt.md`
**Created**: 2026-02-17
