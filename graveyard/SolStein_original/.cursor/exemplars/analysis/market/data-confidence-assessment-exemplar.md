---
type: exemplar
artifact-type: prompt
demonstrates: multi-entity-confidence-assessment pattern applied to competitive intelligence data quality
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/assess-data-confidence.prompt.md
implements: .cursor/templars/analysis/multi-entity-confidence-assessment-templar.md
---

# Assess Data Confidence Prompt - Exemplar

## Artifact Type

**Type**: Prompt (analysis/market)

## Why This is Exemplary

This prompt demonstrates best-in-class application of the multi-entity confidence assessment pattern for competitive intelligence. It turns scattered research file signals (Confirmed / Estimated / Unknown tags) into a single confidence map that tells decision-makers which data they can trust and which competitors need more research.

## Key Quality Elements

1. **5-Dimension Rubric with Per-Band Measurable Criteria**: Each of the 5 dimensions (Completeness, Source Quality, Recency, Consistency, Research Depth) has a full 1-10 rubric where every score band has a specific, measurable criterion (percentages, counts, date ranges). No vague adjectives -- "70-89% filled" not "mostly complete".

2. **Enumerated Standard Data Fields**: The Completeness dimension lists exactly which data fields count (fundamentals, market position, product & technology, AI & innovation, growth trajectory, commodities, pricing) so scoring is objective and reproducible.

3. **Primary vs Secondary Source Taxonomy**: Source Quality dimension explicitly defines what counts as primary (annual reports, SEC filings, official website) vs secondary (LinkedIn, Crunchbase, news articles) -- preventing the common problem of treating all sources as equal.

4. **Self-Correction Step**: The Reasoning Process includes a dedicated self-correction phase requiring the AI to re-check rubric adherence, arithmetic, coverage, action item completeness, and internal consistency before finalising output. This metacognition step is rare and significantly reduces errors.

5. **Two Contrasting Few-Shot Examples**: Shows scoring for a well-researched competitor (Kisters BelVis, 4/4 files, composite 8.0 = High) and a thinly-researched one (Example Energy Corp, 1/4 files, composite 4.6 = Medium). The contrast calibrates the AI's scoring consistency.

6. **Downstream Integration Awareness**: Explicitly documents that the output feeds into FD-018 (Confidence Dashboard sheet) and research prioritisation -- showing mature prompt ecosystem thinking.

7. **Edge-Case Troubleshooting**: 7 specific troubleshooting entries covering real scenarios (empty folders, private companies, contradictions, stubs, recently acquired companies) with concrete solutions.

8. **Consistency Paradox Handled**: The few-shot example for the thinly-researched competitor scores Consistency as 8 and explicitly notes "Only one file, so no contradictions possible -- score reflects absence of conflict, not quality". This anticipates a common scoring trap and addresses it.

9. **Comprehensive Quality Criteria**: 10-item checklist covering scan completeness, rubric justification, arithmetic correctness, table row counts matching enumeration, and action item sorting -- every dimension of output quality addressed.

10. **Traffic-Light Classification with Clear Boundaries**: High (7-10), Medium (4-6.9), Low (1-3.9) with plain-English meanings for each band, enabling non-technical stakeholders to interpret results.

## Pattern Demonstrated

**Multi-Entity Confidence Assessment** -- a framework for prompts that:

1. Enumerate all entities to assess from an index or folder scan
2. Inventory the depth of available data per entity (files, fields, sources)
3. Score each entity on N dimensions using a measurable rubric (1-10 scale)
4. Compute composite scores (simple average) and assign traffic-light classifications
5. Generate prioritised action items for entities scoring below threshold
6. Include self-correction before output to catch errors
7. Produce a standalone report with summary, per-entity table, dimension analysis, and actions

## Full Exemplar Content

The complete prompt is preserved in its source file. Key sections worth studying:

### Scoring Rubric (Dimension 1: Completeness)

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
- Commodities & specialisation (commodities, protocols, compliance)
- Pricing & business model (model, price range, implementation timeline)

### Scoring Rubric (Dimension 2: Source Quality)

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

### Scoring Rubric (Dimension 3: Recency)

How current is the data?

| Score | Criteria |
|---|---|
| 9-10 | Core data from current year or last 6 months |
| 7-8 | Core data from within the last 12 months |
| 5-6 | Core data is 1-2 years old; some metrics outdated |
| 3-4 | Core data is 2-3 years old |
| 1-2 | Core data is 3+ years old or undated |

**Core data** = revenue, employee count, product capabilities, market presence.

### Scoring Rubric (Dimension 4: Consistency)

Do different research files agree, or are there contradictions?

| Score | Criteria |
|---|---|
| 9-10 | All files agree; no contradictions detected |
| 7-8 | Minor discrepancies in non-critical fields (e.g., employee count differs by <10%) |
| 5-6 | Some contradictions in important fields; sources disagree on revenue or key dates |
| 3-4 | Significant contradictions; different files present conflicting pictures |
| 1-2 | Major conflicts across files; data cannot be reconciled without further research |

### Scoring Rubric (Dimension 5: Research Depth)

How many research prompts have been run for this competitor?

| Score | Criteria |
|---|---|
| 9-10 | All 4 research files present (identification + deep-analysis + financial-growth + corporate-history) |
| 7-8 | 3 of 4 research files present |
| 5-6 | 2 of 4 research files present |
| 3-4 | Only 1 research file present (identification only) |
| 1-2 | No dedicated research file; competitor mentioned only in cross-references |

### Few-Shot Example: Well-Researched Competitor

**Competitor**: `kisters-belvis/`
**Files present**: `kisters-belvis.md`, `deep-analysis.md`, `financial-growth.md`, `corporate-history.md` (4 of 4)

| Dimension | Score | Rationale |
|---|---|---|
| Completeness | 7 | All major categories covered; pricing data estimated, AI features section thin |
| Source Quality | 6 | Official website and LinkedIn data solid; revenue figures from analyst estimates only |
| Recency | 8 | Employee count and product features from 2025; revenue figure from 2024 annual report |
| Consistency | 9 | All files agree on key facts; minor 5% variance in employee count between identification and deep-analysis |
| Research Depth | 10 | All 4 research files present |

**Composite**: (7 + 6 + 8 + 9 + 10) / 5 = **8.0** -- **High Confidence**

**Scoring Note**: "Private company -- revenue figures are analyst estimates (Completeness and Source Quality reflect this). All 4 research prompts have been run."

### Few-Shot Example: Thinly-Researched Competitor

**Competitor**: `example-energy-corp/`
**Files present**: `example-energy-corp.md` only (1 of 4)

| Dimension | Score | Rationale |
|---|---|---|
| Completeness | 3 | Only basic identification data: name, HQ, founded year, rough employee estimate |
| Source Quality | 4 | Company website and one news article; no financials from primary sources |
| Recency | 5 | Identification data from 2025 but no depth beyond initial scan |
| Consistency | 8 | Only one file, so no contradictions possible -- score reflects absence of conflict, not quality |
| Research Depth | 3 | Only identification file present; 3 of 4 research files missing |

**Composite**: (3 + 4 + 5 + 8 + 3) / 5 = **4.6** -- **Medium Confidence**

**Action Item**: Run `research-competitor`, `research-financial-growth`, and `research-company-history` prompts to fill critical gaps.

### Self-Correction Section

After drafting the full report, review your own work:

- **Rubric adherence**: Re-read each dimension score and confirm it falls within the rubric's criteria band. If you scored Completeness as 7, verify that 70-89% of standard data fields are actually filled.
- **Arithmetic**: Recalculate every composite score. Confirm the traffic-light label matches the composite range.
- **Coverage**: Count rows in the per-competitor table and compare to the competitor enumeration in Step 1. Every competitor must appear exactly once.
- **Action item completeness**: Every competitor with Medium or Low confidence must have at least one action item. High-confidence competitors with low Recency scores should appear in Priority 3.
- **Internal consistency**: If you scored Consistency as 9 but noted contradictions in the Scoring Notes, re-examine and adjust.

### Troubleshooting Table

| Issue | Solution |
|---|---|
| Competitor folder exists but is empty | Score Research Depth as 1. Note in Scoring Notes. |
| Private company has inherently limited financial data | Score Source Quality based on what's available, not what's theoretically possible. Add note explaining the inherent limitation. |
| Data contradictions found during assessment | Score Consistency low. Document specific contradictions in Scoring Notes with file references. |
| Unsure whether a folder is a competitor | Check `tickets/COMPETITION/README.md` status table. Skip non-competitor folders. |
| Very large number of competitors (20+) | Process in batches alphabetically. All must appear in final output. |
| Research file exists but contains only a stub or template | Treat as absent for Research Depth scoring. Note in Scoring Notes that the file exists but lacks substantive content. |
| Competitor recently acquired or renamed | Use the most current name. Note the name change in Scoring Notes. Score Consistency relative to the rename (files may legitimately use different names). |

## Learning Points

- **Measurable rubric bands are essential**: Every score level must have a numeric threshold (percentage, count, time range). "Mostly complete" is useless; "70-89% filled" is actionable and reproducible.
- **Self-correction prevents cascading errors**: Adding a dedicated review step after drafting catches arithmetic mistakes, missed entities, and score/label mismatches before the output is finalised.
- **Consistency paradox needs explicit handling**: When an entity has only one data source, Consistency will score high by default (no contradictions possible). The few-shot example explicitly calls this out so the AI doesn't naively inflate scores.
- **Downstream integration awareness increases prompt value**: Documenting where the output feeds (FD-018 dashboard, research prioritisation) helps users understand the prompt's role in the larger workflow.
- **Contrasting examples calibrate better than single examples**: Showing both a strong and weak entity in few-shot examples gives the AI two reference points for the scoring scale.
- **Traffic-light labels should be stakeholder-friendly**: "High / Medium / Low" works for non-technical decision-makers; domain-specific labels (Rocket / Dinosaur) work for technical teams. Choose based on audience.
- **Action items must be specific**: "Run `research-financial-growth` to address financial data gap" is actionable; "do more research" is not.

## When to Reference

Use this exemplar when:
- Creating a new multi-entity quality or confidence assessment prompt
- Designing a rubric with per-band measurable criteria
- Adding self-correction steps to an analysis prompt
- Building few-shot examples that span the quality spectrum
- Structuring action items as prioritised, specific recommendations

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-competitor-exemplar.md` -- Single-entity research pattern (feeds data into this assessment)
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` -- Financial research pattern (feeds data into this assessment)
- `.cursor/exemplars/analysis/market/financial-dashboard-exemplar.md` -- Dashboard synthesis pattern (consumes this assessment's output)

## Related Templars

- `.cursor/templars/analysis/multi-entity-confidence-assessment-templar.md` -- Structural template extracted from the same source prompt

---

**Extracted From**: `.cursor/prompts/analysis/market/assess-data-confidence.prompt.md`
**Created**: 2026-02-17
