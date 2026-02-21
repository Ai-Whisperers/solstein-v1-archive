---
type: exemplar
artifact-type: prompt
demonstrates: structured-web-research pattern applied to customer intelligence with tiered usage modes
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-customer-intelligence.prompt.md
implements: .cursor/templars/analysis/market/structured-web-research-templar.md
---

# Research Customer Intelligence Prompt - Exemplar

## Artifact Type

**Type**: Prompt (`.prompt.md`)

## Why This is Exemplary

This prompt demonstrates best-in-class application of the structured web research pattern to a customer-focused research domain. It introduces the **tiered usage mode pattern** (Quick/Standard/Deep) with per-category time budgets -- a novel structural element not yet present in the base templar. It also shows how to decompose a broad research goal into energy market segment-specific categories with precise search strategies.

## Key Quality Elements

1. **Tiered Usage Modes (Quick/Standard/Deep)**: The most distinctive element. Each mode specifies which research categories to include AND provides per-category time estimates in a comparison table. This lets the user make informed trade-offs between thoroughness and time investment. No other prompt in the research family has this.

2. **Energy Market Segment Taxonomy**: Category 1 (Reference Client Inventory) organizes customers by segment (TSO, DSO, Supplier, Trader, BRP, Industrial) with segment-specific search strategies. This domain-specific structure ensures comprehensive coverage across all relevant market segments.

3. **Directional Migration Evidence**: Category 3 (Switching Patterns) structures findings as directional "From -> To" migration evidence with triggers and timelines. This is a sophisticated analytical structure that goes beyond simple data collection.

4. **Overlap Assessment Against Own Customer Base**: Category 5 cross-references competitor customers against the company's own customer base -- a competitive intelligence technique that connects research findings directly to business risk.

5. **Excellent Constraints Section**: Four explicit constraints (public sources only, source attribution required, confidence marking mandatory, no speculation) set clear guardrails that prevent common research prompt failure modes.

6. **Realistic Few-Shot Examples**: Two filled-in examples showing exactly what completed Category 1 (segment distribution table + key accounts) and Category 2 (win/loss timeline) outputs look like. These use realistic energy industry company names and data patterns.

7. **Comprehensive Troubleshooting**: Six troubleshooting entries covering real research challenges specific to customer intelligence (private companies, missing segment data, no switching evidence, no case studies, unknown Eneve overlap, thin results). The last entry notes that thin results are themselves a competitive insight.

8. **Downstream Data Integration**: Purpose section explicitly maps how findings feed into specific downstream analyses (FD-014 M&A Vulnerability, FD-016 Competitive Overlap, FD-020 Portfolio Risk), showing the research isn't standalone but part of a decision pipeline.

## Novel Pattern: Tiered Usage Modes

This pattern is worth adopting in other research prompts. The key elements are:

### Structure

```markdown
## Usage Modes

### Quick Mode (10-15 min)
[Subset of categories, focused scope]

### Standard Mode (20-40 min) -- Default
[All categories, balanced depth]

### Deep Mode (45-90 min)
[All categories, extended search with follow-up queries]
```

### Time Budget Table

```markdown
| Category | Quick | Standard | Deep |
|---|---|---|---|
| 1. [Category Name] | 5-8 min | 8-12 min | 15-20 min |
| 2. [Category Name] | 5-7 min | 5-10 min | 10-15 min |
| 3. [Category Name] | -- | 3-7 min | 10-15 min |
| **Total** | **10-15 min** | **20-40 min** | **45-90 min** |
```

### Invocation Convention

```markdown
@prompt-slug Subject @context-path/ --quick
@prompt-slug Subject @context-path/          # Standard (default)
@prompt-slug Subject @context-path/ --deep
```

**Why this matters**: Research prompts without time guidance either run too long (frustrating the user) or cut corners (missing data). The tiered approach gives explicit permission for quick scans while documenting the thoroughness trade-off.

## Pattern Demonstrated

**Structured Web Research Pattern** as defined in `.cursor/templars/analysis/market/structured-web-research-templar.md`, with these additions:
- Tiered usage modes (Quick/Standard/Deep) with time budgets
- Constraints section with explicit guardrails
- Downstream integration mapping (research -> decision pipeline)
- Segment-specific research categories (energy market taxonomy)
- Cross-reference with own customer base (overlap assessment)

## Key Excerpts

### Tiered Time Budget Table

```markdown
| Category | Quick | Standard | Deep |
|---|---|---|---|
| 1. Reference Client Inventory | 5-8 min | 8-12 min | 15-20 min |
| 2. Win/Loss Signals | 5-7 min | 5-10 min | 10-15 min |
| 3. Switching Patterns | -- | 3-7 min | 10-15 min |
| 4. Implementation Case Studies | -- | 3-7 min | 10-20 min |
| 5. Concentration & Overlap | -- | 3-5 min | 10-15 min |
| **Total** | **10-15 min** | **20-40 min** | **45-90 min** |
```

### Segment Distribution Table (from Few-Shot Example)

```markdown
| Segment | Count | Notable Names | Source | Confidence |
|---|---|---|---|---|
| TSO | 3 | TenneT, Elia, National Grid ESO | Annual Report 2025, p.14 | Confirmed |
| DSO | 5 | Enexis, Liander, Stedin, UK Power Networks, E.ON Netz | Press releases 2023-2025 | Confirmed |
| Supplier | 12 | Vattenfall, Eneco, Shell Energy | Case study page + LinkedIn | Estimated |
| Trader | 2 | Axpo, Statkraft | ETRM vendor guide 2024 | Estimated |
| BRP | 0 | -- | No evidence found | Unknown |
| Industrial | 4 | BASF, Tata Steel, Dow Chemical, Air Liquide | Sustainability report references | Estimated |
| **Total Identified** | **26** | | | |
```

### Constraints Section

```markdown
## Constraints

- **Public sources only**: Do not speculate on private contracts, undisclosed revenue,
  or confidential customer relationships.
- **Source attribution required**: Every finding must include a source reference.
- **Confidence marking mandatory**: Every data point must carry a confidence level.
- **No speculation**: If fewer than 50% of data points in a category can be filled,
  add a note explaining why.
```

### Switching Pattern Output (Directional Evidence)

```markdown
| Date | Customer | From | To | Trigger | Source |
|---|---|---|---|---|---|
| YYYY | [name] | [old vendor] | [COMPANY] | [reason] | [source] |
| YYYY | [name] | [COMPANY] | [new vendor] | [reason] | [source] |
```

### Troubleshooting Highlight

```markdown
| Research yielding very thin results | Switch to Quick mode; document gaps explicitly.
  Thin results are themselves a competitive insight (low market visibility). |
```

## Learning Points

1. **Tiered modes give users explicit control over depth/time trade-off**: Without this, every research session defaults to the same depth regardless of the user's time constraint or the competitor's strategic importance.

2. **Segment-specific categories produce structured intelligence**: Organizing customers by TSO/DSO/Supplier/Trader/BRP/Industrial ensures no market segment is missed. This is domain-specific but the principle (domain taxonomy as research organizer) is universally applicable.

3. **Directional migration evidence reveals competitive dynamics**: "From -> To" evidence with triggers shows WHY customers switch, not just that they did. This analytical depth distinguishes intelligence from mere data collection.

4. **Cross-referencing against own customer base converts research into risk assessment**: The overlap analysis in Category 5 transforms external research into internal business intelligence.

5. **Constraints prevent common failure modes up front**: Stating "public sources only" and "no speculation" prevents the agent from filling gaps with hallucinated data or making claims based on unverifiable information.

6. **Thin results are a valid finding**: The troubleshooting entry explicitly saying "thin results are themselves a competitive insight (low market visibility)" prevents the agent from over-searching or fabricating data to fill a template.

7. **Downstream integration shows research purpose**: Mapping findings to specific downstream analyses (FD-014, FD-016, FD-020) prevents the "so what?" problem where research is produced but never consumed.

## When to Reference

Use this exemplar when:
- Creating a new research prompt that needs tiered usage modes (Quick/Standard/Deep)
- Building a customer-focused research prompt for any industry
- Designing prompts that must cross-reference findings against an internal baseline
- Looking for examples of directional analysis (migration From -> To patterns)
- Needing a reference for constraints/guardrails in research prompts
- Understanding how to integrate research output into a broader decision pipeline

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-competitor-exemplar.md` - Companion exemplar showing the structured web research pattern applied to general competitive intelligence (8 research categories)
- `.cursor/exemplars/analysis/market/research-company-history-exemplar.md` - Same pattern applied to corporate genealogy research
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` - Same pattern applied to financial metrics

---

**Extracted from**: `.cursor/prompts/analysis/market/research-customer-intelligence.prompt.md` (2026-02-17)
**Implements**: `.cursor/templars/analysis/market/structured-web-research-templar.md`
