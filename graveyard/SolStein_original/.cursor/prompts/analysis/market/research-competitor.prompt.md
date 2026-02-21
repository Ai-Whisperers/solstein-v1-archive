---
name: research-competitor
description: "Please perform a deep-dive competitive research analysis on an energy software competitor"
category: analysis
tags: competition, research, market-analysis, energy, deep-dive, competitor
argument-hint: "Company name and path to company folder (e.g., Volue @tickets/COMPETITION/volue/)"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Research Competitor - Deep Analysis

Please perform a structured deep-dive research session on an energy software competitor to Eneve's eBase platform. This prompt drives systematic web research across all relevant data categories, then updates the competitor's existing identification file with a comprehensive `## Deep Analysis` section.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Converts identification-level profiles into actionable competitive intelligence
**Use When**: After initial competitor identification is complete and deeper analysis is needed

---

## Purpose

This prompt formalizes the "deeper analysis" phase of competitive research by:
- Defining exactly what data to collect across 8 research categories
- Driving systematic web searches to fill every data point
- Producing consistent, comparable profiles across all competitors
- Enabling threat assessment relative to Eneve's eBase platform
- Creating a benchmark of what aggressive competitors have achieved (especially those with AI/growth signals)

---

## Required Context

- **Company Name**: The competitor to research (e.g., "Volue ASA")
- **Company Folder**: Path to the competitor's folder in `tickets/COMPETITION/` (e.g., `@tickets/COMPETITION/volue/`)
- **Eneve Context**: The agent should reference `@tickets/COMPETITION/README.md` for Eneve's positioning summary and the comparison matrix

---

## Process

**Estimated Time**: 30-60 minutes per competitor (varies by data availability; public companies take longer due to more data, private startups may be faster but with lower confidence levels)

Follow these steps to perform the deep-dive research:

### Step 1: Read Existing Profile

Read the competitor's existing files in the company folder (e.g., identification file, corporate history) to understand what we already know. Note any data gaps or unverified claims.

### Step 2: Read Eneve Positioning

Read `tickets/COMPETITION/README.md` to refresh understanding of Eneve's capabilities, market position, and the comparison matrix.

### Step 3: Web Research by Category

For each of the 8 research categories below, perform targeted web searches. Use the company name, product names, and relevant keywords. Prioritize:
- Official company website and press releases
- LinkedIn company page (employee count, growth)
- Crunchbase / PitchBook (funding, valuation)
- Annual reports (if public company)
- Industry publications (Energy Risk, Chartis, CTRM Center)
- Conference appearances (E-world, Enlit, etc.)
- Job postings (technology stack, AI hiring signals)

### Step 4: Synthesize Findings

Organize all findings into the structured Deep Analysis template (see Output Format below). For each data point:
- Record the finding with source attribution
- Mark as "Confirmed", "Estimated", or "Unknown" where data quality varies
- Note contradictions between sources
- Prefer primary sources (annual reports, official filings) over secondary sources (news articles, estimates)

### Step 5: Assess Threat to Eneve

Based on all collected data, write a concise threat assessment covering:
- Where this competitor directly threatens Eneve
- What Eneve does better
- What this competitor does better
- Strategic implications and recommended watch items

### Step 6: Write Deep Analysis File

Write the deep analysis output to a **separate file** within the competitor's folder:

- **File path**: `tickets/COMPETITION/[company-slug]/deep-analysis.md`
- **Create the company folder** if it doesn't exist yet (e.g., `tickets/COMPETITION/volue/`)
- Do NOT append to the main identification file -- keep research outputs in their own dedicated files
- If a `deep-analysis.md` already exists, replace it with the updated version

### Step 7: Update README Status

Update the Data Collection Status table in `tickets/COMPETITION/README.md` to reflect "Deep analysis complete" for this competitor.

---

## Research Categories

### Category 1: Company Fundamentals

Verify and expand on identification data:

| Data Point | Search Strategy |
|---|---|
| Legal entity name | Company website, LinkedIn, Companies House / trade register |
| HQ address and country | Company website contact/about page |
| Founded year | LinkedIn, Crunchbase, company about page |
| Key leadership (CEO, CTO, founders) | LinkedIn, company about page, press releases |
| Ownership structure | Annual reports, Crunchbase, press releases |
| Employee count (current) | LinkedIn company page, annual reports |
| Employee count (1yr ago, 2yr ago) | LinkedIn historical data, Wayback Machine, annual reports |
| Revenue (current + historical) | Annual reports (if public), Crunchbase, press estimates |
| Market cap / valuation | Stock exchange (if public), last funding round (if private) |
| Last funding round details | Crunchbase, TechCrunch, EU-Startups, press releases |

### Category 2: Market Position

| Data Point | Search Strategy |
|---|---|
| Countries of active operation | Company website, press releases, job postings by location |
| Number of customers / installations | Company website, press releases, annual reports |
| Notable customer names | Case studies, press releases, testimonials page |
| Market share estimate | Chartis reports, Energy Risk rankings, analyst estimates |
| Industry rankings / awards | Energy Risk Awards, Chartis Energy50, CTRM Center |
| Competitive wins (vs Eneve or similar) | Press releases, case studies, industry news |

### Category 3: Product & Technology

| Data Point | Search Strategy |
|---|---|
| Full product portfolio with modules | Company website products page, brochures |
| Technology stack | Job postings, technical blog, GitHub (if open source) |
| Cloud/on-premise/hybrid model | Product pages, pricing pages, documentation |
| API strategy | Developer docs, API references, integration pages |
| Integration partners and exchanges | Partner pages, exchange ISV listings (EPEX, Nord Pool) |
| Release cadence | Release notes, changelogs, blog posts |

### Category 4: AI & Innovation

| Data Point | Search Strategy |
|---|---|
| AI/ML features in production | Product pages, press releases, demo videos |
| AI roadmap / announced features | Conference talks, blog posts, press releases |
| AI team size / hiring signals | LinkedIn job postings with "AI", "ML", "data science" |
| AI partnerships | Press releases, partner pages |
| Patents or published research | Google Scholar, patent databases, company blog |
| AI-related acquisitions | Press releases, Crunchbase, M&A databases |

### Category 5: Growth & Trajectory

| Data Point | Search Strategy |
|---|---|
| Revenue growth rate (CAGR or YoY) | Annual reports, press releases, analyst estimates |
| Employee growth rate | LinkedIn historical, Glassdoor, annual reports |
| Geographic expansion (last 2yr) | Press releases, new office announcements, job postings |
| Product launches (last 2yr) | Press releases, product pages, conference announcements |
| Acquisitions made (last 3yr) | Press releases, Crunchbase, M&A databases |
| Funding rounds (last 3yr) | Crunchbase, press releases, investor pages |
| Strategic pivots | Press releases, CEO interviews, annual reports |

### Category 6: Commodities & Specialization

| Data Point | Search Strategy |
|---|---|
| Commodities covered | Product pages, case studies, marketing materials |
| Market segments served | Customer stories, vertical pages, marketing |
| Regulatory compliance | Product pages, compliance documentation |
| Protocol support (EDSN, ENTSO-E, TSO) | Technical documentation, integration pages |

### Category 7: Pricing & Business Model

| Data Point | Search Strategy |
|---|---|
| Pricing model | Pricing page, G2/Capterra listings, sales materials |
| Estimated price range | Industry benchmarks, customer testimonials, analyst reports |
| Typical implementation timeline | Case studies, sales materials, customer quotes |
| Services vs product revenue split | Annual reports (if public), analyst estimates |

### Category 8: Threat Assessment (vs Eneve)

This category is synthesized from all other findings -- no separate web search needed.

| Data Point | Analysis Method |
|---|---|
| Direct overlap areas | Compare product capabilities vs Eneve positioning |
| Areas competitor is stronger | Evidence-based assessment from research |
| Areas Eneve is stronger | Evidence-based assessment from research |
| Likelihood of entering NL market | Geographic expansion signals, NL-specific capabilities |
| Likelihood of expanding into Eneve's areas | Product roadmap signals, acquisition patterns |

---

## Output Format

Structure the output as a **standalone markdown file** saved to `tickets/COMPETITION/[company-slug]/deep-analysis.md`:

```markdown
# Deep Analysis - [COMPANY NAME]

**Research Date**: YYYY-MM-DD
**Confidence Level**: High / Medium / Low (based on data availability)

### Company Fundamentals

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Legal Entity | [value] | [source] | Confirmed/Estimated/Unknown |
| HQ Address | [value] | [source] | ... |
| Founded | [value] | [source] | ... |
| CEO | [value] | [source] | ... |
| CTO | [value] | [source] | ... |
| Ownership | [value] | [source] | ... |
| Employees (current) | [value] | [source] | ... |
| Employees (1yr ago) | [value] | [source] | ... |
| Employees (2yr ago) | [value] | [source] | ... |
| Revenue (current) | [value] | [source] | ... |
| Revenue (1yr ago) | [value] | [source] | ... |
| Revenue Growth | [value] | [source] | ... |
| Market Cap / Valuation | [value] | [source] | ... |

### Market Position

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Countries Active | [list] | [source] | ... |
| Customer Count | [value] | [source] | ... |
| Notable Customers | [list] | [source] | ... |
| Market Share | [value] | [source] | ... |
| Rankings / Awards | [list] | [source] | ... |

### Product & Technology

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Product Portfolio | [list with modules] | [source] | ... |
| Tech Stack | [languages, frameworks, DB] | [source] | ... |
| Deployment Model | [cloud/on-prem/hybrid] | [source] | ... |
| API Strategy | [REST/GraphQL/proprietary] | [source] | ... |
| Exchange Integrations | [list] | [source] | ... |
| Release Cadence | [continuous/quarterly/annual] | [source] | ... |

### AI & Innovation

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| AI Features in Production | [list] | [source] | ... |
| AI Roadmap | [announced features] | [source] | ... |
| AI Hiring Signals | [job count, roles] | [source] | ... |
| AI Partnerships | [list] | [source] | ... |
| Published Research | [papers, patents] | [source] | ... |
| AI Acquisitions | [list] | [source] | ... |

### Growth & Trajectory

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Revenue Growth (YoY) | [value] | [source] | ... |
| Employee Growth (YoY) | [value] | [source] | ... |
| Geographic Expansion | [new countries, 2yr] | [source] | ... |
| Product Launches (2yr) | [list] | [source] | ... |
| Acquisitions (3yr) | [list] | [source] | ... |
| Funding Rounds (3yr) | [list] | [source] | ... |
| Strategic Pivots | [description] | [source] | ... |

### Commodities & Specialization

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Commodities | [power, gas, carbon, etc.] | [source] | ... |
| Market Segments | [wholesale, retail, grid, etc.] | [source] | ... |
| Regulatory Compliance | [EMIR, REMIT, national] | [source] | ... |
| Protocol Support | [EDSN, ENTSO-E, TSO formats] | [source] | ... |

### Pricing & Business Model

| Data Point | Value | Source | Confidence |
|---|---|---|---|
| Pricing Model | [license/SaaS/usage-based] | [source] | ... |
| Est. Price Range | [range or "undisclosed"] | [source] | ... |
| Implementation Timeline | [weeks/months] | [source] | ... |
| Services vs Product Revenue | [split or estimate] | [source] | ... |

### Threat Assessment vs Eneve

**Direct Overlap Areas**:
- [Area 1]: [description of overlap and competitive dynamic]
- [Area 2]: [description]

**Where Competitor is Stronger**:
- [Strength 1]: [evidence]
- [Strength 2]: [evidence]

**Where Eneve is Stronger**:
- [Strength 1]: [evidence]
- [Strength 2]: [evidence]

**NL Market Entry Likelihood**: [High/Medium/Low] - [reasoning]

**Capability Expansion Likelihood**: [High/Medium/Low] - [reasoning]

**Strategic Implications**:
[2-3 sentences on what this means for Eneve's competitive position and what to watch for]
```

---

## Quality Criteria

- [ ] All 8 research categories addressed (no sections skipped)
- [ ] Each data point has a source attribution
- [ ] Each data point has a confidence level (Confirmed/Estimated/Unknown)
- [ ] Threat assessment is evidence-based, not speculative
- [ ] Existing identification data verified or corrected
- [ ] AI & Innovation section has concrete product features, not just marketing claims
- [ ] Growth data includes historical comparison (not just current snapshot)
- [ ] Output saved to `tickets/COMPETITION/[company-slug]/deep-analysis.md` (standalone file, not appended to main file)
- [ ] README.md status table updated

---

## Usage

### Priority 1: AI-Signal Companies (run these first)

```
@research-competitor Engrate @tickets/COMPETITION/engrate/
```

```
@research-competitor Volue ASA @tickets/COMPETITION/volue/
```

```
@research-competitor Previse Systems @tickets/COMPETITION/previse-systems-coral/
```

```
@research-competitor Sopra Steria cpX.Energy @tickets/COMPETITION/sopra-steria-cpx-energy/
```

```
@research-competitor Brady Technologies @tickets/COMPETITION/brady-technologies-powerdesk/
```

### Priority 2: Remaining Competitors

```
@research-competitor KISTERS @tickets/COMPETITION/kisters-belvis/
```

```
@research-competitor Hitachi Energy @tickets/COMPETITION/hitachi-energy/
```

```
@research-competitor Trayport @tickets/COMPETITION/trayport-periotheus/
```

```
@research-competitor Energy One @tickets/COMPETITION/energy-one-entrader/
```

```
@research-competitor ION Commodities @tickets/COMPETITION/ion-commodities-allegro/
```

### Priority 3: Ecosystem Players

```
@research-competitor CGI EDSN @tickets/COMPETITION/cgi-edsn/
```

```
@research-competitor Worldgrid ALTEN @tickets/COMPETITION/alten-worldgrid/
```

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read existing files**: Load the competitor's existing files from the company folder to understand current state of knowledge
2. **Read Eneve positioning**: Load `tickets/COMPETITION/README.md` for comparison baseline
3. **Plan search strategy**: For each research category, formulate 2-3 specific web search queries using company name, product names, and category-specific keywords
4. **Execute searches systematically**: Work through categories in order, recording findings with sources
5. **Cross-reference data**: When multiple sources provide different numbers, note the discrepancy and pick the most authoritative source
6. **Synthesize threat assessment**: Based on all data collected, form an evidence-based view of competitive threat to Eneve
7. **Format and write**: Structure findings in the Deep Analysis template and write to `tickets/COMPETITION/[company-slug]/deep-analysis.md` as a standalone file
8. **Update status**: Mark the competitor as "Deep analysis complete" in README.md

---

## Search Query Templates

Use year-agnostic patterns. Replace `[YEAR]` with current year, `[YEAR-1]`/`[YEAR-2]` with previous years. Combine company name with category-specific keywords. Example:

- `"[COMPANY]" employees revenue [YEAR-1] [YEAR]`
- `"[COMPANY]" AI features product [YEAR-1] [YEAR]`
- `"[PRODUCT]" technology stack architecture`

Full query templates for all 8 categories: see `.cursor/exemplars/analysis/market/research-competitor-exemplar.md`

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Private company, limited financials | Use proxy indicators (LinkedIn count, Crunchbase, job volume). Mark as "Estimated". |
| Non-English company website | Search in both English and local language. Check investor relations pages. |
| Contradictory data across sources | Prefer primary sources (annual report > LinkedIn > news). Note contradictions. |
| No AI/innovation data found | Try adjacent terms ("automation", "forecasting", "predictive"). Absence is a valid finding when search was thorough. |
| Company acquired/merged since identification | Research parent company. Update ownership. Assess impact on competitive positioning. |

Detailed troubleshooting with root causes and full solutions: see `.cursor/exemplars/analysis/market/research-competitor-exemplar.md`

---

## Data Quality Guidelines

| Confidence Level | Criteria |
|---|---|
| **Confirmed** | Official primary source (annual report, SEC filing, company website) |
| **Estimated** | Credible secondary source (LinkedIn, Crunchbase, analyst report) |
| **Unknown** | No reliable data found -- mark explicitly, do not guess |

If fewer than 50% of data points in a category can be filled, add a note explaining why and what research methods could help.

---

## Pattern Used

This prompt follows: `.cursor/templars/analysis/market/structured-web-research-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/research-competitor-exemplar.md`

---

## Related Prompts

- `analysis/market/research-company-history.prompt.md` - Corporate genealogy research (companion prompt)
- `analysis/market/generate-financial-dashboard.prompt.md` - Generate financial comparison dashboards from deep analysis data
- `prompt/create-new-prompt.prompt.md` - Template used to create this prompt
- `prompt/enhance-prompt.prompt.md` - For improving this prompt after first use

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: 2026-02-15
**Improved**: 2026-02-15 (improve-prompt + enhance-prompt applied: added tools/rules frontmatter, troubleshooting, data quality guidelines, time estimate, year-agnostic search templates, expanded related prompts)
**Extracted**: 2026-02-15 (templar + exemplar extracted; bulky sections trimmed to compact form with pointers)
**Context**: tickets/COMPETITION/ competitive landscape analysis
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
