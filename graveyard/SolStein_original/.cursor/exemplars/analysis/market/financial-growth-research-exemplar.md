---
type: exemplar
artifact-type: prompt
demonstrates: multi-dimensional-research-scorecard pattern applied to financial competitor research
domain: analysis/market
quality-score: exceptional
version: 1.0.0
implements: .cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md
extracted-from: .cursor/prompts/analysis/market/research-financial-growth.prompt.md
---

# Financial Growth Research - Exemplar

## Artifact Type

**Type**: Prompt (analysis/market)

## Why This is Exemplary

This prompt represents best-in-class implementation of the multi-dimensional research with scoring rubric pattern. It demonstrates how to turn abstract research goals into a rigorous, reproducible, evidence-backed assessment framework that produces comparable results across subjects.

## Key Quality Elements

1. **Exhaustive research categories**: 6 categories with 60+ specific data points, each paired with concrete search strategies -- leaves no ambiguity about what to look for
2. **Measurable scoring rubrics**: Every score level (1-10) has numeric thresholds (e.g., "CAGR >30% = 9-10") rather than vague adjectives, making scores comparable across competitors
3. **10-level source reliability hierarchy**: From annual reports (most reliable) to Wayback Machine (least reliable), giving the AI clear precedence rules when sources conflict
4. **Company-type decision tree**: Routes research approach based on subject characteristics (public, PE-acquired, VC-funded, private), preventing wasted effort on irrelevant sources
5. **Data-quality-aware few-shot examples**: Three examples calibrated to High, Medium, and Low data availability, teaching the AI to handle uncertainty honestly rather than fabricating data
6. **Mermaid chart integration**: Revenue trend, employee growth, and scorecard bar chart templates embedded directly in the output format -- visual impact with minimal friction
7. **Composite scoring with memorable classifications**: "Rocket / Riser / Steady / Dinosaur" labels stick in stakeholders' minds far better than "Level 1-4"
8. **Confidence tracking per data point**: Every cell in every timeline table requires Source + Confidence (Confirmed/Estimated/Unknown), enforcing intellectual honesty
9. **Proxy metric guidance**: Explicit methodology for estimating revenue of private companies (employee count x EUR 150-250K) with instructions to flag as "Estimated (proxy)"
10. **Prioritised usage backlog**: 30+ competitor invocations organised into 4 priority tiers by threat level, serving as both documentation and a research task queue

## Pattern Demonstrated

**Multi-Dimensional Research with Scoring Rubric** -- a framework for structured research prompts that:

1. Define 4-8 research categories with specific data points and search strategies
2. Provide source reliability hierarchies to resolve conflicting data
3. Route research approach via subject-type decision trees
4. Require evidence + confidence tracking for every data point
5. Score dimensions using explicit numeric rubrics (not impressions)
6. Produce composite scores with named classification bands
7. Generate visual outputs (Mermaid charts) for stakeholder impact
8. Handle data scarcity honestly through proxy metrics and "Unknown" markers

## Full Exemplar Content

Below is the complete, working prompt that demonstrates this pattern applied to financial competitor research in the European energy software market.

---

### Frontmatter (Exemplary)

Note how the frontmatter is minimal but complete -- name maps to slash command, description fits in a quick-pick, argument-hint guides the user:

```yaml
---
name: research-financial-growth
description: "Please perform a deep financial and growth research analysis on an energy software competitor"
category: analysis
tags: competition, financial, growth, revenue, funding, trajectory, dinosaur-vs-rocket
argument-hint: "Company name and path to company folder (e.g., Volue ASA @tickets/COMPETITION/volue/)"
---
```

### Source Reliability Hierarchy (Exemplary)

The prompt defines a 10-level source preference list. This prevents the AI from treating a blog post and an annual report as equally reliable:

1. Annual reports / financial filings
2. Stock exchange filings (Oslo Bors, Euronext, LSE, ASX)
3. Crunchbase / PitchBook / CB Insights
4. Press releases
5. LinkedIn company page
6. Glassdoor / Indeed
7. Industry analyst reports (Chartis, Energy Risk, IDC)
8. News articles (TechCrunch, EU-Startups, Sifted)
9. Company website (about page, investor relations)
10. Wayback Machine (historical data)

### Research Categories (Exemplary)

Six categories with specific data points. Example from Category 1:

| Data Point | Search Strategy |
| --- | --- |
| Revenue (current year) | Annual report, financial filings, press releases |
| Revenue (1yr ago) | Annual report, financial filings |
| Revenue CAGR (3yr and 5yr) | Calculated from above |
| EBITDA / Operating margin | Annual report, financial filings |
| Recurring revenue % | Annual report, SaaS metrics disclosures |
| Revenue per employee | Calculated: revenue / headcount |
| Revenue by segment | Annual report segment reporting |

The full prompt defines 60+ data points across: Revenue & Profitability, Funding & Investment, Employee Growth, Geographic & Market Expansion, M&A Activity, and SaaS Transition Metrics.

### Scoring Rubric (Exemplary)

Each dimension has explicit numeric criteria. Example for Revenue Growth:

| Score | Criteria |
| --- | --- |
| 9-10 | Revenue CAGR >30% over 3yr, or explosive YoY growth >50% |
| 7-8 | Revenue CAGR 20-30% over 3yr, strong consistent growth |
| 5-6 | Revenue CAGR 10-20% over 3yr, solid growth |
| 3-4 | Revenue CAGR 5-10% over 3yr, modest growth |
| 1-2 | Revenue CAGR <5%, flat, or declining |

No vague labels -- every level has a number. This makes scores comparable across competitors.

### Classification Bands (Exemplary)

Memorable, evocative names tied to score ranges:

- **Rocket** (avg 7.0-10.0): Explosive growth, heavy investment, market disruptor
- **Riser** (avg 5.0-6.9): Strong growth signals, investing in future, accelerating
- **Steady** (avg 3.0-4.9): Stable but not transforming, evolutionary
- **Dinosaur** (avg 1.0-2.9): Flat or declining, legacy mode, no visible investment

### Company-Type Decision Tree (Exemplary)

Routes research approach to avoid wasted effort:

```text
Is the company publicly listed?
+-- YES -> Path A: Public Company
|   +-- Search: Annual reports, stock exchange filings, investor relations page
|   +-- Expected data quality: HIGH (3-5yr revenue, margins, headcount)
|   +-- Start with: "[COMPANY] annual report [YEAR] PDF"
|
+-- RECENTLY DELISTED / PE-ACQUIRED -> Path B: Post-Public
|   +-- Search: Last public filings + PE firm portfolio page + press releases
|   +-- Expected data quality: MEDIUM (historical + sparse recent)
|   +-- Start with: "[COMPANY] [PE FIRM] acquisition annual report"
|
+-- VC-FUNDED STARTUP -> Path C: Funded Private
|   +-- Search: Crunchbase + PitchBook + funding press releases + LinkedIn
|   +-- Expected data quality: MEDIUM (funding data good, revenue estimates)
|   +-- Start with: "[COMPANY] Crunchbase funding series"
|
+-- PRIVATE / BOOTSTRAPPED -> Path D: Opaque
    +-- Search: LinkedIn headcount + government filings + trade press + proxies
    +-- Expected data quality: LOW (heavy estimation required)
    +-- Start with: "[COMPANY] LinkedIn employees" + country-specific registries
```

### Few-Shot Examples (Exemplary -- Data Availability Spectrum)

**High-Data Example (Volue ASA -- Public Company)**:
- Revenue Timeline: 5 years from annual reports, NOK with EUR conversion
- Employee Timeline: LinkedIn ~500 current, Wayback Machine for historical
- Growth Scorecard: Revenue Growth 7 (CAGR ~22%), Funding 5 (IPO, no recent rounds), Employee Growth 7 (15-25% CAGR), Geographic Expansion 7 (3 countries added), M&A 9 (5+ acquisitions in 3yr), SaaS 6 (hybrid, transitioning)
- Composite: 6.8 = **Riser** (just below Rocket threshold)

**Medium-Data Example (Engrate -- VC-Funded Startup)**:
- Revenue Timeline: 1-2 years, estimated from press releases and employee count
- Employee Timeline: LinkedIn only, 10-30 employees
- Growth Scorecard: Revenue Growth 9 (>50% YoY from near-zero), Funding 3 (EUR 3M seed), Employee Growth 9 (tripling), Geographic Expansion 3 (single market), M&A 1 (none), SaaS 9 (cloud-native)
- Composite: 5.7 = **Riser** (high variance, high upside)
- Key challenge: Mark most data points as "Estimated"

**Low-Data Example (Schleupen -- Private Legacy)**:
- Revenue Timeline: 1-2 data points from press mentions, rest "Unknown"
- Employee Timeline: LinkedIn (may undercount), XING for German companies
- Growth Scorecard: All dimensions likely 2-4 range, heavy "Unknown" markers
- Composite: ~3.0 = **Steady/Dinosaur** boundary
- Key challenge: Honesty about data gaps; search XING and German trade press

### Troubleshooting (Exemplary)

The prompt handles 4 common data challenges:

1. **No Financial Data Available** -- Use proxy metrics (employees x EUR 150-250K), check government filings (Bundesanzeiger, KVK, Companies House), search interview quotes
2. **Conflicting Data Sources** -- Prefer primary sources (annual report > filing > press release > Crunchbase > news), document both figures, use conservative figure for scoring
3. **Company Recently Acquired / Delisted** -- Use pre-acquisition financials, search parent company segment reporting, note cutoff year
4. **Currency Conversion for Multi-Year Timelines** -- Use annual average EUR rate per year (ECB Statistical Data Warehouse), not today's rate

### Search Query Templates (Exemplary)

Ready-to-use with `[COMPANY]` placeholder:

**Revenue**: `"[COMPANY]" revenue 2023 2024 2025 annual report`
**Funding**: `"[COMPANY]" funding round series investors 2024 2025 2026`
**Employees**: `"[COMPANY]" employees headcount LinkedIn`
**M&A**: `"[COMPANY]" acquisition 2022 2023 2024 2025`
**SaaS**: `"[COMPANY]" cloud SaaS migration platform`

### Prioritised Usage Backlog (Exemplary)

The prompt includes 30+ competitor invocations organised into 4 priority tiers:

- **Priority 1 - Rockets and Risers** (6 competitors): Research first, these are the threat
- **Priority 2 - Large Players** (6 competitors): Understand the scale
- **Priority 3 - Direct Competitors** (5 competitors): Know thy enemy
- **Priority 4 - National Specialists** (10 competitors): National/infrastructure players

This serves dual purpose: prompt documentation AND research task queue.

### Quality Criteria Checklist (Exemplary)

12 specific, verifiable criteria including:
- All 6 categories addressed
- Minimum 3 years of timeline data
- Every data point has source + confidence level
- Revenue in both original currency AND EUR
- Scores follow rubric (not gut feeling)
- Composite score = average of 6 dimensions
- Classification matches threshold bands

## Learning Points

1. **Numeric rubrics beat vague labels**: "CAGR >30% = 9-10" is infinitely more useful than "Excellent growth = High". This makes scores reproducible and comparable across different subjects and different researchers
2. **Source hierarchies resolve conflicts**: When Crunchbase says EUR 20M and a press release says EUR 25M, the prompt tells you which to trust. Without this, the AI picks randomly
3. **Data-availability-aware examples are essential**: Showing the AI how to handle a data-rich public company AND a data-scarce private company prevents it from fabricating data to fill templates
4. **Decision trees save effort**: Routing to "Path D: Opaque" for bootstrapped companies means the AI immediately goes to LinkedIn + government registries instead of wasting time searching for non-existent annual reports
5. **Memorable classification names drive action**: "Dinosaur" is a wake-up call; "Category 4" is forgettable. Evocative labels make stakeholders remember the findings
6. **Confidence tracking enforces honesty**: Requiring "Confirmed/Estimated/Unknown" per data point prevents the research from reading more authoritative than it actually is
7. **Proxy metrics unlock opaque subjects**: The EUR 150-250K revenue-per-employee proxy turns a dead end (no revenue data) into a usable estimate, clearly flagged as such
8. **Mermaid charts embedded in output format**: Including chart templates directly in the expected output means the AI generates them by default, without the user needing to ask separately

## When to Reference

Use this exemplar when:

- Creating a new multi-dimensional research or assessment prompt
- Wanting to see how to implement explicit scoring rubrics with numeric thresholds
- Building research prompts that handle varying data availability
- Needing inspiration for subject-type decision trees
- Designing output formats that combine tables, timelines, charts, and scorecards
- Setting up source reliability hierarchies for structured research
- Creating classification systems with memorable band names

## Related Exemplars

- (None yet in analysis category -- this is the first)

## Related Templars

- `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md` -- The abstract pattern this exemplar implements

---

**Extracted From**: `.cursor/prompts/analysis/market/research-financial-growth.prompt.md`
**Created**: 2026-02-15
