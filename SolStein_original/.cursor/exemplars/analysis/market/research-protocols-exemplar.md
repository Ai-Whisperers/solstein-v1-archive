---
type: exemplar
artifact-type: prompt
demonstrates: systematic-mapping-research pattern applied to energy market protocols
domain: analysis / market / competitive intelligence
quality-score: exceptional
version: 1.0.0
illustrates: analysis.mapping-research
use: critic-only
notes: "Pattern extraction only. NEVER copy domain-specific content (protocol names, country tables, competitor references) to other prompts. Extract the structural approach: 7-step process, self-correction checkpoints, edge case handling, search query templates, cross-reference workflow."
---

# Research Energy Protocols Exemplar

## Artifact Type

**Type**: Prompt
**Source**: `.cursor/prompts/analysis/market/research-protocols.prompt.md`
**Templar**: `.cursor/templars/analysis/market/systematic-mapping-research-templar.md`

## Why This is Exemplary

This prompt demonstrates an exceptional implementation of the "Systematic Mapping Research" pattern. It stands out for several reasons:

1. **Domain insight as research strategy**: The "key insight" -- that energy protocols are mandated, specific, and finite, making every implementer discoverable -- elevates this from a generic research prompt to a strategic discovery tool. Every good mapping research prompt should articulate *why* the chosen dimension is a reliable indicator.

2. **Comprehensive category breakdown**: The 5 protocol categories (A through E) with specific research-focus questions per sub-area ensure no gaps in coverage. The tabular format makes it scannable and actionable.

3. **Multi-format output specification**: The prompt defines four distinct deliverable types (protocol map, company-protocol matrix, newly discovered companies, convergence assessment), each with its own table format. This prevents vague "write a report" outcomes.

4. **Self-correction checkpoints**: Five explicit validation questions the agent must ask itself before finalizing, targeting the most common failure modes (confusing names vs. categories, listing users instead of vendors, missing categories).

5. **Edge case handling**: Four specific edge cases with concrete solutions (language barriers, deprecated protocols, missing vendor lists, multi-country variants).

6. **Search query templates**: Grouped by source type (governing body lists, protocol implementers, industry events, job postings) with fill-in-the-blank patterns that an AI agent can directly adapt.

7. **Starting reference data**: The "Key Protocols by Country" section provides seed data that bootstraps research and prevents the agent from starting from zero.

8. **File output discipline**: Explicit instructions on *where* to write output (`tickets/COMPETITION/protocol-map.md` and per-company folders), with a clear rule to NOT append to existing files.

## Key Quality Elements

### 1. Strategic Framing (Pattern Element)

The prompt doesn't just say "research protocols." It frames the research as a **discovery strategy**:

> "Protocols are the fingerprint of the energy back-office market -- if you implement EDSN, MaBiS, or AS4, you're a player. Following the protocols reveals the full competitive landscape."

**Lesson**: Every mapping research prompt should articulate *why* the chosen dimension is a reliable discovery mechanism, not just *what* to research.

### 2. Structured Category Tables (Pattern Element)

Instead of a flat list, protocol areas are organized into 5 categories with specific research questions:

- A. Market Communication & Messaging
- B. Balancing & Settlement
- C. Nomination & Scheduling
- D. Metering & Data Exchange
- E. Market Registration & Master Data

Each has a table with sub-areas and focused research questions.

**Lesson**: Break the mapping dimension into exhaustive categories with specific research prompts per sub-area. Tables with "Research Focus" columns force specificity.

### 3. Cross-Reference Workflow (Pattern Element)

Step 5 explicitly compares discovered entities against the known list:

> "Mark companies already tracked with a checkmark. Flag new companies not yet in the competitor list. Note multi-protocol companies."

**Lesson**: The cross-reference step is what transforms research into *discovery*. Always include explicit comparison instructions with clear marking conventions.

### 4. Self-Correction Checkpoints (Pattern Element)

Five targeted questions:
1. Did I distinguish between dimension *names* and *categories*?
2. Did I verify against primary source documents?
3. Are listed entities actual *vendors* (not just users)?
4. Did I miss any category for any scope unit?
5. Are "newly discovered" entities genuinely absent from the known list?

**Lesson**: Self-correction checkpoints should target the most common *specific* failure modes for the domain, not generic "did I do a good job?" questions.

### 5. Seed Data Section (Pattern Element)

The "Key Protocols by Country" tables for Netherlands, Germany, Nordics, UK, and Belgium provide starting-point data.

**Lesson**: Providing seed/reference data dramatically improves research quality by giving the agent a baseline to verify and expand, rather than researching from scratch.

### 6. Few-Shot Examples (Pattern Element)

Two concrete examples:
- Single country focus (Netherlands) showing expected output structure
- Single protocol focus (MaBiS) showing expected output structure

Both include the cross-reference step showing "Already tracked" vs "NEW" markers.

**Lesson**: Few-shot examples should show the *output format* for different invocation modes, including the cross-reference markers that make the output actionable.

## Full Exemplar Content

The full prompt content is preserved in the source file:
`.cursor/prompts/analysis/market/research-protocols.prompt.md`

Refer to the source for the complete implementation. Key sections to study:

| Section | Lines | What to Learn |
|---|---|---|
| Purpose | ~22-34 | How to frame research as strategy |
| Protocol Categories (A-E) | ~56-102 | How to structure exhaustive category tables |
| Step 3: Identify per Country | ~103-123 | Output format specification per scope unit |
| Step 4: Map Companies | ~125-145 | Search strategy enumeration |
| Step 5: Cross-Reference | ~147-153 | Discovery through comparison |
| Self-Correction | ~366-372 | Targeted validation questions |
| Edge Cases | ~374-378 | Concrete solutions for common problems |
| Search Query Templates | ~328-349 | Parameterized search patterns by source type |
| Few-Shot Examples | ~383-449 | Output format demonstrations |

## Learning Points

- **Dimension selection matters**: Choose dimensions that are mandated, finite, and documented for highest discovery yield
- **Categories prevent gaps**: Breaking the dimension into exhaustive sub-categories ensures comprehensive coverage
- **Cross-referencing is the discovery mechanism**: The value isn't in the research itself, but in comparing findings against the known list
- **Self-correction targets domain-specific failures**: Generic checkpoints are less useful than ones targeting the specific ways *this* research can go wrong
- **Seed data bootstraps quality**: Providing starting-point reference data prevents cold-start research failures
- **Multiple output formats serve different consumers**: A matrix, a per-entity detail, a gap list, and a trend assessment each serve different stakeholder needs
- **File output discipline**: Specifying exact output paths and separation rules prevents messy data accumulation

## When to Reference

Use this exemplar when:
- Creating a new mapping research prompt for a different domain
- Improving an existing research prompt's structure or self-correction mechanisms
- Understanding how to frame a research dimension as a discovery strategy
- Learning how to structure category breakdowns with research-focus questions
- Designing search query templates for a new domain

## Related Exemplars

- No other analysis exemplars yet (this is the first in this domain)

## Related Artifacts

- **Templar**: `.cursor/templars/analysis/market/systematic-mapping-research-templar.md`
- **Source**: `.cursor/prompts/analysis/market/research-protocols.prompt.md`
- **Sibling prompts**: `research-competitor.prompt.md`, `research-company-history.prompt.md`, `research-financial-growth.prompt.md`
