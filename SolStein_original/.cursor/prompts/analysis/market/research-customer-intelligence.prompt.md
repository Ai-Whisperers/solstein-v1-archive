---
name: research-customer-intelligence
description: "Please research customer intelligence for an energy software competitor -- reference clients, win/loss signals, switching patterns, case studies, and concentration risk"
category: analysis
tags: competition, research, customers, win-loss, switching, case-studies, energy
argument-hint: "Company name and path to company folder (e.g., Hansen Technologies @tickets/COMPETITION/hansen-technologies/)"
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Research Customer Intelligence

Please perform a structured customer intelligence research session on an energy software competitor to Eneve's eBase platform. This prompt drives systematic web research across 5 customer-focused categories, producing a standalone `customer-intelligence.md` file in the competitor's folder.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Reveals where competitors actually win deals, not just where they theoretically compete
**Use When**: After initial competitor identification is complete and you need to understand customer dynamics

---

## Purpose

This prompt fills a gap left by the general `research-competitor` prompt, which captures "Notable Customers" as a simple name list under Market Position. Customer intelligence requires deeper context:

- **Who** are their customers, broken down by energy market segment?
- **When** did they win those customers (recent momentum vs legacy base)?
- **From whom** did customers switch (migration patterns)?
- **How** did implementations go (timelines, scope, outcomes)?
- **How concentrated** is their customer base (risk exposure)?
- **Do any overlap** with Eneve's customer base?

This data feeds directly into:
- FD-014 M&A Vulnerability assessment
- FD-016 Competitive Overlap analysis
- FD-020 Portfolio Risk evaluation

---

## Required Context

- **Company Name**: The competitor to research (e.g., "Hansen Technologies")
- **Company Folder**: Path to the competitor's folder in `tickets/COMPETITION/` (e.g., `@tickets/COMPETITION/hansen-technologies/`)
- **Eneve Context**: Reference `@tickets/COMPETITION/README.md` for Eneve's customer base summary

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read existing files**: Load the competitor's existing files to understand what customer data already exists
2. **Read Eneve context**: Load `tickets/COMPETITION/README.md` for overlap assessment baseline
3. **Select research mode**: Determine Quick, Standard, or Deep based on user instruction or default to Standard
4. **Plan search strategy**: For each applicable category, formulate 2-3 web search queries using the Search Query Templates
5. **Execute searches systematically**: Work through categories in order, recording findings with sources
6. **Build segment table**: Classify each identified customer into the correct energy market segment
7. **Cross-reference for overlap**: Compare identified customers against Eneve's known customer base
8. **Assess concentration risk**: Look for revenue dependency disclosures in annual reports
9. **Know when to stop**: Move to the next category when 3 consecutive searches yield no new findings, or when all search templates have been exhausted
10. **Format and write**: Structure findings in the Customer Intelligence template and write to `tickets/COMPETITION/[company-slug]/customer-intelligence.md`
11. **Update status**: Mark "Customer intelligence complete" in README.md

---

## Constraints

- **Public sources only**: Do not speculate on private contracts, undisclosed revenue, or confidential customer relationships. If evidence is indirect (e.g., customer logo on website without context), note this limitation.
- **Source attribution required**: Every finding must include a source reference (URL or publication name + date).
- **Confidence marking mandatory**: Every data point must carry a confidence level (Confirmed / Estimated / Unknown).
- **No speculation**: If fewer than 50% of data points in a category can be filled, add a note explaining why and what research methods could improve coverage.

---

## Usage Modes

### Quick Mode (10-15 min)
For initial scans or time-constrained sessions. Focus on Category 1 (Reference Clients) and Category 2 (Win/Loss Signals) only.

```
@research-customer-intelligence Hansen Technologies @tickets/COMPETITION/hansen-technologies/ --quick
```

### Standard Mode (20-40 min) -- Default
All 5 categories, balanced depth. Suitable for most competitors.

```
@research-customer-intelligence Hansen Technologies @tickets/COMPETITION/hansen-technologies/
```

### Deep Mode (45-90 min)
All 5 categories with extended search. For public companies with extensive disclosure, or for strategically critical competitors. Includes follow-up searches on individual customer relationships and cross-referencing multiple annual reports.

```
@research-customer-intelligence Hansen Technologies @tickets/COMPETITION/hansen-technologies/ --deep
```

---

## Process

**Time Estimates by Category**:

| Category | Quick | Standard | Deep |
|---|---|---|---|
| 1. Reference Client Inventory | 5-8 min | 8-12 min | 15-20 min |
| 2. Win/Loss Signals | 5-7 min | 5-10 min | 10-15 min |
| 3. Switching Patterns | -- | 3-7 min | 10-15 min |
| 4. Implementation Case Studies | -- | 3-7 min | 10-20 min |
| 5. Concentration & Overlap | -- | 3-5 min | 10-15 min |
| **Total** | **10-15 min** | **20-40 min** | **45-90 min** |

### Step 1: Read Existing Profile

Read the competitor's existing files (identification, deep-analysis, corporate-history) to understand what customer data we already have. Note any customer names already captured in the deep-analysis Market Position section.

### Step 2: Read Eneve Customer Context

Read `tickets/COMPETITION/README.md` to understand Eneve's current customer base. This is needed for the overlap assessment in Category 5.

### Step 3: Web Research by Category

For each applicable research category (see Usage Modes for which categories apply), perform targeted web searches. Prioritize sources in this order:
1. Official company press releases and news sections
2. Annual reports and investor presentations (public companies)
3. Case study and customer story pages on company website
4. Industry conference presentations (E-world, Enlit, CTRM London)
5. Energy industry publications (Energy Risk, Montel, ICIS, S&P Global)
6. LinkedIn company page (customer testimonials, shared posts)
7. Government tender databases and regulatory filings

### Step 4: Synthesize Findings

Organize all findings into the structured output template (see Output Format below). For each finding:
- Record with source attribution (URL or publication name + date)
- Mark confidence level: "Confirmed" / "Estimated" / "Unknown"
- Note contradictions between sources
- Prefer primary sources (annual reports, official announcements) over secondary sources

### Step 5: Write Customer Intelligence File

Write output to a **standalone file** in the competitor's folder:
- **File path**: `tickets/COMPETITION/[company-slug]/customer-intelligence.md`
- Create the company folder if it doesn't exist
- If a `customer-intelligence.md` already exists, replace it with the updated version

### Step 6: Update README Status

Update the Data Collection Status table in `tickets/COMPETITION/README.md` to reflect "Customer intelligence complete" for this competitor.

---

## Research Categories

### Category 1: Reference Client Inventory

Build a comprehensive list of known customers, organized by energy market segment.

| Data Point | Search Strategy |
|---|---|
| TSO customers | Press releases, annual reports, tender awards, conference references |
| DSO customers | Press releases, smart grid / metering project announcements |
| Energy supplier customers | Case studies, product pages, industry news |
| Energy trader customers | CTRM/ETRM vendor guides, exchange ISV listings, trading desk references |
| BRP (Balance Responsible Party) customers | Balancing market announcements, regulatory filings |
| Industrial / large consumer customers | Energy management case studies, sustainability reports |
| Total customer count | Annual reports, company website, investor presentations |
| Customer count by segment | Derived from above; mark segment-level counts as "Estimated" if not disclosed |

**Output**: Segment distribution table (see Output Format).

### Category 2: Win/Loss Signals

Identify recent customer wins, contract renewals, and expansions that indicate competitive momentum.

| Data Point | Search Strategy |
|---|---|
| New customer wins (last 2 years) | Press releases, news section, LinkedIn announcements |
| Contract renewals / extensions | Press releases, annual report revenue commentary |
| Upsell / expansion deals | Press releases mentioning "expanded", "additional modules", "phase 2" |
| Lost customers (if discoverable) | Competitor switch announcements, industry news, tender re-awards |
| Competitive displacement wins | Press releases mentioning "replaced", "migrated from", "selected over" |
| Geographic expansion via customers | New country entries announced via customer wins |

**Output**: Chronological win/loss timeline with source for each entry.

### Category 3: Switching Patterns

Document evidence of customers migrating between vendors -- especially relevant for customers leaving legacy platforms.

| Data Point | Search Strategy |
|---|---|
| Customers migrating TO this competitor | Press releases mentioning predecessor system, "replaced", "migrated" |
| Customers migrating FROM this competitor | Competitor announcements mentioning this company as predecessor |
| Legacy vendor displacement patterns | Which vendors are being replaced most often? |
| Migration triggers | Why customers switch (cost, features, cloud, regulation, vendor sunset) |
| Migration timelines | How long do transitions take? (from case studies or announcements) |
| Platform consolidation trends | Customers consolidating multiple vendors into one |

**Output**: Switching pattern evidence table with directional arrows (From -> To) and source attribution.

### Category 4: Implementation Case Studies

Gather published case studies, project summaries, and implementation references.

| Data Point | Search Strategy |
|---|---|
| Published case studies | Company website case study page, PDF downloads |
| Conference presentations | E-world, Enlit, CTRM London, Eurelectric slide decks |
| Implementation timeline | Case study details: project duration from start to go-live |
| Scope and modules deployed | Which products/modules implemented per case study |
| Success metrics reported | Quantified outcomes (cost savings, efficiency gains, time reduction) |
| Implementation partner involved | Systems integrators or consultants mentioned |
| Customer quotes / testimonials | Website testimonials page, press releases, LinkedIn recommendations |

**Output**: Case study summary table with key metrics per study.

### Category 5: Customer Concentration & Eneve Overlap

Assess dependency on large accounts and check for overlap with Eneve's customer base.

| Data Point | Search Strategy |
|---|---|
| Top customers by revenue (if disclosed) | Annual reports (public companies often disclose concentration) |
| Revenue concentration risk | "No single customer exceeds X% of revenue" disclosures |
| Customer churn indicators | Annual report commentary, employee reviews mentioning customer issues |
| Eneve customer overlap | Cross-reference identified customers against Eneve's known customer base |
| Dual-vendor situations | Customers using both Eneve and this competitor (different modules/markets) |
| At-risk Eneve customers | Eneve customers known to be evaluating alternatives |

**Output**: Concentration risk assessment + Eneve overlap table.

---

## Examples (Few-Shot)

### Example 1: Filled Reference Client Inventory (Category 1)

This shows what a completed segment distribution looks like for a hypothetical competitor:

**Input**: `@research-customer-intelligence ExampleSoft @tickets/COMPETITION/examplesoft/`

**Excerpt from output (Category 1)**:

```markdown
## 1. Reference Client Inventory

### Segment Distribution

| Segment | Count | Notable Names | Source | Confidence |
|---|---|---|---|---|
| TSO | 3 | TenneT, Elia, National Grid ESO | Annual Report 2025, p.14 | Confirmed |
| DSO | 5 | Enexis, Liander, Stedin, UK Power Networks, E.ON Netz | Press releases 2023-2025 | Confirmed |
| Supplier | 12 | Vattenfall, Eneco, Shell Energy | Case study page + LinkedIn | Estimated |
| Trader | 2 | Axpo, Statkraft | ETRM vendor guide 2024 | Estimated |
| BRP | 0 | -- | No evidence found | Unknown |
| Industrial | 4 | BASF, Tata Steel, Dow Chemical, Air Liquide | Sustainability report references | Estimated |
| **Total Identified** | **26** | | | |

### Key Accounts

- **TenneT** (TSO) -- Grid balancing and congestion management modules since 2019. Expanded to include frequency restoration in 2023. Source: ExampleSoft press release 2023-06-15
- **Vattenfall** (Supplier) -- Full ETRM suite across Nordic and Dutch operations. Source: Enlit 2024 conference presentation
```

### Example 2: Filled Win/Loss Entry (Category 2)

```markdown
## 2. Win/Loss Signals

### Recent Wins (Last 2 Years)

| Date | Customer | Type | Details | Source |
|---|---|---|---|---|
| 2025-09 | Elia Group | Expansion | Added frequency ancillary services module to existing grid management contract | Press release 2025-09-12 |
| 2025-03 | Shell Energy Europe | New Win | Selected for European gas and power trading platform, replacing in-house system | Energy Risk article 2025-03-28 |
| 2024-11 | UK Power Networks | Renewal | 5-year contract extension for distribution management suite | Annual Report 2024, p.22 |

### Known Losses

| Date | Customer | Switched To | Reason (if known) | Source |
|---|---|---|---|---|
| 2024-06 | Statkraft (Nordic ops) | Competitor X | Cloud-native requirement; ExampleSoft's on-prem architecture cited | Industry source (Montel 2024-07) |
```

---

## Output Format

Structure output as a **standalone markdown file** saved to `tickets/COMPETITION/[company-slug]/customer-intelligence.md`:

```markdown
# Customer Intelligence - [COMPANY NAME]

**Research Date**: YYYY-MM-DD
**Research Mode**: Quick / Standard / Deep
**Confidence Level**: High / Medium / Low (based on data availability)
**Data Sources**: [count] sources consulted

---

## Customer Overview

| Metric | Value | Source | Confidence |
|---|---|---|---|
| Total Customers (claimed) | [value] | [source] | Confirmed/Estimated |
| Total Customers (verified) | [value] | [based on evidence below] | Estimated |
| Customer Growth Trend | [growing/stable/declining] | [source] | Estimated |
| Geographic Spread | [countries] | [source] | Confirmed/Estimated |

---

## 1. Reference Client Inventory

### Segment Distribution

| Segment | Count | Notable Names | Source | Confidence |
|---|---|---|---|---|
| TSO | [n] | [names] | [source] | ... |
| DSO | [n] | [names] | [source] | ... |
| Supplier | [n] | [names] | [source] | ... |
| Trader | [n] | [names] | [source] | ... |
| BRP | [n] | [names] | [source] | ... |
| Industrial | [n] | [names] | [source] | ... |
| **Total Identified** | **[n]** | | | |

### Key Accounts

For each major customer identified, provide context:

- **[Customer Name]** ([Segment]) -- [what they use, since when, scope]. Source: [source]
- **[Customer Name]** ([Segment]) -- [context]. Source: [source]

---

## 2. Win/Loss Signals

### Recent Wins (Last 2 Years)

| Date | Customer | Type | Details | Source |
|---|---|---|---|---|
| YYYY-MM | [name] | New Win / Renewal / Expansion | [brief description] | [source] |
| YYYY-MM | [name] | ... | ... | ... |

### Known Losses

| Date | Customer | Switched To | Reason (if known) | Source |
|---|---|---|---|---|
| YYYY-MM | [name] | [competitor] | [reason] | [source] |

### Win Rate Indicators

[Qualitative assessment of competitive momentum based on volume and pattern of wins vs losses]

---

## 3. Switching Patterns

### Migration Evidence

| Date | Customer | From | To | Trigger | Source |
|---|---|---|---|---|---|
| YYYY | [name] | [old vendor] | [COMPANY] | [reason] | [source] |
| YYYY | [name] | [COMPANY] | [new vendor] | [reason] | [source] |

### Pattern Analysis

**Vendors most often replaced by [COMPANY]**:
- [Vendor 1]: [n] known replacements -- [context]
- [Vendor 2]: [n] known replacements -- [context]

**Vendors replacing [COMPANY]**:
- [Vendor 1]: [n] known replacements -- [context]

**Common Migration Triggers**:
- [Trigger 1]: [evidence]
- [Trigger 2]: [evidence]

**Typical Migration Timeline**: [duration based on evidence]

---

## 4. Implementation Case Studies

### Published Case Studies

| Customer | Year | Scope | Duration | Key Metrics | Source |
|---|---|---|---|---|---|
| [name] | YYYY | [modules/scope] | [duration] | [outcomes] | [URL or publication] |
| [name] | YYYY | ... | ... | ... | ... |

### Implementation Patterns

- **Average implementation timeline**: [range based on evidence]
- **Common modules deployed first**: [list]
- **Implementation partners used**: [list]
- **Success metrics typically reported**: [types of KPIs]

---

## 5. Customer Concentration & Eneve Overlap

### Concentration Risk

| Metric | Value | Source | Confidence |
|---|---|---|---|
| Top customer revenue share | [X%] or "undisclosed" | [source] | ... |
| Top 5 customers revenue share | [X%] or "undisclosed" | [source] | ... |
| Concentration risk level | High / Medium / Low | [analysis] | Estimated |

**Assessment**: [1-2 sentences on how dependent this competitor is on a small number of accounts]

### Eneve Customer Overlap

| Customer | Eneve Relationship | Competitor Relationship | Risk Level |
|---|---|---|---|
| [name] | [what Eneve provides] | [what competitor provides] | High/Medium/Low |

**Overlap Assessment**: [Summary of dual-vendor situations, competitive tension, and risk to Eneve]

### At-Risk Indicators

[Any evidence of Eneve customers evaluating this competitor, or vice versa]

---

## Quality Assessment

- Data completeness: [X/5 categories with substantive data]
- Source quality: [primary/secondary/mixed]
- Key data gaps: [what couldn't be found and why]
- Recommended follow-up: [specific research that would fill gaps]
```

---

## Data Quality Guidelines

| Confidence Level | Criteria |
|---|---|
| **Confirmed** | Official primary source: press release, annual report, case study page, SEC/regulatory filing |
| **Estimated** | Credible secondary source: industry publication, LinkedIn, analyst report, conference slides |
| **Unknown** | No reliable data found -- mark explicitly, do not guess or speculate |

If fewer than 50% of data points in a category can be filled, add a note explaining why and what research methods could improve coverage.

---

## Search Query Templates

Replace `[COMPANY]` with the competitor name and `[PRODUCT]` with their product name. Use current and recent years.

| Category | Query Templates |
|---|---|
| Reference Clients | `"[COMPANY]" customers energy`, `"[PRODUCT]" case study`, `"[COMPANY]" press release customer` |
| Win/Loss Signals | `"[COMPANY]" "selected by"`, `"[COMPANY]" "new customer"`, `"[COMPANY]" "contract award"` |
| Switching Patterns | `"migrated from" "[COMPANY]"`, `"[COMPANY]" "replaced" energy`, `"switched to" "[PRODUCT]"` |
| Case Studies | `"[COMPANY]" case study energy`, `"[PRODUCT]" implementation`, `"[COMPANY]" go-live` |
| Concentration | `"[COMPANY]" annual report customers`, `"[COMPANY]" revenue concentration` |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Private company, no disclosed customers | Check press releases, conference talks, partner pages, exchange ISV listings. LinkedIn "services" section sometimes lists client logos. |
| Customers found but no segment data | Classify based on customer's own business (check customer's website to determine if TSO/DSO/supplier/trader). |
| No switching pattern evidence | Absence is a valid finding -- document as "no public migration evidence found." Check tender databases for re-procurements. |
| No published case studies | Check conference presentation archives (E-world, Enlit), YouTube for recorded demos/talks, SlideShare. |
| Can't determine Eneve overlap | Note as "overlap assessment requires Eneve customer list not available in public domain." Flag for internal follow-up. |
| Research yielding very thin results | Switch to Quick mode; document gaps explicitly. Thin results are themselves a competitive insight (low market visibility). |

---

## Quality Criteria

- [ ] All applicable research categories addressed (5 for Standard/Deep, 2 for Quick)
- [ ] Segment distribution table with customer counts per segment
- [ ] Each customer attribution includes source and confidence level
- [ ] Win/loss signals documented chronologically with dates
- [ ] Switching pattern evidence includes directional migration (From -> To)
- [ ] At least 1 implementation case study captured (if any exist publicly)
- [ ] Customer concentration risk assessed
- [ ] Eneve customer overlap assessment completed
- [ ] All data from public sources only (no speculation on private contracts)
- [ ] Output saved to `tickets/COMPETITION/[company-slug]/customer-intelligence.md`
- [ ] README.md status table updated
- [ ] Research mode noted in output header

---

## Usage

### Priority: Public Companies (most data available)

```
@research-customer-intelligence Hansen Technologies @tickets/COMPETITION/hansen-technologies/
```

```
@research-customer-intelligence Volue ASA @tickets/COMPETITION/volue/
```

### Other Competitors

```
@research-customer-intelligence KISTERS @tickets/COMPETITION/kisters-belvis/
```

```
@research-customer-intelligence Hitachi Energy @tickets/COMPETITION/hitachi-energy/
```

```
@research-customer-intelligence Brady Technologies @tickets/COMPETITION/brady-technologies-powerdesk/
```

### Quick Mode (time-constrained)

```
@research-customer-intelligence KISTERS @tickets/COMPETITION/kisters-belvis/ --quick
```

---

## Related Prompts

- `analysis/market/research-competitor.prompt.md` - General deep-dive competitive research (companion prompt)
- `analysis/market/research-company-history.prompt.md` - Corporate genealogy research
- `analysis/market/research-financial-growth.prompt.md` - Financial metrics and growth analysis
- `analysis/market/generate-financial-dashboard.prompt.md` - Dashboard generation from research data

---

## Pattern Used

This prompt follows: `.cursor/templars/analysis/market/structured-web-research-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/research-customer-intelligence-exemplar.md`

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: 2026-02-17
**Improved**: 2026-02-17 (improve-prompt + enhance-prompt applied)
**Context**: tickets/FINANCIALDASHBOARD/FD-029-customer-intelligence-prompt
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0
**Companion to**: `analysis/market/research-competitor.prompt.md`
