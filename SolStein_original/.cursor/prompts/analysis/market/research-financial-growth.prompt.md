---
name: research-financial-growth
description: "Please perform a deep financial and growth research analysis on an energy software competitor"
category: analysis
tags: competition, financial, growth, revenue, funding, trajectory, dinosaur-vs-rocket
argument-hint: "Company name and path to company folder (e.g., Volue ASA @tickets/COMPETITION/volue/)"
---

# Research Financial Growth - Per-Competitor Deep-Dive

Please perform a structured deep financial and growth research session on an energy software competitor to Eneve's eBase platform. This prompt drives systematic web research focused exclusively on financial metrics, growth trajectories, funding, and M&A activity, then appends a `## Financial & Growth Deep-Dive` section to the competitor's existing file.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Converts identification-level profiles into hard financial intelligence with scoreable growth metrics
**Use When**: After initial competitor identification (or deep analysis) is complete and detailed financial/growth data is needed

---

## Purpose

This prompt goes deeper than the general `research-competitor` prompt on financial dimensions by:

- Collecting 3-5 year revenue histories (not just current snapshots)
- Tracking funding rounds with amounts, investors, and valuations
- Measuring employee growth trajectories over time
- Mapping M&A activity with deal rationale
- Scoring SaaS transition maturity
- Producing a numeric **Growth Scorecard** (1-10 per dimension) that feeds into the cross-competitor financial dashboard

The end goal: identify which competitors are **rockets** (explosive growth, heavy investment, AI-native) and which are **dinosaurs** (flat revenue, no funding, legacy mode). This is the data backbone for Eneve's wake-up call.

---

## Required Context

- **Company Name**: The competitor to research (e.g., "Volue ASA")
- **Company Folder**: Path to the competitor's folder in `tickets/COMPETITION/` (e.g., `@tickets/COMPETITION/volue/`)
- **Eneve Context**: Reference `@tickets/COMPETITION/README.md` for Eneve's positioning and the comparison matrix

---

## Process

### Step 1: Read Existing Profile

Read the competitor's existing files from the company folder. Extract any financial data already present in identification, deep analysis, or corporate history files. Note gaps.

### Step 2: Read Eneve Positioning

Read `tickets/COMPETITION/README.md` to understand Eneve's current trajectory for contrast.

### Step 3: Web Research by Financial Category

For each of the 6 financial research categories below, perform targeted web searches. Prioritize these source types (in order of reliability):

1. **Annual reports / financial filings** (most reliable for public companies)
2. **Stock exchange filings** (Oslo Bors, Euronext, LSE, ASX)
3. **Crunchbase / PitchBook / CB Insights** (funding rounds, valuations)
4. **Press releases** (acquisitions, funding announcements)
5. **LinkedIn company page** (employee count trends)
6. **Glassdoor / Indeed** (employee growth signals, open positions)
7. **Industry analyst reports** (Chartis, Energy Risk, IDC)
8. **News articles** (TechCrunch, EU-Startups, Sifted, energy trade press)
9. **Company website** (about page, investor relations, careers page)
10. **Wayback Machine** (historical employee counts, revenue claims)

### Step 4: Build Revenue Timeline

Construct the most complete revenue timeline possible. For each year, record:

- Revenue figure (in original currency AND EUR equivalent)
- Source and confidence level
- YoY growth rate

If exact figures are unavailable, estimate ranges and mark as "Estimated".

### Step 5: Build Employee Timeline

Construct a multi-year employee count timeline. Sources: LinkedIn, annual reports, Glassdoor, press releases. Calculate YoY growth rates.

### Step 6: Score Growth Dimensions

Using the **Growth Scorecard Criteria** defined below, assign a score (1-10) for each of the 6 dimensions. Be rigorous -- use the scoring rubric, not gut feeling.

### Step 7: Write Financial Growth File

Write the financial & growth output to a **separate file** within the competitor's folder:

- **File path**: `tickets/COMPETITION/[company-slug]/financial-growth.md`
- **Create the company folder** if it doesn't exist yet (e.g., `tickets/COMPETITION/volue/`)
- Do NOT append to the main identification file -- keep research outputs in their own dedicated files
- If a `financial-growth.md` already exists, replace it with the updated version

### Step 8: Update README Status

Update the Data Collection Status table in `tickets/COMPETITION/README.md` to reflect "Financial analysis complete" for this competitor.

---

## Research Categories

### Category 1: Revenue & Profitability

| Data Point | Search Strategy |
| --- | --- |
| Revenue (current year) | Annual report, financial filings, press releases |
| Revenue (1yr ago) | Annual report, financial filings |
| Revenue (2yr ago) | Annual report, historical filings |
| Revenue (3yr ago) | Annual report, historical filings, Wayback Machine |
| Revenue (4-5yr ago, if available) | Historical filings, press archives |
| Revenue CAGR (3yr and 5yr) | Calculated from above |
| YoY growth rate (each year) | Calculated from above |
| Currency and EUR equivalent | ECB exchange rates for conversion |
| EBITDA / Operating margin | Annual report, financial filings |
| Net profit / loss | Annual report, financial filings |
| Recurring revenue % | Annual report, SaaS metrics disclosures |
| SaaS revenue % | Annual report, earnings calls |
| Revenue per employee | Calculated: revenue / headcount |
| Revenue by segment (if disclosed) | Annual report segment reporting |

### Category 2: Funding & Investment

| Data Point | Search Strategy |
| --- | --- |
| All funding rounds (date, amount, series) | Crunchbase, PitchBook, press releases |
| Lead investors per round | Crunchbase, press releases |
| Total funding raised to date | Crunchbase, calculated sum |
| Latest valuation (pre/post-money) | Crunchbase, PitchBook, press releases |
| IPO date and price (if applicable) | Stock exchange filings |
| Delisting (if applicable) | Stock exchange filings, press releases |
| PE/VC backing (current investors) | Crunchbase, annual report, investor pages |
| Debt financing / credit facilities | Annual report, financial filings |
| Government grants / subsidies | Press releases, EU funding databases |
| Acquisition war chest signals | Cash on balance sheet, undrawn facilities, PE dry powder |

### Category 3: Employee Growth

| Data Point | Search Strategy |
| --- | --- |
| Headcount (current) | LinkedIn company page, annual report |
| Headcount (1yr ago) | LinkedIn historical, annual report, Wayback Machine |
| Headcount (2yr ago) | LinkedIn historical, annual report |
| Headcount (3yr ago) | LinkedIn historical, annual report |
| Headcount (4-5yr ago) | Historical data, press releases |
| YoY growth rate (each year) | Calculated from above |
| Employee CAGR (3yr) | Calculated from above |
| Current open positions (total) | Careers page, LinkedIn jobs, Indeed |
| AI/ML/Data Science open roles | Filtered job search on careers page |
| Engineering vs non-engineering split | Job postings, LinkedIn, annual report |
| Geographic distribution of hiring | Job postings by location |
| Key recent hires (C-level, VP) | LinkedIn, press releases |

### Category 4: Geographic & Market Expansion

| Data Point | Search Strategy |
| --- | --- |
| New countries entered (last 3yr) | Press releases, new office announcements |
| New offices opened (last 3yr) | Press releases, company website, LinkedIn |
| New exchange integrations (last 3yr) | Product announcements, press releases |
| New regulatory market entries | Press releases, compliance announcements |
| International revenue % (if disclosed) | Annual report segment reporting |
| Expansion strategy signals | CEO interviews, annual report strategy sections |

### Category 5: M&A Activity

| Data Point | Search Strategy |
| --- | --- |
| Acquisitions made (last 5yr) | Crunchbase, press releases, M&A databases |
| Each acquisition: target, date, price | Press releases, Crunchbase |
| Each acquisition: strategic rationale | Press releases, CEO quotes |
| Each acquisition: capability gained | Product analysis, press releases |
| Divestitures (last 5yr) | Press releases, annual reports |
| Been acquired by (if applicable) | Press releases, Crunchbase |
| M&A pipeline signals | CEO interviews, analyst commentary |
| Integration success indicators | Post-acquisition product launches, customer growth |

### Category 6: SaaS Transition Metrics

| Data Point | Search Strategy |
| --- | --- |
| Deployment model (cloud/on-prem/hybrid) | Product pages, documentation |
| Cloud revenue % (current) | Annual report, earnings calls |
| Cloud revenue % (1yr ago, 2yr ago) | Historical financial reports |
| Recurring revenue % trajectory | Multi-year annual reports |
| Customer churn / retention rate | Annual report, earnings calls |
| Average contract value signals | Annual report (ARR / customer count) |
| Platform modernization evidence | Job postings (tech stack), press releases |
| Migration timeline (on-prem to cloud) | Product roadmap, press releases |

---

## Growth Scorecard Criteria

Score each dimension 1-10 using these explicit criteria. The scores must be comparable across competitors.

### Revenue Growth (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | Revenue CAGR >30% over 3yr, or explosive YoY growth >50% |
| 7-8 | Revenue CAGR 20-30% over 3yr, strong consistent growth |
| 5-6 | Revenue CAGR 10-20% over 3yr, solid growth |
| 3-4 | Revenue CAGR 5-10% over 3yr, modest growth |
| 1-2 | Revenue CAGR <5%, flat, or declining |

### Funding Momentum (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | >EUR 50M raised in last 3yr, or recent round at >EUR 200M valuation |
| 7-8 | EUR 20-50M raised in last 3yr, strong investor backing |
| 5-6 | EUR 5-20M raised, or significant PE/VC backing |
| 3-4 | Small funding (<EUR 5M), or bootstrap with profitability |
| 1-2 | No external funding, no visible investment, or parent company neglect |

### Employee Growth (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | Employee CAGR >25% over 3yr, aggressive hiring across geographies |
| 7-8 | Employee CAGR 15-25%, strong hiring with AI/ML roles |
| 5-6 | Employee CAGR 5-15%, steady growth |
| 3-4 | Employee CAGR 0-5%, stable but not growing |
| 1-2 | Flat or declining headcount, layoffs, or hiring freeze signals |

### Geographic Expansion (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | Entered 3+ new countries in last 3yr, or intercontinental expansion |
| 7-8 | Entered 2-3 new countries, new offices, active international push |
| 5-6 | Entered 1-2 new countries, or expanding within existing region |
| 3-4 | No new countries, but serving multiple markets |
| 1-2 | Single-country focus, no expansion signals |

### M&A Activity (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | 3+ acquisitions in last 3yr, or transformative acquisition (>30% of revenue) |
| 7-8 | 2-3 acquisitions, clear capability-building pattern |
| 5-6 | 1-2 small acquisitions, or been acquired by larger player |
| 3-4 | No acquisitions but actively exploring (analyst/CEO signals) |
| 1-2 | No M&A activity, no signals, inward-focused |

### SaaS Maturity (1-10)

| Score | Criteria |
| --- | --- |
| 9-10 | Cloud-native from founding, or >80% recurring revenue, full SaaS |
| 7-8 | 60-80% recurring revenue, active SaaS migration, modern stack |
| 5-6 | 30-60% recurring revenue, hybrid model, transitioning |
| 3-4 | <30% recurring, on-premise dominant, early cloud experiments |
| 1-2 | Fully on-premise, no cloud strategy, legacy architecture |

---

## Output Format

Structure the output as a **standalone markdown file** saved to `tickets/COMPETITION/[company-slug]/financial-growth.md`:

````markdown
# Financial & Growth Deep-Dive - [COMPANY NAME]

**Research Date**: YYYY-MM-DD
**Data Availability**: High / Medium / Low (public companies = High, funded startups = Medium, private/bootstrapped = Low)

### Revenue Timeline

| Year | Revenue | Currency | EUR Equivalent | YoY Growth | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 2026 (est.) | [value] | [curr] | [EUR] | [%] | [source] | Estimated |
| 2025 | [value] | [curr] | [EUR] | [%] | [source] | Confirmed/Estimated |
| 2024 | [value] | [curr] | [EUR] | [%] | [source] | ... |
| 2023 | [value] | [curr] | [EUR] | [%] | [source] | ... |
| 2022 | [value] | [curr] | [EUR] | [%] | [source] | ... |
| 2021 | [value] | [curr] | [EUR] | [%] | [source] | ... |

**Revenue CAGR (3yr)**: [X]%
**Revenue CAGR (5yr)**: [X]% (if data available)

#### Revenue Trend Chart

(Generate a Mermaid line chart using the Revenue Timeline data above)

```mermaid
xychart-beta
    title "[COMPANY] Revenue Trend (EUR M)"
    x-axis [2021, 2022, 2023, 2024, 2025]
    y-axis "EUR Millions" 0 --> [max]
    line [val1, val2, val3, val4, val5]
```

### Profitability

| Data Point | Value | Source | Confidence |
| --- | --- | --- | --- |
| EBITDA (current) | [value] | [source] | ... |
| EBITDA Margin | [%] | [source] | ... |
| EBITDA Margin (1yr ago) | [%] | [source] | ... |
| Net Profit / Loss | [value] | [source] | ... |
| Recurring Revenue % | [%] | [source] | ... |
| SaaS Revenue % | [%] | [source] | ... |
| Revenue per Employee | EUR [value] | Calculated | ... |

### Funding & Investment History

| Date | Round | Amount | Lead Investor(s) | Valuation | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| [date] | [Series X / PE / IPO] | [amount] | [investors] | [pre/post] | [source] | ... |

**Total Raised**: EUR [amount]
**Latest Valuation**: EUR [amount] ([date])
**Current Investors**: [list of key investors with ownership % if known]
**War Chest Signals**: [cash on hand, undrawn facilities, PE dry powder]

### Employee Timeline

| Year | Headcount | YoY Growth | Source | Confidence |
| --- | --- | --- | --- | --- |
| 2026 (current) | [value] | [%] | [source] | ... |
| 2025 | [value] | [%] | [source] | ... |
| 2024 | [value] | [%] | [source] | ... |
| 2023 | [value] | [%] | [source] | ... |
| 2022 | [value] | [%] | [source] | ... |
| 2021 | [value] | [%] | [source] | ... |

**Employee CAGR (3yr)**: [X]%
**Current Open Positions**: [total] (of which [N] AI/ML/Data Science)
**Hiring Hotspots**: [cities/countries with most open roles]

#### Employee Growth Chart

(Generate a Mermaid line chart using the Employee Timeline data above)

```mermaid
xychart-beta
    title "[COMPANY] Employee Growth"
    x-axis [2021, 2022, 2023, 2024, 2025, 2026]
    y-axis "Headcount" 0 --> [max]
    line [val1, val2, val3, val4, val5, val6]
```

### Geographic & Market Expansion

| Year | Expansion Event | Details | Source | Confidence |
| --- | --- | --- | --- | --- |
| [year] | [new country / office / exchange] | [details] | [source] | ... |

**International Revenue %**: [% if disclosed]
**Expansion Trajectory**: [1-2 sentence summary of direction and pace]

### M&A Activity

| Date | Target | Deal Size | Capability Gained | Strategic Rationale | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| [date] | [company] | [EUR amount] | [what was acquired] | [why] | [source] | ... |

**Divestitures**: [list or "None"]
**M&A Pattern**: [1-2 sentence summary: capability-building, geographic, consolidation, etc.]

### SaaS Transition Metrics

| Data Point | Value | Source | Confidence |
| --- | --- | --- | --- |
| Deployment Model | [cloud-native / SaaS / hybrid / on-prem] | [source] | ... |
| Cloud Revenue % (current) | [%] | [source] | ... |
| Cloud Revenue % (1yr ago) | [%] | [source] | ... |
| Cloud Revenue % (2yr ago) | [%] | [source] | ... |
| Recurring Revenue % | [%] | [source] | ... |
| Platform Stack | [languages, cloud provider, architecture] | [source] | ... |
| Migration Status | [complete / in-progress / planned / none] | [source] | ... |

### Growth Scorecard

| Dimension | Score (1-10) | Evidence Summary |
| --- | --- | --- |
| Revenue Growth | [X] | [1-line justification citing CAGR or key metric] |
| Funding Momentum | [X] | [1-line justification citing total raised or key round] |
| Employee Growth | [X] | [1-line justification citing CAGR or headcount trend] |
| Geographic Expansion | [X] | [1-line justification citing countries/offices added] |
| M&A Activity | [X] | [1-line justification citing deal count or pattern] |
| SaaS Maturity | [X] | [1-line justification citing recurring revenue % or model] |
| **COMPOSITE SCORE** | **[avg]** | **[Classification: Rocket / Riser / Steady / Dinosaur]** |

**Classification Thresholds**:

- **Rocket** (avg 7.0-10.0): Explosive growth, heavy investment, market disruptor
- **Riser** (avg 5.0-6.9): Strong growth signals, investing in future, accelerating
- **Steady** (avg 3.0-4.9): Stable but not transforming, evolutionary
- **Dinosaur** (avg 1.0-2.9): Flat or declining, legacy mode, no visible investment

#### Growth Scorecard Radar

(Generate a Mermaid bar chart visualizing the 6 dimension scores for at-a-glance comparison)

```mermaid
xychart-beta
    title "[COMPANY] Growth Scorecard"
    x-axis ["Revenue", "Funding", "Employees", "Geography", "M&A", "SaaS"]
    y-axis "Score" 0 --> 10
    bar [revScore, fundScore, empScore, geoScore, maScore, saasScore]
```

> The bar chart above gives immediate visual impact -- tall bars = strong dimensions, short bars = vulnerabilities. Combined with the composite score, this creates a "fingerprint" for each competitor.

````

---

## Quality Criteria

- [ ] All 6 financial research categories addressed (no sections skipped)
- [ ] Revenue timeline has minimum 3 years of data (or explicit "Unknown" entries with explanation)
- [ ] Employee timeline has minimum 3 years of data
- [ ] Every data point has a source attribution
- [ ] Every data point has a confidence level (Confirmed/Estimated/Unknown)
- [ ] Revenue figures include both original currency AND EUR equivalent
- [ ] Growth Scorecard scores follow the explicit rubric (not gut feeling)
- [ ] Composite score calculated as average of 6 dimensions
- [ ] Classification matches composite score thresholds
- [ ] Output saved to `tickets/COMPETITION/[company-slug]/financial-growth.md` (standalone file, not appended to main file)
- [ ] README.md status table updated to "Financial analysis complete"

---

## Examples (Few-Shot)

### Example: Public Company (Volue ASA - Data-Rich)

A public company like Volue has annual reports on Oslo Bors. Expected output quality: **High**. Revenue Timeline: 5yr from annual reports with EUR conversion. Composite: 6.8 = **Riser**. Scores: Revenue 7, Funding 5, Employees 7, Geography 7, M&A 9, SaaS 6.

### Example: VC-Funded Startup (Engrate - Data-Scarce)

Seed-stage with limited public data. Expected output quality: **Low-Medium**. Revenue estimated from employee count. Composite: 5.7 = **Riser** (high variance). Mark most data as "Estimated".

### Example: Private Legacy Company (Schleupen - Data-Minimal)

Private, no VC backing. Expected output quality: **Low**. Heavy "Unknown" markers. Composite: ~3.0 = **Steady/Dinosaur** boundary. Search XING and German trade press.

> **Full examples with detailed breakdowns**: See `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md`

---

## Troubleshooting

| Problem | Quick Solution |
| --- | --- |
| No financial data (private/bootstrapped) | Use proxy: employees x EUR 150-250K. Check government filings (Bundesanzeiger, KVK, Companies House). Mark as "Estimated (proxy)". |
| Conflicting data sources | Prefer: annual report > filing > press release > Crunchbase > news. Use conservative figure for scoring. |
| Company recently acquired/delisted | Use pre-acquisition financials. Search parent segment reporting. Mark cutoff year. |
| Currency conversion across years | Use annual average EUR rate per year from ECB Statistical Data Warehouse, not today's rate. |

> **Detailed troubleshooting with full solutions**: See `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md`

---

## Search Query Templates

Use these as starting points, adapting company/product names:

**Revenue & Financials**:

- `"[COMPANY]" revenue 2023 2024 2025 annual report`
- `"[COMPANY]" financial results earnings EBITDA`
- `"[COMPANY]" recurring revenue SaaS ARR`
- `"[COMPANY]" annual report PDF investor relations`

**Funding**:

- `"[COMPANY]" funding round series investors 2024 2025 2026`
- `"[COMPANY]" valuation Crunchbase PitchBook`
- `"[COMPANY]" private equity venture capital investment`
- `"[COMPANY]" IPO stock exchange listing`

**Employee Growth**:

- `"[COMPANY]" employees headcount LinkedIn`
- `"[COMPANY]" hiring growth jobs open positions`
- `"[COMPANY]" AI ML data science job posting`
- `site:linkedin.com "[COMPANY]" energy employees`

**M&A**:

- `"[COMPANY]" acquisition 2022 2023 2024 2025`
- `"[COMPANY]" acquired merger energy software`
- `"[COMPANY]" divestiture sold business unit`

**SaaS / Cloud**:

- `"[COMPANY]" cloud SaaS migration platform`
- `"[COMPANY]" recurring revenue cloud transition`
- `"[COMPANY]" "[PRODUCT]" cloud-native architecture`

---

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read existing files**: Load the competitor's files from the company folder to extract any financial data already captured
2. **Read Eneve positioning**: Load `tickets/COMPETITION/README.md` for context
3. **Classify company type** and follow the appropriate research path:

### Company-Type Decision Tree

```text
Is the company publicly listed?
├── YES → Path A: Public Company
│   ├── Search: Annual reports, stock exchange filings, investor relations page
│   ├── Expected data quality: HIGH (3-5yr revenue, margins, headcount)
│   └── Start with: "[COMPANY] annual report [YEAR] PDF"
│
├── RECENTLY DELISTED / PE-ACQUIRED → Path B: Post-Public
│   ├── Search: Last public filings + PE firm portfolio page + press releases
│   ├── Expected data quality: MEDIUM (historical + sparse recent)
│   └── Start with: "[COMPANY] [PE FIRM] acquisition annual report"
│
├── VC-FUNDED STARTUP → Path C: Funded Private
│   ├── Search: Crunchbase + PitchBook + funding press releases + LinkedIn
│   ├── Expected data quality: MEDIUM (funding data good, revenue estimates)
│   └── Start with: "[COMPANY] Crunchbase funding series"
│
└── PRIVATE / BOOTSTRAPPED → Path D: Opaque
    ├── Search: LinkedIn headcount + government filings + trade press + proxies
    ├── Expected data quality: LOW (heavy estimation required)
    └── Start with: "[COMPANY] LinkedIn employees" + country-specific registries
        (DE: Bundesanzeiger, NL: KVK, UK: Companies House, NO: Brønnøysund)
```

1. **Build timelines first**: Revenue and employee timelines are the backbone; fill these before other categories
2. **Cross-reference**: When sources conflict, prefer: annual reports > financial filings > Crunchbase > press releases > estimates
3. **Be honest about gaps**: Mark "Unknown" with explanation rather than inventing data. Gaps are information -- well-funded companies publicize their growth
4. **Use proxy metrics when needed**: For private companies, employee count x EUR 150-250K = revenue estimate; flag as "Estimated (proxy)"
5. **Score rigorously**: Apply the rubric criteria, not impressions from marketing materials. A private company with no data should not automatically score low -- search harder first, then score conservatively
6. **Generate Mermaid charts**: Populate the Revenue Trend, Employee Growth, and Growth Scorecard bar chart templates with actual data from the research. Skip a chart only if fewer than 2 data points exist for that timeline
7. **Format and write**: Structure findings and write to `tickets/COMPETITION/[company-slug]/financial-growth.md` as a standalone file
8. **Update status**: Mark "Financial analysis complete" in README.md

---

## Usage

```text
@research-financial-growth Volue ASA @tickets/COMPETITION/volue/
@research-financial-growth Engrate @tickets/COMPETITION/engrate/
@research-financial-growth Brady Technologies @tickets/COMPETITION/brady-technologies-powerdesk/
```

> **Full prioritised competitor backlog (30+ companies in 4 tiers)**: See `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md`

---

## Related Prompts

- `analysis/market/research-competitor.prompt.md` - Broader 8-category deep analysis (complementary; this prompt goes deeper on financial dimensions)
- `analysis/market/generate-financial-dashboard.prompt.md` - Cross-competitor dashboard that consumes the Growth Scorecards produced by this prompt
- `analysis/market/research-protocols.prompt.md` - Protocol-based competitor discovery

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

---

**Created**: 2026-02-15
**Context**: tickets/COMPETITION/ competitive landscape financial analysis
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0

## Pattern Used

This prompt follows: `.cursor/templars/analysis/market/multi-dimensional-research-scorecard-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md`
