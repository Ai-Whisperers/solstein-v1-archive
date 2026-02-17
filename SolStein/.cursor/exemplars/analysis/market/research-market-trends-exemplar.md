---
type: exemplar
artifact-type: prompt
demonstrates: landscape-trend-scanning-with-impact-scoring, multi-mode-research, downstream-feed-mapping, regulatory-timeline-visualization
domain: analysis/market
quality-score: exceptional
version: 1.0.0
extracted-from: .cursor/prompts/analysis/market/research-market-trends.prompt.md
illustrates: analysis.landscape-trend-scanning
use: critic-only
notes: "Pattern extraction only. NEVER copy domain-specific content (EU energy regulation, EDSN, Eneve) to other prompts. Extract the structural patterns, scoring approach, and downstream mapping technique."
---

# Research Market Trends Exemplar

## Artifact Type

**Type**: Prompt (`.prompt.md`)

## Why This is Exemplary

This prompt demonstrates exceptional quality across multiple dimensions that go beyond what existing per-entity research templars offer. It introduces architectural innovations worth studying and replicating.

## Key Quality Elements

1. **Multi-Mode Research Design**: Three usage modes (Full Research / Quick Refresh / Quarterly Review) allow the same prompt to serve different research depths and time budgets. Each mode specifies scope, time estimate, and output behavior. This prevents prompt duplication for different use cases.

2. **Multi-Dimensional Trend Scoring with Named Rubric**: Every trend gets 6 scored columns (Impact 1-5, Timeline, Subject Impact, Confidence, Dashboard Feed, Source). The Impact Score rubric has named thresholds with concrete examples (not vague adjectives), making scoring reproducible across research sessions.

3. **Subject-Specific Impact Lens**: Every research category includes a "Subject-Specific Focus" callout that anchors abstract trends in concrete business impact. This prevents research from becoming disconnected academic exercises.

4. **Downstream Feed Mapping**: Each trend is explicitly mapped to the downstream dashboard artifacts that consume it (FD-015 Threat Timeline, FD-019 Scenarios, FD-020 Portfolio Risk). This architectural connection ensures research flows into decision-making.

5. **Regulatory Timeline via Mermaid Gantt**: The output format includes a Mermaid gantt chart template for plotting regulatory milestones chronologically -- a visual synthesis pattern that makes complex timelines scannable.

6. **3-Tier Quality Criteria**: Quality criteria are split into Critical (must pass), Important (should pass), and Nice-to-have -- preventing perfectionism while ensuring minimum quality bar. Most prompts use flat checklists.

7. **Concrete Few-Shot Examples**: The examples section shows exact table row format, full analysis paragraph depth, and dashboard feed mapping entries -- not just abstract descriptions of what "good" looks like.

8. **Downstream Prompt Chaining Table**: Explicitly documents which prompts consume this prompt's output, when to run them, and what data they use. This enables workflow orchestration across prompt families.

9. **12-Step Reasoning Process with Self-Review**: The reasoning process includes a self-review checkpoint (step 11) that verifies completeness, scoring consistency, and analysis depth before writing output.

10. **Time-Allocation Table per Category**: Process step 2 includes estimated time and complexity per research category, helping the agent allocate effort proportionally.

## Patterns Demonstrated

### Pattern 1: Multi-Mode Research Prompt

The three usage modes show how a single prompt can serve:
- **Initial build** (comprehensive, 60-90 min)
- **Event-triggered refresh** (targeted, 15-30 min)  
- **Periodic review** (re-scoring, 30-45 min)

This prevents creating three separate prompts for the same research domain.

### Pattern 2: Trend Scoring with Named Thresholds

The Impact Scoring Rubric (1-5) uses named levels with measurable thresholds:

| Score | Name | Example Threshold |
|---|---|---|
| 5 | Transformative | Fundamentally changes competitive landscape; forces strategic pivot |
| 4 | High Impact | Significant competitive advantage/disadvantage; requires major response |
| 3 | Moderate | Noticeable effect; requires planned response |
| 2 | Low Impact | Minor effect; monitor but no immediate action |
| 1 | Minimal | Background noise; awareness only |

Each level has a concrete example from the domain, making scoring reproducible.

### Pattern 3: Downstream Feed Mapping

Each trend maps to specific downstream artifacts with rationale:

| Downstream | Selection Criteria |
|---|---|
| Threat Timeline | Trends with convergence implications (multiple forces combining) |
| Scenario Projections | Trends with branching outcomes (optimistic/pessimistic) |
| Portfolio Risk | Trends creating direct risk to product portfolio |

This pattern transforms research from standalone documents into pipeline inputs.

### Pattern 4: Research Category with Subject-Specific Focus

Each research category ends with a "Subject-Specific Focus" callout:

> **Eneve-Specific Focus**: Which regulations require platform changes that Eneve's current MSSQL/on-premise architecture cannot support without migration?

This anchors abstract domain research in the subject's concrete reality.

### Pattern 5: Category-Level Time and Complexity Guidance

The process step includes a time allocation table:

| Category | Est. Time | Complexity |
|---|---|---|
| EU Regulatory Changes | 20-25 min | Highest -- EU institutional complexity |
| Protocol Convergence | 10-15 min | Medium -- niche topic |

This calibrates agent effort and sets expectations for varying category depths.

## Full Exemplar Content

The complete prompt is preserved below for reference. Study the structural patterns, scoring approach, and downstream mapping technique -- do not copy the domain-specific content.

---

```markdown
---
name: research-market-trends
description: "Please research macro-level market trends, regulatory changes, and technology shifts in European energy software that shape competitive dynamics"
category: analysis
tags: competition, market-trends, regulatory, technology, energy, strategy, europe, trends
argument-hint: "No arguments needed -- researches all 5 trend categories and produces tickets/COMPETITION/market-trends.md"
agent: cursor-agent
model: GPT-4
tools:
  - web/*
  - search/codebase
  - fileSystem
rules:
  - .cursor/rules/prompts/prompt-creation-rule.mdc
---

# Research Market Trends & Regulatory Landscape

Please perform a structured research session on macro-level market trends, regulatory changes, and technology shifts in European energy software. This prompt captures the market-wide forces that shape competitive dynamics -- forces that no single competitor prompt can cover. Output is a standalone `tickets/COMPETITION/market-trends.md` file with scored trends, Mermaid regulatory timeline, and dashboard feed mapping.

**Pattern**: Guided Analysis Pattern
**Effectiveness**: Converts ad-hoc market knowledge into structured, scored, and actionable strategic intelligence
**Use When**: Building or refreshing the competitive landscape dashboard, especially for threat timelines, scenario projections, and portfolio risk assessment

---

## Purpose

Current competitive research prompts focus on individual competitors. No prompt captures the market-wide forces that shape competitive dynamics:

- **EU regulatory changes** driving mandatory platform upgrades and new market designs
- **Protocol convergence** eroding national moats (directly threatens Eneve's NL-only EDSN position)
- **Technology shifts** changing what buyers expect from energy software
- **Market structure changes** reshaping who competes and how
- **Customer behavior shifts** altering purchasing patterns and vendor selection criteria

This data feeds directly into:
- [FD-015](../../tickets/FINANCIALDASHBOARD/FD-015-threat-timeline/plan.md) Threat Convergence Timeline
- [FD-019](../../tickets/FINANCIALDASHBOARD/FD-019-scenario-projections/plan.md) Scenario Projections
- [FD-020](../../tickets/FINANCIALDASHBOARD/FD-020-portfolio-risk/plan.md) Portfolio Risk Dashboard

---

## Required Context

- **Eneve Context**: Reference `@tickets/COMPETITION/README.md` for Eneve's positioning summary (NL-focused, EDSN protocol specialist, on-premise MSSQL, migrating to C#/.NET)
- **Existing Competitor Data**: Reference competitor files in `tickets/COMPETITION/*/` for context on who is moving where
- **Dashboard Spec**: Reference `@tickets/COMPETITION/financial-dashboard.md` for how trends feed into the dashboard narrative

---

## Usage Modes

### Full Research Mode (Default)

Complete 5-category research session for initial build or annual refresh:

@research-market-trends

**Time**: 60-90 minutes | **Scope**: All 5 categories | **Output**: Full `market-trends.md`

### Quick Refresh Mode

Targeted update of 1-2 categories after specific events (regulatory announcement, M&A news, conference):

@research-market-trends -- quick refresh Category 1 (Regulatory) after ACER Q1 2026 report

**Time**: 15-30 minutes | **Scope**: Specified categories only | **Output**: Updates relevant sections in existing `market-trends.md`, preserves unchanged categories

### Quarterly Review Mode

Re-score existing trends and add newly identified ones:

@research-market-trends -- quarterly review, re-score existing trends and add new

**Time**: 30-45 minutes | **Scope**: All 5 categories, focus on changes since last research date | **Output**: Updated `market-trends.md` with change annotations

---

## Process

### Step 1: Read Eneve Positioning

Read `tickets/COMPETITION/README.md` to understand Eneve's current capabilities, market position, and strategic vulnerabilities. Every trend must be assessed through the lens of "what does this mean for Eneve specifically?"

### Step 2: Web Research by Category

For each of the 5 research categories below, perform targeted web searches. Time allocation guidance:

| Category | Est. Time | Complexity |
|---|---|---|
| 1. EU Regulatory Changes | 20-25 min | Highest -- EU institutional complexity, multiple sources |
| 2. Protocol Convergence | 10-15 min | Medium -- niche topic, fewer sources |
| 3. Technology Shifts | 10-15 min | Medium -- broad but well-documented |
| 4. Market Structure Changes | 10-15 min | Medium -- M&A data scattered across sources |
| 5. Customer Behavior Shifts | 10-15 min | Lower -- fewer primary sources, more inference |

Prioritize these source types:
- EU institutional sources (ACER, ENTSO-E, European Commission DG Energy)
- Industry publications (Energy Risk, Montel, ICIS, S&P Global Commodity Insights, Platts)
- Regulatory body publications (ACM for NL, CREG for BE, BNetzA for DE)
- Technology analyst reports (Gartner, IDC, Chartis Energy50)
- Conference content (E-world, Enlit Europe, European Utility Week)
- Investment and M&A databases (Crunchbase, PitchBook, Mergermarket)
- Industry association publications (Eurelectric, EFET, VGB PowerTech)

### Step 3: Score Each Trend

For every trend identified, assign:
- **Impact Score** (1-5): How significantly this trend affects European energy software competitive dynamics
- **Timeline Horizon**: Near (<1yr), Medium (1-3yr), Far (3+yr)
- **Eneve Impact**: Specific assessment of how this trend affects Eneve's competitive position (Positive / Neutral / Negative + explanation)
- **Confidence**: How reliable the underlying evidence is (Confirmed / Estimated / Speculative)

### Step 4: Build Regulatory Timeline

Create a Mermaid gantt chart plotting key regulatory milestones chronologically. Include implementation deadlines, go-live dates, and consultation periods for major EU energy regulations.

### Step 5: Map to Dashboard Feeds

For each trend, identify which downstream dashboard sheet(s) it feeds:
- **FD-015 Threat Timeline**: Trends with convergence implications (multiple forces combining)
- **FD-019 Scenario Projections**: Trends with branching outcomes (optimistic/pessimistic scenarios)
- **FD-020 Portfolio Risk**: Trends creating direct risk to Eneve's product portfolio

### Step 6: Write Market Trends File

Write output to `tickets/COMPETITION/market-trends.md` as a standalone file. If the file already exists, replace it with the updated version.

---

## Research Categories

### Category 1: EU Regulatory Changes

Track regulatory developments that force energy software platform changes or create new market opportunities.

| Research Question | Search Strategy |
|---|---|
| Clean Energy Package implementation status | ACER reports, European Commission DG Energy, national regulator updates |
| Electricity Balancing Guideline (EB GL) impact | ENTSO-E implementation reports, balancing platform go-live dates |
| MARI / PICASSO / TERRE platform status | ENTSO-E balancing platforms pages, national TSO announcements |
| Network code harmonization progress | ACER network code publications, ENTSO-E code development |
| REMIT II enforcement timeline | ACER REMIT pages, compliance vendor announcements |
| Capacity mechanism market design changes | National regulator consultations, DG Competition decisions |
| Renewable energy directive targets (RED III) | European Commission publications, national transposition plans |
| Flexibility market regulation | National sandbox programs, ENTSO-E flexibility studies |

**Eneve-Specific Focus**: Which regulations require platform changes that Eneve's current MSSQL/on-premise architecture cannot support without migration?

### Category 2: Protocol Convergence

Track standardization efforts that erode national protocol moats -- directly threatening Eneve's EDSN specialization.

| Research Question | Search Strategy |
|---|---|
| ENTSO-E CIM/CGMES adoption across countries | ENTSO-E data exchange working groups, TSO implementation reports |
| National protocol sunset timelines | NL: EDSN/TenneT roadmaps; DE: BDEW; BE: Elia announcements |
| Cross-border data exchange harmonization | ENTSO-E transparency platform, JAO allocation office updates |
| MNA (Market Network Adapter) standardization | National TSO/DSO announcements, market coupling updates |
| ebIX / Edig@s convergence with CIM | ebIX working group publications, gas/power protocol convergence |
| API-first vs message-based protocol evolution | TSO/DSO digital strategy publications, industry API initiatives |

**Eneve-Specific Focus**: If EDSN converges with ENTSO-E CIM, Eneve's core differentiator (deep EDSN knowledge) erodes. Timeline and probability assessment required.

### Category 3: Technology Shifts

Track technology adoption patterns that change what buyers expect from energy software vendors.

| Research Question | Search Strategy |
|---|---|
| AI/ML adoption in energy trading and scheduling | Gartner energy reports, vendor announcements, conference talks |
| Cloud migration patterns in energy utilities | IDC utility cloud reports, vendor cloud-first announcements |
| API-first architecture adoption rates | Developer ecosystem reports, energy API marketplace growth |
| Real-time data processing requirements | IoT/smart grid data volume projections, TSO data frequency changes |
| Low-code/no-code platforms in energy | Analyst reports, vendor product launches, utility CIO surveys |
| Cybersecurity requirements for energy platforms | NIS2 directive impact, ENISA guidelines, vendor compliance |

**Eneve-Specific Focus**: Which technology shifts make Eneve's current on-premise MSSQL architecture increasingly uncompetitive? Where does the C#/.NET migration create opportunity to leapfrog?

### Category 4: Market Structure Changes

Track consolidation, investment, and new-entrant patterns that reshape who competes in European energy software.

| Research Question | Search Strategy |
|---|---|
| M&A activity in energy software (last 2yr) | Crunchbase, PitchBook, Mergermarket, press releases |
| PE/VC investment trends in energy tech | Crunchbase sector reports, energy-focused VC fund announcements |
| New entrants with AI-first positioning | Startup databases, accelerator programs (EIT InnoEnergy, Plug and Play) |
| Platform consolidation patterns | Multi-vendor to single-platform migrations, vendor announcements |
| Big tech entry signals (Microsoft, Google, AWS) | Cloud provider energy vertical pages, partnership announcements |
| Geographic expansion patterns of competitors | Press releases, job postings by location, new office announcements |

**Eneve-Specific Focus**: Is the market consolidating around large platforms that Eneve cannot compete with? Are AI-first startups creating a "born-in-the-cloud" threat?

### Category 5: Customer Behavior Shifts

Track how energy company buying patterns and vendor selection criteria are changing.

| Research Question | Search Strategy |
|---|---|
| SaaS preference vs on-premise in utilities | Gartner/IDC utility surveys, vendor licensing model changes |
| Multi-market solution demand (vs single-market) | RFP trend analysis, vendor multi-country announcements |
| AI-enabled tooling as selection criterion | RFP requirements analysis, conference buyer panels |
| Total cost of ownership sensitivity | Industry benchmark studies, procurement trend reports |
| Implementation speed expectations | Vendor go-to-market messaging, agile deployment case studies |
| Vendor lock-in concerns and open-source preference | Open-source energy projects (OSGP, OpenADR), buyer surveys |

**Eneve-Specific Focus**: Are buyers moving to SaaS and multi-market platforms faster than Eneve can migrate? Is "deep single-market knowledge" still valued, or is "broad multi-market coverage" winning?

---

## Impact Scoring Rubric

### Impact Score (1-5)

| Score | Definition | Example |
|---|---|---|
| **5 - Transformative** | Fundamentally changes competitive landscape; forces strategic pivot | EDSN protocol sunset announcement |
| **4 - High Impact** | Significant competitive advantage/disadvantage; requires major response | EU-wide mandatory cloud security certification for energy platforms |
| **3 - Moderate** | Noticeable effect on competitive positioning; requires planned response | New entrant raises >EUR50M for energy AI platform |
| **2 - Low Impact** | Minor effect; monitor but no immediate action needed | Incremental protocol version update |
| **1 - Minimal** | Background noise; awareness only | Minor regulatory consultation on edge-case scenario |

### Timeline Horizon

| Horizon | Definition | Planning Implication |
|---|---|---|
| **Near (<1yr)** | Already happening or imminent | Must be in current roadmap |
| **Medium (1-3yr)** | Confirmed direction, implementation in progress | Must be in strategic plan |
| **Far (3+yr)** | Directional signals, not yet committed | Monitor and prepare, don't commit resources yet |

### Eneve Impact Assessment

| Rating | Definition |
|---|---|
| **Positive** | Trend creates opportunity for Eneve (e.g., regulation requiring deep NL market knowledge) |
| **Neutral** | Trend affects market broadly; no disproportionate impact on Eneve |
| **Negative** | Trend threatens Eneve's position (e.g., protocol standardization eroding EDSN moat) |

### Confidence Level

| Level | Criteria | Usage |
|---|---|---|
| **Confirmed** | Official institutional source: EU regulation text, ACER decision, ENTSO-E publication, national regulator ruling | Use for hard dates, enacted regulations, official announcements |
| **Estimated** | Credible secondary source: industry analyst report, conference presentation, expert commentary, trade publication | Use for projected timelines, adoption rates, market sizing |
| **Speculative** | Forward-looking inference based on directional signals. Must be explicitly labeled. | Use sparingly; flag prominently in trend tables |

---

## Examples (Few-Shot)

### Example: Completed Trend Table Entry (Category 1)

This shows the expected depth and format for a single trend row:

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| MARI platform full go-live across all EU balancing areas | 4 | Near (<1yr) | Negative: Requires automated mFRR bid submission via standardized API. Eneve's current batch-based EDSN interface needs upgrade to real-time API integration. | Confirmed | FD-015, FD-020 | ENTSO-E MARI implementation report, Jan 2026 |
| NIS2 directive cybersecurity compliance for energy platforms | 3 | Medium (1-3yr) | Negative: On-premise MSSQL deployments face stricter audit requirements. Cloud-native competitors can leverage provider certifications. Eneve must invest in security hardening. | Confirmed | FD-020 | EU Directive 2022/2555, national transposition tracker |
| Flexibility market sandbox programs (NL, DE) | 3 | Medium (1-3yr) | Positive: New market segment requiring deep knowledge of local market rules -- plays to Eneve's NL specialization strength. | Estimated | FD-019 | ACM flexibility market consultation Q4 2025, BNetzA pilot program announcement |

### Example: Category Analysis Section

This shows the expected depth for a category analysis paragraph:

> **Category 1 Analysis (example)**:
>
> The EU regulatory landscape is converging on three simultaneous pressures for energy software vendors: (1) the final phase of balancing platform integration (MARI/PICASSO/TERRE) requiring real-time API connectivity by mid-2026, (2) REMIT II enforcement creating new transaction reporting obligations that demand database schema changes, and (3) NIS2 cybersecurity compliance raising the bar for on-premise deployments.
>
> For Eneve specifically, the balancing platform integration timeline is the most urgent. The current batch-oriented EDSN message interface is insufficient for the sub-second response times MARI requires. This creates a forcing function for the C#/.NET migration -- the new architecture must support real-time API integration from day one. The silver lining: competitors who haven't invested in NL-specific balancing market knowledge (like generic multi-market platforms) will struggle with the Dutch-specific activation rules that still apply alongside the EU harmonized processes.

### Example: Dashboard Feed Mapping Entry

| Trend | Category | Impact | Timeline | Convergence With |
|---|---|---|---|---|
| MARI go-live + NIS2 compliance + cloud migration pressure | Cat 1 + Cat 3 | 4 | Near-Medium | Three forces combine: regulatory deadline forces API upgrade, security requirements favor cloud, cloud migration enables API-first -- creating a "migrate now or fall behind" pressure point for on-premise vendors like Eneve |

---

## Downstream Prompt Chaining

After this prompt completes, the following prompts consume its output:

| Next Prompt | What It Uses | When to Run |
|---|---|---|
| `analysis/market/generate-financial-dashboard.prompt.md` | All 5 category tables + dashboard feed mapping | After market-trends.md is complete |
| `analysis/market/research-competitor.prompt.md` | Market structure trends (Category 4) as context for individual competitor deep-dives | When refreshing specific competitor files |
| `analysis/market/research-customer-intelligence.prompt.md` | Customer behavior trends (Category 5) as context for buyer intelligence | When analyzing customer segments |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| EU regulatory sources behind paywalls | Try ACER public consultations, ENTSO-E public reports, EUR-Lex for regulation text. Many DG Energy publications are free. |
| Trend impact hard to score | Use the rubric strictly. If uncertain between two scores, prefer the higher (conservative assessment of risk). |
| No clear Eneve impact for a trend | Assess whether the trend affects NL-specific, EDSN-dependent, on-premise, or single-market vendors disproportionately. If none apply, mark Neutral. |
| Regulatory timeline dates uncertain | Use the latest official publication date. Mark uncertain dates with "~" prefix (e.g., ~2027-Q1). |
| Category yields fewer than 3 trends | Broaden search terms. If still sparse, document as-is with a note on data limitations. |
| Quick Refresh mode: unclear what changed | Compare research date in existing file header. Focus web searches on news/publications after that date. |

---

## Quality Criteria

### Critical (must pass)

- [ ] All 5 research categories addressed with trend tables (no categories skipped)
- [ ] Each category has 3-5 identified trends minimum
- [ ] Every trend has Impact (1-5), Timeline, Eneve Impact, Confidence, Dashboard Feed, and Source
- [ ] Every trend has source attribution (no unsourced claims)
- [ ] Mermaid regulatory timeline included with real milestone dates
- [ ] Output saved to `tickets/COMPETITION/market-trends.md`

### Important (should pass)

- [ ] Dashboard feed mapping completed for FD-015, FD-019, and FD-020
- [ ] Executive summary captures the 3-5 most critical trends
- [ ] Eneve-specific analysis present in each category
- [ ] Analysis sections provide synthesis, not just table repetition
- [ ] Confidence levels appropriately distributed (not all Confirmed or all Speculative)

### Nice-to-have

- [ ] Research date and source count in file header
- [ ] Per-category data gap notes where sources were limited
- [ ] Convergence patterns identified across categories in FD-015 mapping
```

## Learning Points

- **Multi-mode prompts prevent duplication**: Instead of creating separate Full/Refresh/Review prompts, design a single prompt with mode switches. This keeps the research categories, scoring rubric, and output format in sync.
- **Downstream feed mapping is an architectural connector**: Explicitly mapping each research finding to its consuming artifact transforms research from standalone analysis into a data pipeline. Apply this whenever research feeds dashboards or decision tools.
- **Subject-specific focus callouts ground abstract research**: Generic landscape scanning risks producing disconnected insights. Adding a "what does this mean for US" callout per category forces practical relevance.
- **3-tier quality criteria prevent perfectionism**: Splitting quality into Critical/Important/Nice-to-have gives the agent a minimum quality bar while allowing time-pressured sessions to still produce useful output.
- **Time allocation per category calibrates agent effort**: Not all categories are equal. Providing time/complexity guidance prevents the agent from spending 80% of effort on the first category and rushing the rest.
- **Scoring rubrics with concrete examples ensure reproducibility**: Named thresholds with domain examples (not vague adjectives like "significant") make scoring consistent across different research sessions and agents.

## When to Reference

Use this exemplar when:
- Creating a new landscape-level research prompt for any domain
- Designing a multi-mode research prompt (full/refresh/review)
- Adding downstream feed mapping to research prompts
- Building scoring rubrics with named thresholds for trend assessment
- Structuring research categories with subject-specific focus callouts
- Designing 3-tier quality criteria for research prompts

## Related Exemplars

- `.cursor/exemplars/analysis/market/research-competitor-exemplar.md` -- Per-entity research pattern (contrast with this landscape-level pattern)
- `.cursor/exemplars/analysis/market/financial-growth-research-exemplar.md` -- Per-entity scoring pattern (contrast with this trend-scoring pattern)
- `.cursor/exemplars/analysis/market/financial-dashboard-exemplar.md` -- Downstream synthesis dashboard (consumes output from prompts like this)

---

**Extracted From**: `.cursor/prompts/analysis/market/research-market-trends.prompt.md`
**Created**: 2026-02-17
