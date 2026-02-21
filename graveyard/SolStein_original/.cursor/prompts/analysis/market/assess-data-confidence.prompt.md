---
name: assess-data-confidence
description: "Please assess data confidence across all researched competitors and produce per-competitor quality scores"
category: analysis
tags: competition, data-quality, confidence, completeness, dashboard, scoring
argument-hint: "No arguments needed -- scans all competitor folders in tickets/COMPETITION/"
tools:
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Assess Data Confidence - Per-Competitor Quality Scoring

Please perform a systematic data-confidence assessment across all researched competitors in `tickets/COMPETITION/`. For each competitor, score data quality on 5 dimensions, compute a composite confidence score, and generate a prioritized action list showing where further research is needed.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Turns scattered research files into a single confidence map that tells decision-makers which data they can trust
**Use When**: After running research prompts (identification, deep-analysis, financial-growth, corporate-history) and before generating dashboards or making strategic decisions

---

## Purpose

Individual research prompts tag data points as Confirmed / Estimated / Unknown, but nothing aggregates these signals into an overall confidence picture per competitor. Without this prompt:

- The financial dashboard presents all competitors as equally well-researched, which is misleading
- Decision-makers cannot distinguish reliable data from rough estimates
- Nobody knows which competitors need more research and which prompts to run next

This prompt closes that gap by producing a single `tickets/COMPETITION/data-confidence.md` report.

---

## Required Context

- **Competitor folders**: `tickets/COMPETITION/[company-slug]/` -- each folder may contain:
  - `[company-slug].md` -- identification file
  - `deep-analysis.md` -- deep-dive research
  - `financial-growth.md` -- financial and growth metrics
  - `corporate-history.md` -- corporate genealogy
- **Eneve positioning**: `tickets/COMPETITION/README.md` -- competitor list and data-collection status table

No arguments required. The prompt scans all competitor sub-folders automatically.

---

## Process

### Step 1: Enumerate Competitors

Read `tickets/COMPETITION/README.md` and list all sub-folders in `tickets/COMPETITION/` that represent competitors (exclude non-competitor folders like `protocols/`, `.cache/`).

### Step 2: Inventory Files Per Competitor

For each competitor folder, check which of the following files exist:

| File | Research Prompt |
|---|---|
| `[slug].md` | Initial identification |
| `deep-analysis.md` | `research-competitor` |
| `financial-growth.md` | `research-financial-growth` |
| `corporate-history.md` | `research-company-history` |

Record presence/absence. This feeds the Research Depth dimension.

### Step 3: Score Each Competitor on 5 Dimensions

For every competitor, read all available files and assign a score from 1-10 on each dimension using the rubric below.

### Step 4: Compute Composite Score

Calculate the **Composite Confidence Score** as the simple average of the 5 dimension scores, rounded to one decimal.

### Step 5: Classify Traffic Light

Apply the traffic-light classification:

| Range | Label | Meaning |
|---|---|---|
| 7.0 -- 10.0 | **High** | Data is reliable enough for strategic decisions |
| 4.0 -- 6.9 | **Medium** | Data is directionally useful but has gaps |
| 1.0 -- 3.9 | **Low** | Data is too thin for confident conclusions |

### Step 6: Generate Action Items

For each competitor scoring Medium or Low, recommend:
- Which specific research prompts to run next
- Which dimensions are weakest and why
- Priority order (lowest-scoring competitors first)

### Step 7: Write Output

Write the full report to `tickets/COMPETITION/data-confidence.md`.

---

## Scoring Rubric (1-10 Scale)

### Dimension 1: Completeness

How many expected data fields are filled vs blank/Unknown?

| Score | Criteria |
|---|---|
| 9-10 | 90%+ of standard data fields filled across all research files |
| 7-8 | 70-89% filled; minor gaps in secondary categories |
| 5-6 | 50-69% filled; one or more major categories have significant gaps |
| 3-4 | 30-49% filled; only basic identification data available |
| 1-2 | <30% filled; barely more than a company name |

**Standard data fields** (from research prompts):
- Company fundamentals (name, HQ, founded, employees, revenue, ownership)
- Market position (countries, customers, rankings)
- Product & technology (portfolio, tech stack, deployment model)
- AI & innovation (features, hiring, partnerships)
- Growth trajectory (revenue growth, employee growth, funding, M&A)
- Commodities & specialization (commodities, protocols, compliance)
- Pricing & business model (model, price range, implementation timeline)

### Dimension 2: Source Quality

What percentage of data points come from primary sources vs estimates or guesses?

| Score | Criteria |
|---|---|
| 9-10 | 80%+ from primary sources (annual reports, SEC filings, official website) |
| 7-8 | 60-79% primary; remaining from credible secondary sources (LinkedIn, Crunchbase) |
| 5-6 | 40-59% primary; significant reliance on analyst estimates or news articles |
| 3-4 | 20-39% primary; mostly secondary sources or single-source claims |
| 1-2 | <20% primary; data is mostly estimated or unattributed |

**Primary sources**: Annual reports, SEC/trade register filings, official company pages, investor presentations.
**Secondary sources**: LinkedIn, Crunchbase, news articles, analyst estimates, job postings.

### Dimension 3: Recency

How current is the data?

| Score | Criteria |
|---|---|
| 9-10 | Core data from current year or last 6 months |
| 7-8 | Core data from within the last 12 months |
| 5-6 | Core data is 1-2 years old; some metrics outdated |
| 3-4 | Core data is 2-3 years old |
| 1-2 | Core data is 3+ years old or undated |

**Core data** = revenue, employee count, product capabilities, market presence.

### Dimension 4: Consistency

Do different research files agree, or are there contradictions?

| Score | Criteria |
|---|---|
| 9-10 | All files agree; no contradictions detected |
| 7-8 | Minor discrepancies in non-critical fields (e.g., employee count differs by <10%) |
| 5-6 | Some contradictions in important fields; sources disagree on revenue or key dates |
| 3-4 | Significant contradictions; different files present conflicting pictures |
| 1-2 | Major conflicts across files; data cannot be reconciled without further research |

**Check for**: Revenue figures across files, employee counts, founding dates, ownership claims, product capabilities described differently.

### Dimension 5: Research Depth

How many research prompts have been run for this competitor?

| Score | Criteria |
|---|---|
| 9-10 | All 4 research files present (identification + deep-analysis + financial-growth + corporate-history) |
| 7-8 | 3 of 4 research files present |
| 5-6 | 2 of 4 research files present (e.g., identification + one deep-dive) |
| 3-4 | Only 1 research file present (identification only) |
| 1-2 | No dedicated research file; competitor mentioned only in cross-references |

---

## Output Format

Write the output to `tickets/COMPETITION/data-confidence.md`:

```markdown
# Data Confidence Assessment

**Assessment Date**: YYYY-MM-DD
**Competitors Assessed**: [count]
**Methodology**: 5-dimension scoring (1-10 scale), composite average, traffic-light classification

## Summary

| Confidence Level | Count | Competitors |
|---|---|---|
| High (7-10) | [n] | [list] |
| Medium (4-6) | [n] | [list] |
| Low (1-3) | [n] | [list] |

## Per-Competitor Scores

| Competitor | Completeness | Source Quality | Recency | Consistency | Research Depth | Composite | Confidence |
|---|---|---|---|---|---|---|---|
| [Company 1] | [1-10] | [1-10] | [1-10] | [1-10] | [1-10] | [avg] | High/Medium/Low |
| [Company 2] | [1-10] | [1-10] | [1-10] | [1-10] | [1-10] | [avg] | High/Medium/Low |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Dimension Analysis

### Strongest Dimension Across All Competitors
[Which dimension scores highest on average and why]

### Weakest Dimension Across All Competitors
[Which dimension scores lowest on average and what to do about it]

### Distribution
- Average Composite Score: [value]
- Highest: [company] ([score])
- Lowest: [company] ([score])
- Standard Deviation: [value]

## Action Items (Prioritized)

### Priority 1: Critical Research Gaps (Low Confidence)

| Competitor | Composite | Weakest Dimension | Recommended Action |
|---|---|---|---|
| [Company] | [score] | [dimension] | Run `[prompt-name]` to address [gap] |
| ... | ... | ... | ... |

### Priority 2: Moderate Gaps (Medium Confidence)

| Competitor | Composite | Weakest Dimension | Recommended Action |
|---|---|---|---|
| [Company] | [score] | [dimension] | Run `[prompt-name]` to address [gap] |
| ... | ... | ... | ... |

### Priority 3: Refresh Needed (High Confidence but aging)

| Competitor | Composite | Recency Score | Recommended Action |
|---|---|---|---|
| [Company] | [score] | [recency] | Re-run `[prompt-name]` to refresh [data] |
| ... | ... | ... | ... |

## Scoring Notes

[Per-competitor notes explaining non-obvious scores or special circumstances, e.g., "Private company -- financial data inherently limited, Completeness score reflects data availability, not research effort."]
```

---

## Examples (Few-Shot)

See exemplar for two detailed scoring walkthroughs (well-researched competitor scoring High, thinly-researched competitor scoring Medium): `.cursor/exemplars/analysis/market/data-confidence-assessment-exemplar.md`

---

## Quality Criteria

- [ ] All competitor sub-folders in `tickets/COMPETITION/` scanned
- [ ] Each competitor scored on all 5 dimensions with 1-10 values
- [ ] Every score justified against the rubric criteria (not assigned arbitrarily)
- [ ] Composite score correctly computed as simple average of 5 dimensions, rounded to 1 decimal
- [ ] Traffic-light classification applied per the defined ranges (High 7-10, Medium 4-6.9, Low 1-3.9)
- [ ] Summary table competitor counts match the per-competitor table row count
- [ ] Action items specify which prompt to run and what gap it fills
- [ ] Action items sorted by priority (lowest confidence first)
- [ ] Scoring notes provided for every non-obvious rating (especially private companies, single-file competitors)
- [ ] Output written to `tickets/COMPETITION/data-confidence.md`

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Enumerate**: List all competitor sub-folders in `tickets/COMPETITION/`
2. **Inventory**: For each competitor, check which research files exist
3. **Read**: For each competitor, read all available research files
4. **Score**: Apply the rubric systematically -- dimension by dimension, competitor by competitor
5. **Compute**: Calculate composite scores and assign traffic-light levels
6. **Prioritize**: Sort action items by composite score ascending (worst first)
7. **Write**: Produce the output file in the specified format
8. **Cross-check**: Verify every competitor has a row in the table and every low-scorer has an action item

### Self-Correction (before finalizing output)

After drafting the full report, review your own work:

- **Rubric adherence**: Re-read each dimension score and confirm it falls within the rubric's criteria band. If you scored Completeness as 7, verify that 70-89% of standard data fields are actually filled.
- **Arithmetic**: Recalculate every composite score. Confirm the traffic-light label matches the composite range.
- **Coverage**: Count rows in the per-competitor table and compare to the competitor enumeration in Step 1. Every competitor must appear exactly once.
- **Action item completeness**: Every competitor with Medium or Low confidence must have at least one action item. High-confidence competitors with low Recency scores should appear in Priority 3.
- **Internal consistency**: If you scored Consistency as 9 but noted contradictions in the Scoring Notes, re-examine and adjust.

---

## Troubleshooting

See exemplar for 7 detailed troubleshooting entries (empty folders, private companies, contradictions, stubs, renames): `.cursor/exemplars/analysis/market/data-confidence-assessment-exemplar.md`

---

## Usage

### Full Assessment (standard)

```
@assess-data-confidence
```

No arguments needed. Scans all competitor folders and produces the complete report.

### Re-Assessment After New Research

After running additional research prompts for specific competitors, re-run the same command to regenerate the report with updated scores:

```
@assess-data-confidence
```

Compare the new composite scores against the previous report to measure research progress.

---

## Downstream Integration

The output file `tickets/COMPETITION/data-confidence.md` feeds into:

- **FD-018 (Confidence Dashboard sheet)**: The per-competitor scores and traffic-light classifications are consumed by `generate-financial-dashboard.prompt.md` to annotate dashboard data with confidence indicators
- **Research prioritization**: Action items from this report drive which `research-*` prompts to run next and for which competitors

---

## Related Prompts

- `analysis/market/research-competitor.prompt.md` -- Deep-dive research (feeds data into this assessment)
- `analysis/market/research-financial-growth.prompt.md` -- Financial growth research (feeds data)
- `analysis/market/research-company-history.prompt.md` -- Corporate history research (feeds data)
- `analysis/market/research-customer-intelligence.prompt.md` -- Customer intelligence research (feeds data)
- `analysis/market/generate-financial-dashboard.prompt.md` -- Dashboard generation (consumes confidence scores from FD-018)
- `prompt/improve-prompt.prompt.md` -- Used to identify and fix issues in this prompt
- `prompt/enhance-prompt.prompt.md` -- Used to add advanced features to this prompt

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` -- Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` -- Registry format requirements

---

## Pattern Used

This prompt follows: `.cursor/templars/analysis/multi-entity-confidence-assessment-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/data-confidence-assessment-exemplar.md`

---

**Created**: 2026-02-17
**Improved**: 2026-02-17 (improve-prompt + enhance-prompt applied)
**Extracted**: 2026-02-17 (templar + exemplar extracted via extract-templar-exemplar)
**Context**: tickets/FINANCIALDASHBOARD/FD-027-data-confidence-prompt
**Feeds**: FD-018 (Confidence Dashboard sheet)
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
