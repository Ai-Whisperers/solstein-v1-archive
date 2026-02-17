---
type: exemplar
artifact-type: prompt
demonstrates: pairwise scoring matrix with fixed rubrics, multi-mode invocation, self-correction validation, and strategic insight derivation
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-competitive-overlap.prompt.md
illustrates: pairwise-scoring-matrix
---

# Competitive Overlap Pairwise Assessment - Exemplar

## Artifact Type

**Type**: Prompt (analysis/market)

## Why This is Exemplary

This prompt is an outstanding implementation of the Pairwise Scoring Matrix pattern (`pairwise-scoring-matrix-templar.md`). It demonstrates how to take an abstract comparison framework and instantiate it with domain-specific rubrics, evidence-based scoring, and actionable strategic output.

## Key Quality Elements

1. **Rubric Precision**: Each of the 5 dimensions has a 4-level (0-3) rubric with concrete, measurable criteria. No vague adjectives -- every level has specific thresholds (e.g., "Share 2-3 overlapping capabilities but differ on others" for a score of 2).

2. **Self-Correction Loop**: Step 11 requires re-reading the output and verifying matrix symmetry, arithmetic, completeness, rubric compliance, evidence for max scores, and ranking consistency before declaring done. Catches errors that matrix-heavy outputs are prone to.

3. **Multi-Mode Invocation**: Supports Full Matrix, Eneve-Only, Tier-Filtered, and Delta Update modes -- demonstrating how a single prompt can serve different speed/depth trade-offs without duplicating prompt files.

4. **Evidence-Based Scoring**: Explicitly requires that every score of 3 (direct overlap) must cite specific evidence. Sparse data defaults to conservative (lower) scores. This prevents speculation-driven inflation.

5. **Strategic Derivation**: The prompt doesn't stop at the matrix. Steps 8-9 require cluster identification and strategic implications (geographic moats, M&A candidates, differentiation gaps). The matrix is a means, not an end.

6. **Exceptional Few-Shot Examples**: Three examples spanning the score range (high=10, low=2, moderate=9) with full rationale per dimension. Calibrates the scoring model and prevents drift.

7. **Comprehensive Troubleshooting**: Five problem-solution pairs covering large matrices, sparse data, asymmetric information, post-assembly score doubts, and delta merging.

## Pattern Demonstrated

**Pairwise Scoring Matrix**: Define N entities, K scoring dimensions with fixed rubrics, compute pairwise scores for all unique pairs, assemble symmetric N x N matrix, rank top pairs, identify clusters, derive implications.

Key instantiation decisions in this exemplar:
- K = 5 dimensions (Product, Geography, Market Segment, Customer Base, Technology)
- Scale = 0-3 per dimension (4 levels, not 10 -- appropriate granularity for qualitative assessment)
- Composite = simple sum (0-15 range)
- 4 interpretation bands (Minimal / Moderate / Significant / Direct head-to-head)
- Reference entity (Eneve) scored first as anchor

## Full Exemplar Content

### Dimension Rubrics (Exemplary Level of Detail)

Each dimension follows this pattern -- note the specificity of criteria:

**Dimension 1: Product Capability Overlap**

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different product categories (e.g., ETRM trading vs meter data only) |
| 1 | Adjacent | Related categories but different focus (e.g., front-office trading vs back-office settlement) |
| 2 | Partial overlap | Share 2-3 overlapping capabilities but differ on others (e.g., both do balancing but only one does nominations) |
| 3 | Direct competitor | Core product suites overlap on 4+ capabilities (e.g., both do time series, balancing, settlement, nominations) |

**Dimension 2: Geographic Overlap**

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different regions (e.g., Nordics-only vs Iberia-only) |
| 1 | Adjacent | Neighbouring regions with potential expansion overlap (e.g., DACH vs Benelux) |
| 2 | Partial overlap | Share 1-2 active countries or one operates where the other is expanding |
| 3 | Direct overlap | Both actively operate in 3+ shared countries or in the same national market |

**Dimension 3: Market Segment Overlap**

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Different segments entirely (e.g., wholesale trading vs retail billing) |
| 1 | Adjacent | Related segments (e.g., wholesale trading vs balancing services) |
| 2 | Partial overlap | Share 1-2 segments but differ on others (e.g., both do balancing but one is retail-focused) |
| 3 | Direct overlap | Target the same 3+ segments (e.g., both serve wholesale trading, balancing, and nominations) |

**Dimension 4: Customer Base Overlap**

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Completely different buyer types (e.g., TSOs vs residential consumers) |
| 1 | Adjacent | Related buyers in the same value chain (e.g., TSOs vs DSOs) |
| 2 | Partial overlap | Serve some of the same customer types (e.g., both serve suppliers, but one also serves traders) |
| 3 | Direct overlap | Competing for the same buyer personas -- suppliers, BRPs, traders -- in the same markets |

**Dimension 5: Technology Overlap**

| Score | Label | Criteria |
| --- | --- | --- |
| 0 | No overlap | Fundamentally different platforms (e.g., cloud-native SaaS vs mainframe) |
| 1 | Adjacent | Same generation but different stacks (e.g., both modern web but different languages) |
| 2 | Partial overlap | Shared stack elements enabling some migration (e.g., both .NET, both SQL-based) |
| 3 | Direct overlap | Very similar stacks -- migration between them is technically straightforward |

### Few-Shot Examples (Exemplary Calibration)

**Example 1: Eneve vs SOPTIM (Expected High Overlap -- Composite 10)**

| Dimension | Score | Rationale |
| --- | --- | --- |
| Product | 3 | Both offer balancing, scheduling, nominations, TSO communication -- core back-office suite |
| Geography | 1 | Eneve = NL/BE, SOPTIM = DE. Adjacent DACH/Benelux markets, no shared country yet |
| Market Segment | 3 | Both target wholesale market operations, balancing services, nominations/scheduling |
| Customer Base | 2 | Both serve suppliers and BRPs, but in different national markets |
| Technology | 1 | Both modern platforms but different stacks (MSSQL/.NET vs SOPTIM's cloud-native Java) |
| **Composite** | **10** | **Significant overlap -- closest functional twin, separated mainly by geography** |

**Example 2: Eneve vs Octopus/Kraken (Expected Low Overlap -- Composite 2)**

| Dimension | Score | Rationale |
| --- | --- | --- |
| Product | 1 | Kraken is utility CRM/billing/demand response; Eneve is market operations/back-office. Adjacent but different |
| Geography | 1 | Kraken has Rotterdam hub (Jedlix) but targets consumers, not wholesale market |
| Market Segment | 0 | Kraken = retail energy, demand response. Eneve = wholesale balancing, nominations |
| Customer Base | 0 | Kraken serves utilities/retailers. Eneve serves suppliers/BRPs/market participants |
| Technology | 0 | Kraken is cloud-native Python/K8s. Eneve is on-prem MSSQL/.NET |
| **Composite** | **2** | **Minimal overlap -- different competitive space despite both being "energy software"** |

**Example 3: Volue vs KISTERS (Expected Moderate Overlap -- Composite 9)**

| Dimension | Score | Rationale |
| --- | --- | --- |
| Product | 2 | Both offer energy management and forecasting, but Volue is broader (trading + hydro) while KISTERS is deeper in time series |
| Geography | 2 | Both active in DACH + Nordics, with some shared customers |
| Market Segment | 2 | Both serve wholesale trading and balancing, but Volue adds hydro optimization |
| Customer Base | 2 | Both serve utilities and grid operators in Northern Europe |
| Technology | 1 | Both modernising toward cloud, but different legacy bases |
| **Composite** | **9** | **Significant overlap -- competing in Northern European energy management** |

### Self-Correction Validation (Exemplary Practice)

The prompt requires this explicit validation pass before finalising:

1. **Matrix symmetry**: Score(A,B) equals Score(B,A) for every pair
2. **Arithmetic**: Every composite equals the sum of its 5 dimension scores
3. **Completeness**: Every competitor from the roster appears in the matrix
4. **Rubric compliance**: No score exceeds 3 or falls below 0 on any dimension
5. **Evidence for 3s**: Every direct-overlap score (3) has a cited rationale
6. **Ranking consistency**: Top-15 pairs and Eneve rankings match the matrix values

### Output Structure (Exemplary Completeness)

The output specification includes these sections -- note how it goes beyond the matrix to strategic value:

1. Scoring Rubric Summary (reference for readers)
2. Eneve Self-Assessment (anchor before comparisons)
3. Eneve Overlap Rankings (focused strategic view)
4. Top 15 Most Overlapping Pairs (market-wide view)
5. Full N x N Matrix (complete data)
6. Overlap Clusters (emergent groupings)
7. Dimension Heatmaps (Mermaid visualisation)
8. Strategic Implications (the payoff -- moats, M&A candidates, differentiation)
9. Data Confidence Notes (honest about limitations)
10. Methodology (reproducibility)

### Multi-Mode Design (Exemplary Flexibility)

Four modes from a single prompt, each with clear use case:

| Mode | Use Case | Output |
| --- | --- | --- |
| Full Matrix (default) | Complete strategic analysis | N x N matrix + all sections |
| `--eneve-only` | Quick strategic review | Single ranked column |
| `--tier N` | Focused tier analysis | Reduced matrix for readability |
| `--delta` | Incremental update | Re-scored pairs merged into existing file |

## Learning Points

- **Fixed rubric scale prevents drift**: Using 0-3 with explicit criteria per level is more consistent than asking the AI to "rate overlap on a scale of 1-10" where scoring drifts between pairs.
- **Self-correction is essential for matrices**: N x N outputs are prone to symmetry errors, arithmetic mistakes, and missing entities. An explicit validation pass catches these.
- **Strategic implications are the real deliverable**: The matrix is infrastructure; the clusters, moats, and recommendations are what decision-makers act on. Always include a "so what" section.
- **Multi-mode design avoids prompt proliferation**: Rather than four separate prompts, one prompt with argument-driven modes keeps the library compact.
- **Evidence gating for max scores**: Requiring cited rationale for top scores prevents the AI from casually handing out 3s, improving overall score calibration.
- **Conservative scoring for sparse data**: Explicitly instructing the AI to default low when data is missing prevents overconfident assessments.

## When to Reference

Use this exemplar when:

- Creating a new pairwise comparison prompt for any domain
- Designing rubrics for qualitative multi-dimensional scoring
- Adding self-correction validation to matrix-heavy outputs
- Implementing multi-mode prompt design (same prompt, different scopes)
- Building strategic analysis prompts that go beyond data tables to implications

## Related Exemplars

- `.cursor/exemplars/analysis/market/financial-dashboard-exemplar.md` -- Complementary per-entity ranking view
- `.cursor/exemplars/analysis/market/research-competitor-exemplar.md` -- Per-entity deep-dive (produces input data for overlap analysis)
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` -- Per-entity scorecard pattern (different from pairwise)

## Related Templars

- `.cursor/templars/analysis/market/pairwise-scoring-matrix-templar.md` -- The abstract structural pattern this exemplar demonstrates
- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- Per-entity scoring (complementary)

---

**Extracted From**: `.cursor/prompts/analysis/market/research-competitive-overlap.prompt.md`
**Created**: 2026-02-17
