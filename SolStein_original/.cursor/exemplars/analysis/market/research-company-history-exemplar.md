---
type: exemplar
artifact-type: prompt
demonstrates: guided-web-research-prompt pattern applied to corporate genealogy research
domain: analysis/market (competitive intelligence)
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-company-history.prompt.md
implements: .cursor/templars/analysis/market/guided-research-prompt-templar.md
---

# Research Company History - Exemplar

## Artifact Type

**Type**: Prompt (`.prompt.md` -- guided web research)

## Why This is Exemplary

This prompt demonstrates exceptional execution of the **Guided Web Research Prompt** pattern (see templar: `.cursor/templars/analysis/market/guided-research-prompt-templar.md`). It goes beyond the basic pattern with domain-specific depth that produces consistently high-quality corporate genealogy research across multiple competitor profiles.

## Key Quality Elements

1. **Research Categories with actionable search strategies**: Each of the 6 categories pairs every data point with concrete search guidance (e.g., "Annual reports, stock exchange filings, Crunchbase, PitchBook" for shareholder data). This eliminates guesswork during research.

2. **Three distinct Mermaid diagram types**: Corporate Structure (graph TD for ownership trees), Corporate Timeline (timeline for chronological events), and M&A Genealogy (graph LR for acquisition assembly). Each diagram type matches the shape of the data it visualizes.

3. **Investor type classification**: Goes beyond listing investors to classifying each as Strategic/VC/PE/Sovereign/Government/Corporate -- enabling pattern analysis across the competitive landscape.

4. **10-step reasoning process**: Explicitly guides AI agent behavior through read, establish baseline, research backwards, follow breadcrumbs, cross-reference, build timeline, identify patterns, build diagrams, assess implications, and format output. The "research backwards" and "follow the breadcrumbs" steps are domain-specific innovations.

5. **Source attribution + confidence baked into every table**: Not an afterthought -- the output template makes "Source" and "Confidence" mandatory columns in every data table, ensuring auditability.

6. **Pattern analysis section**: After raw data collection, requires synthesis of growth strategy, acquisition patterns, technology evolution, and leadership stability -- transforming data into intelligence.

7. **Search query templates organized by research focus**: Provides 3-4 query patterns for each research dimension (origin, name changes, M&A, ownership, investment, splits, critical events, trade registers), making search systematic and reproducible.

8. **Multiple invocation patterns**: Demonstrates flexible usage -- single company, company without folder, focused M&A analysis, and product lineage tracing -- showing the prompt adapts to different research needs.

## Pattern Demonstrated

### Guided Web Research Prompt Pattern

The prompt implements the full guided-research-prompt-templar structure with these domain-specific adaptations:

| Templar Element | How This Exemplar Implements It |
|---|---|
| **Research Categories** | 6 categories (Ownership, Identity Timeline, M&A, Investment, Splits, Critical Events) each with 6-10 data points and specific search strategies |
| **Output Format** | Full markdown template with 8 structured table sections + 3 Mermaid diagrams + text timeline + pattern analysis + strategic assessment |
| **Search Query Templates** | 30+ query templates organized by 8 research dimensions, including trade register site-specific queries |
| **Reasoning Process** | 10 steps with domain-specific innovations ("research backwards", "follow the breadcrumbs", "spot timeline gaps") |
| **Quality Criteria** | 20 checkboxes covering data completeness, diagram generation, source attribution, and strategic assessment |
| **Mermaid Diagrams** | 3 types matched to data shape: ownership tree (graph TD), timeline (timeline), M&A assembly (graph LR) |

### Structural Innovations Worth Replicating

**1. Research Category tables with "Search Strategy" column**:

```markdown
| Data Point | Search Strategy |
|---|---|
| Current shareholders with % stakes | Annual reports, stock exchange filings, Crunchbase, PitchBook |
| Investor type classification | Investor websites, Crunchbase (strategic/VC/PE/sovereign/government) |
```

This pairs WHAT to find with WHERE to find it, making the prompt self-contained.

**2. Output template with mandatory source + confidence columns**:

```markdown
| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Founded | [year] | [source] | Confirmed/Estimated |
```

Baking source attribution into the table structure ensures every data point is auditable.

**3. Multiple Mermaid diagram types matched to data shape**:

- **Ownership tree** (graph TD): Hierarchical parent-child relationships
- **Timeline** (timeline): Chronological events grouped by phase
- **M&A genealogy** (graph LR): Left-to-right flow showing how company was assembled from parts

Choosing the right Mermaid diagram type for each data shape makes complex information scannable.

**4. "Research backwards" reasoning step**:

> Start from the present and work backwards through time, following each thread (acquisitions, name changes, parent companies) to its origin

This domain-specific insight prevents the common trap of researching forward from founding (which misses events you don't know about yet).

**5. Timeline gap detection**:

> Place events chronologically to spot gaps (e.g., "nothing happened between 2008-2015" likely means we missed something)

Using the timeline as a quality check for research completeness is a technique applicable to any chronological research.

## Learning Points

- **Pair every data point with search strategy**: Don't just list what to research -- tell the agent WHERE to find each data point. This is the difference between "Research M&A history" and "Search Crunchbase, press releases, annual reports for acquisitions."
- **Use multiple Mermaid diagram types**: Choose diagram types that match data shape (hierarchies = graph TD, timelines = timeline, flows = graph LR). Don't force all data into one diagram type.
- **Classify, don't just list**: Classifying investors by type (Strategic/VC/PE/Sovereign) enables cross-company pattern analysis. Apply this principle to any categorical data.
- **Research backwards from present**: For historical research, start with what's known (present) and trace backwards. Each discovery opens new threads to follow.
- **Use timeline gaps as quality signals**: If chronological research has large gaps, something was missed. Build gap detection into the reasoning process.
- **Multiple output formats for different consumers**: Tables for detail consumers, Mermaid diagrams for visual scanners, text timeline for narrative readers. Serve all reading styles.
- **Quality criteria as checklist, not prose**: 20 concrete checkboxes are more enforceable than "ensure high quality." Each checkbox is independently verifiable.

## When to Reference

Use this exemplar when:
- Creating a new research prompt for any domain (technology, market, regulatory, etc.)
- Improving an existing research prompt's structure
- Designing output templates that need source attribution and confidence levels
- Adding Mermaid diagrams to research output
- Building search query templates for systematic web research
- Structuring AI agent reasoning processes for multi-step research tasks

## Source Artifact

**Full prompt**: `.cursor/prompts/analysis/market/research-company-history.prompt.md`

The source artifact contains the complete, functional prompt with all research categories, output templates, search queries, and reasoning process. Refer to it for the full implementation; this exemplar highlights the quality patterns worth replicating.

## Companion Artifacts

- `.cursor/prompts/analysis/market/research-competitor.prompt.md` -- Same pattern applied to deep-dive competitive analysis (8 categories, different focus)
- `.cursor/prompts/analysis/market/research-protocols.prompt.md` -- Protocol-focused research (different domain, similar structure)
- `.cursor/prompts/analysis/market/research-financial-growth.prompt.md` -- Financial research dimension

## Related Exemplars

- Ticket exemplars (`.cursor/exemplars/ticket/`) -- Different domain, similar structured-output quality standards

## Related Templars

- `.cursor/templars/analysis/market/guided-research-prompt-templar.md` -- The abstract pattern extracted from this exemplar
