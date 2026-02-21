---
name: research-competitive-overlap
description: "Please produce a pairwise competitive overlap assessment matrix across all tracked competitors"
category: analysis
tags: competition, overlap, pairwise, matrix, heatmap, market-segments, geography
argument-hint: "Optional: --eneve-only | --tier 1 | --delta | (no args = full matrix)"
model: GPT-4
tools:
  - search/codebase
  - fileSystem
  - web/*
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Research Competitive Overlap - Pairwise Assessment Matrix

Please produce a pairwise competitive overlap assessment across all tracked competitors in `tickets/COMPETITION/`. For every pair of competitors (including Eneve), score overlap on 5 dimensions, compute a composite score, and generate a full N x N matrix plus a ranked list of the most overlapping pairs.

**Pattern**: Guided Analysis Pattern ⭐⭐⭐⭐⭐  
**Effectiveness**: Reveals which competitors actually fight over the same customers, geographies, and capabilities -- not just which ones exist in "energy software"  
**Use When**: After individual competitor profiles exist (via `research-competitor`) and before strategic positioning or M&A analysis

---

## Purpose

Individual competitor profiles describe each company in isolation. The financial dashboard ranks them by growth. But neither answers the critical strategic question: **which competitors actually overlap with each other, and with Eneve, on the dimensions that matter?**

Without this prompt:

- All competitors appear equally threatening, regardless of whether they target the same customers
- Geographic moats and product niches are invisible in flat leaderboards
- Strategic decisions lack a pairwise comparison basis (e.g., "Who should we worry about in NL gas balancing?")
- M&A overlap analysis has no data foundation

This prompt produces `tickets/COMPETITION/competitive-overlap.md` with a full N x N matrix.

---

## Required Context

- **Competitor profiles**: `tickets/COMPETITION/[company-slug]/` folders containing identification files, deep-analysis, or financial-growth data
- **Eneve positioning**: `tickets/COMPETITION/README.md` for Eneve's capabilities, markets, and platform details
- **Quick-Reference Comparison Matrix**: The capability matrix in README.md for cross-checking product overlap

No arguments required for full mode. The prompt scans all competitor sub-folders automatically.

---

## Usage Modes

### Full Matrix (Default)

Score every pair across all tracked competitors. Produces the complete N x N matrix.

```text
@research-competitive-overlap
```

### Eneve-Only Focus

Score only Eneve's overlap with each competitor. Faster, produces a single ranked column instead of a full matrix.

```text
@research-competitive-overlap --eneve-only
```

### Tier-Filtered

Score only competitors in a specific tier (reduces matrix size for readability).

```text
@research-competitive-overlap --tier 1
@research-competitive-overlap --tier 1b
```

### Delta Update

Re-score only pairs involving newly added or recently updated competitor profiles. Merges results into an existing `competitive-overlap.md`.

```text
@research-competitive-overlap --delta
```

---

## Overlap Dimensions (5)

Each dimension is scored independently per pair.

### Dimension 1: Product Capability Overlap

Do the two competitors offer the same types of modules?

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different product categories (e.g., ETRM trading vs meter data only) |
| 1 | Adjacent | Related categories but different focus (e.g., front-office trading vs back-office settlement) |
| 2 | Partial overlap | Share 2-3 overlapping capabilities but differ on others (e.g., both do balancing but only one does nominations) |
| 3 | Direct competitor | Core product suites overlap on 4+ capabilities (e.g., both do time series, balancing, settlement, nominations) |

### Dimension 2: Geographic Overlap

Do the two competitors operate in the same countries or regions?

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different regions (e.g., Nordics-only vs Iberia-only) |
| 1 | Adjacent | Neighbouring regions with potential expansion overlap (e.g., DACH vs Benelux) |
| 2 | Partial overlap | Share 1-2 active countries or one operates where the other is expanding |
| 3 | Direct overlap | Both actively operate in 3+ shared countries or in the same national market |

### Dimension 3: Market Segment Overlap

Do the two competitors target the same market segments?

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Different segments entirely (e.g., wholesale trading vs retail billing) |
| 1 | Adjacent | Related segments (e.g., wholesale trading vs balancing services) |
| 2 | Partial overlap | Share 1-2 segments but differ on others (e.g., both do balancing but one is retail-focused) |
| 3 | Direct overlap | Target the same 3+ segments (e.g., both serve wholesale trading, balancing, and nominations) |

### Dimension 4: Customer Base Overlap

Do the two competitors compete for the same buyer personas?

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different buyer types (e.g., TSOs vs residential consumers) |
| 1 | Adjacent | Related buyers in the same value chain (e.g., TSOs vs DSOs) |
| 2 | Partial overlap | Serve some of the same customer types (e.g., both serve suppliers, but one also serves traders) |
| 3 | Direct overlap | Competing for the same buyer personas -- suppliers, BRPs, traders -- in the same markets |

### Dimension 5: Technology Overlap

Do the two competitors use similar technology stacks that could enable competitive switching?

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Fundamentally different platforms (e.g., cloud-native SaaS vs mainframe) |
| 1 | Adjacent | Same generation but different stacks (e.g., both modern web but different languages) |
| 2 | Partial overlap | Shared stack elements enabling some migration (e.g., both .NET, both SQL-based) |
| 3 | Direct overlap | Very similar stacks -- migration between them is technically straightforward |

---

## Composite Overlap Score

For each pair (A, B):

```text
Composite = Product + Geography + MarketSegment + CustomerBase + Technology
```

- **Range**: 0-15
- **Interpretation**:
  - 0-3: Minimal overlap -- different competitive space
  - 4-7: Moderate overlap -- watch for convergence
  - 8-11: Significant overlap -- active competitive pressure
  - 12-15: Direct head-to-head -- fighting for the same business

---

## Process

### Step 1: Build Competitor Roster

Read `tickets/COMPETITION/README.md` and build the full list of tracked competitors across all tiers. Include Eneve as row/column 0.

### Step 2: Read All Competitor Profiles

For each competitor, read available files (`[slug].md`, `deep-analysis.md`, `financial-growth.md`) and extract:

- Product capabilities / modules offered
- Countries of active operation
- Market segments served (wholesale, retail, balancing, nominations, grid, etc.)
- Target customer types (TSOs, DSOs, suppliers, traders, BRPs, retailers)
- Technology stack (languages, databases, deployment model)

### Step 3: Score Eneve's Self-Assessment

Before scoring pairs, explicitly document Eneve's own profile on each dimension:

| Dimension | Eneve Profile |
| --- | --- |
| Product | Time series, balancing, settlement, nominations, scheduling, TSO comms, smart meter, market ops |
| Geography | Netherlands (primary), Belgium (expanding) |
| Market Segment | Wholesale market operations, balancing, nominations/scheduling |
| Customer Base | Suppliers, BRPs, market participants in NL energy market |
| Technology | MSSQL, on-premise, migrating to C#/.NET |

### Step 4: Score Pairwise Overlaps

For each unique pair (A, B) where A < B in the roster:

1. Score each of the 5 dimensions (0-3) using the rubrics above
2. Compute composite (sum of 5 scores)
3. Record rationale for any score of 3 (direct overlap)

Scoring should be based on evidence from competitor profiles, not speculation. Where data is sparse, score conservatively (lower) and note the uncertainty.

### Step 5: Assemble N x N Matrix

Build the full matrix with competitors on both axes. The matrix is symmetric (overlap A-B = overlap B-A), so only compute the upper triangle. Diagonal is N/A (self-overlap).

### Step 6: Rank Top Overlapping Pairs

Extract all pairs sorted by composite score descending. Highlight the top 15 most overlapping pairs.

### Step 7: Extract Eneve's Overlap Profile

Create a dedicated section showing Eneve's overlap with every competitor, sorted by composite score descending. This answers: "Who is Eneve most directly competing with?"

### Step 8: Generate Visualisation Template

Include a Mermaid chord diagram or heatmap template that can be populated from the matrix data.

### Step 9: Derive Strategic Implications

From the overlap data, extract actionable strategic insights:

- Which competitors form natural clusters fighting for the same customers?
- Where does Eneve have a geographic moat (high product overlap but low geo overlap)?
- Which competitive pairs suggest potential M&A consolidation?
- Where should Eneve invest in differentiation vs. where is the competitive space already clear?

### Step 10: Write Output

Save all results to `tickets/COMPETITION/competitive-overlap.md`.

### Step 11: Self-Correction Validation

Before finalising, re-read the output file and verify:

1. **Matrix symmetry**: Score(A,B) equals Score(B,A) for every pair
2. **Arithmetic**: Every composite equals the sum of its 5 dimension scores
3. **Completeness**: Every competitor from the roster appears in the matrix
4. **Rubric compliance**: No score exceeds 3 or falls below 0 on any dimension
5. **Evidence for 3s**: Every direct-overlap score (3) has a cited rationale
6. **Ranking consistency**: Top-15 pairs and Eneve rankings match the matrix values

If any check fails, fix the error before declaring the output complete.

---

## Output Format

Generate the complete file `tickets/COMPETITION/competitive-overlap.md` with this structure:

````markdown
# Competitive Overlap Matrix

**Generated**: YYYY-MM-DD
**Competitors Assessed**: [N] (including Eneve)
**Data Source**: Per-competitor profiles via `research-competitor` prompt
**Scoring**: 5 dimensions x 0-3 scale = 0-15 composite per pair

---

## Scoring Rubric Summary

| Score | Label | Meaning |
| --- | --- | --- |
| 0 | No overlap | Different competitive space |
| 1 | Adjacent | Related but distinct |
| 2 | Partial overlap | Shared ground in some areas |
| 3 | Direct competitor | Head-to-head on this dimension |

**Composite**: Sum of 5 dimensions (0-15)
- 0-3: Minimal overlap
- 4-7: Moderate overlap
- 8-11: Significant overlap
- 12-15: Direct head-to-head

---

## Eneve Self-Assessment

| Dimension | Eneve Profile |
| --- | --- |
| Product | [capabilities] |
| Geography | [countries] |
| Market Segment | [segments] |
| Customer Base | [buyer types] |
| Technology | [stack] |

---

## Eneve Overlap Rankings

Eneve's overlap with each competitor, sorted by composite score:

| Rank | Competitor | Tier | Product | Geo | Segment | Customer | Tech | Composite | Threat Level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [company] | [tier] | [0-3] | [0-3] | [0-3] | [0-3] | [0-3] | [0-15] | [Direct/Significant/Moderate/Minimal] |
| 2 | [company] | [tier] | [0-3] | [0-3] | [0-3] | [0-3] | [0-3] | [0-15] | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Top 15 Most Overlapping Pairs (All Competitors)

| Rank | Competitor A | Competitor B | Product | Geo | Segment | Customer | Tech | Composite |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [company] | [company] | [0-3] | [0-3] | [0-3] | [0-3] | [0-3] | [0-15] |
| 2 | [company] | [company] | [0-3] | [0-3] | [0-3] | [0-3] | [0-3] | [0-15] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Full N x N Overlap Matrix (Composite Scores)

|  | Eneve | SOPTIM | Trayport | Brady | Volue | KISTERS | ... |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Eneve** | -- | [score] | [score] | [score] | [score] | [score] | ... |
| **SOPTIM** | [score] | -- | [score] | [score] | [score] | [score] | ... |
| **Trayport** | [score] | [score] | -- | [score] | [score] | [score] | ... |
| ... | ... | ... | ... | ... | ... | ... | ... |

> Symmetric matrix. Diagonal is self (--). Scores range 0-15.

---

## Overlap Clusters

Based on composite scores >= 8 (significant overlap), the following competitive clusters emerge:

### Cluster 1: [Name] (e.g., "NL Energy Back-Office")
- Members: [list]
- Shared dimensions: [which dimensions drive the clustering]
- Competitive dynamic: [brief description]

### Cluster 2: [Name]
- Members: [list]
- Shared dimensions: [list]
- Competitive dynamic: [brief description]

---

## Dimension Heatmaps

### Product Overlap Heatmap

```mermaid
quadrantChart
    title "Product Overlap: Core Back-Office vs Broader ETRM"
    x-axis "Narrow Back-Office" --> "Broad ETRM"
    y-axis "Few Modules" --> "Full Suite"
    quadrant-1 "Full-Suite Back-Office"
    quadrant-2 "Full-Suite ETRM"
    quadrant-3 "Niche Back-Office"
    quadrant-4 "Niche ETRM"
    Eneve: [x, y]
    SOPTIM: [x, y]
    KISTERS: [x, y]
```

> Position each competitor based on product breadth (X) and back-office vs trading focus (Y).

---

## Strategic Implications

### Eneve's Competitive Position
- **Closest functional twin(s)**: [Competitor(s) with highest Eneve overlap, what drives it]
- **Geographic moat**: [Competitors with high product overlap but low geo overlap -- potential future threats if they expand]
- **Clear space**: [Dimensions where Eneve faces minimal competition]

### Market Dynamics
- **Consolidation candidates**: [Pairs with composite >= 12 that might merge or acquire each other]
- **Convergence risks**: [Pairs currently at 4-7 that are trending upward based on expansion plans]
- **Differentiation opportunities**: [Gaps in the matrix where no competitor scores highly -- potential blue ocean]

### Recommended Actions
1. [Action based on highest-overlap competitor]
2. [Action based on cluster dynamics]
3. [Action based on geographic moat preservation or expansion]

---

## Data Confidence Notes

- [Note any competitors with sparse profiles where scores are low-confidence]
- [Note where web research was used to supplement profile data]
- [Note any scoring assumptions or judgment calls]

---

## Methodology

- **Dimensions**: 5 (Product, Geography, Market Segment, Customer Base, Technology)
- **Scale**: 0-3 per dimension (see rubric above)
- **Composite**: Sum of 5 dimensions (0-15)
- **Data sources**: Per-competitor profiles in `tickets/COMPETITION/[slug]/`, README.md capability matrix
- **Symmetry**: Overlap(A,B) = Overlap(B,A)
- **Eneve**: Scored as a row/column using README.md positioning data
````

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Check mode**: Determine if running in Full, Eneve-Only, Tier-Filtered, or Delta mode based on arguments
2. **Read README.md first**: Build the full competitor roster and understand Eneve's positioning
3. **Scan all competitor folders**: Extract product, geography, segment, customer, and technology data from available files
4. **Score Eneve first**: Document Eneve's self-assessment explicitly before starting pairwise comparisons
5. **Score systematically**: Work through pairs in a consistent order (row by row in the matrix)
6. **Be evidence-based**: Every score of 3 (direct overlap) should cite specific capability matches or shared countries
7. **Score conservatively**: Where data is sparse, prefer lower scores and note uncertainty
8. **Identify clusters**: After scoring, look for groups of 3+ competitors with mutual high overlap
9. **Derive strategic implications**: Extract actionable insights from the overlap patterns -- don't stop at the matrix
10. **Write and self-correct**: Generate the output file, then re-read to verify matrix symmetry, score arithmetic, and completeness before declaring done

---

## Examples (Few-Shot)

### Calibration Example: Eneve vs SOPTIM (High Overlap = 10/15)

| Dimension | Score | Rationale |
| --- | --- | --- |
| Product | 3 | Both offer balancing, scheduling, nominations, TSO communication -- core back-office suite |
| Geography | 1 | Eneve = NL/BE, SOPTIM = DE. Adjacent DACH/Benelux markets, no shared country yet |
| Market Segment | 3 | Both target wholesale market operations, balancing services, nominations/scheduling |
| Customer Base | 2 | Both serve suppliers and BRPs, but in different national markets |
| Technology | 1 | Both modern platforms but different stacks (MSSQL/.NET vs SOPTIM's cloud-native Java) |
| **Composite** | **10** | **Significant overlap -- closest functional twin, separated mainly by geography** |

> **Full Few-Shot set** (high/low/moderate examples with rationale): See `.cursor/exemplars/analysis/market/competitive-overlap-exemplar.md`

---

## Troubleshooting

Common issues (large matrices, sparse data, asymmetric information, score doubts, delta merging) are documented with solutions in the exemplar.

> **Full troubleshooting guide**: See `.cursor/exemplars/analysis/market/competitive-overlap-exemplar.md`

**Quick rules**:
- Sparse data: score conservatively (0-1), mark with `*`, note in Data Confidence
- Large matrices: generate full matrix but create sub-matrix for visual display (Tier 1 + 1b only)
- Delta mode: re-score only affected pairs, replace rows/columns, re-rank, update date

---

## Quality Criteria

### Completeness

- [ ] All tracked competitors from README.md included in the matrix
- [ ] Eneve included as row/column with explicit self-assessment
- [ ] All 5 overlap dimensions scored for every pair
- [ ] Top 15 most overlapping pairs identified and ranked
- [ ] Eneve's overlap with each competitor ranked separately
- [ ] Overlap clusters identified (groups with mutual composite >= 8)
- [ ] Strategic Implications section completed with actionable recommendations

### Correctness

- [ ] Scoring rubric (0-3 per dimension) consistently applied
- [ ] Composite scores computed correctly (sum of 5 dimensions, 0-15 range)
- [ ] Matrix is symmetric (score A-B equals score B-A)
- [ ] Every score of 3 (direct overlap) has a cited rationale
- [ ] No speculative scores above 1 without supporting evidence from profiles

### Output Quality

- [ ] At least one Mermaid visualisation included
- [ ] Data confidence notes document any low-confidence scores
- [ ] Output saved to `tickets/COMPETITION/competitive-overlap.md`
- [ ] Self-correction validation passed (symmetry, arithmetic, completeness)

---

## Usage

**Full matrix** (all competitors, all pairs):

```text
@research-competitive-overlap
```

**Eneve-only** (just Eneve's row, faster for strategic review):

```text
@research-competitive-overlap --eneve-only
```

**Tier-filtered** (reduce matrix to a specific tier for readability):

```text
@research-competitive-overlap --tier 1
```

**Delta update** (re-score only new/changed profiles, merge into existing file):

```text
@research-competitive-overlap --delta
```

---

## Related Prompts

- `analysis/market/research-competitor.prompt.md` -- Per-competitor deep analysis (produces the input data for this prompt)
- `analysis/market/generate-financial-dashboard.prompt.md` -- Financial growth rankings (complementary view)
- `analysis/market/assess-data-confidence.prompt.md` -- Data quality scoring (helps interpret low-confidence overlap scores)
- `analysis/market/research-customer-intelligence.prompt.md` -- Customer base analysis (feeds Dimension 4)
- `analysis/market/research-market-trends.prompt.md` -- Market segment trends (feeds Dimension 3)

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` -- Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` -- Registry format requirements

---

## Pattern Used

This prompt follows the **Pairwise Scoring Matrix** pattern: `.cursor/templars/analysis/market/pairwise-scoring-matrix-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/competitive-overlap-exemplar.md`

---

**Created**: 2026-02-17  
**Improved**: 2026-02-17 (improve-prompt + enhance-prompt pass)  
**Extracted**: 2026-02-17 (templar + exemplar extraction via `extract-templar-exemplar`)  
**Context**: tickets/FINANCIALDASHBOARD/FD-026-competitive-overlap-prompt (feeds FD-016 Competitive Overlap Heatmap)  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
