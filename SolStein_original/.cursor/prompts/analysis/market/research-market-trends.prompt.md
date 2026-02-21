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

**Pattern**: Guided Analysis Pattern ⭐⭐⭐⭐⭐  
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

```
@research-market-trends
```

**Time**: 60-90 minutes | **Scope**: All 5 categories | **Output**: Full `market-trends.md`

### Quick Refresh Mode

Targeted update of 1-2 categories after specific events (regulatory announcement, M&A news, conference):

```
@research-market-trends -- quick refresh Category 1 (Regulatory) after ACER Q1 2026 report
```

**Time**: 15-30 minutes | **Scope**: Specified categories only | **Output**: Updates relevant sections in existing `market-trends.md`, preserves unchanged categories

### Quarterly Review Mode

Re-score existing trends and add newly identified ones:

```
@research-market-trends -- quarterly review, re-score existing trends and add new
```

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

Score each trend on 4 dimensions. Full rubric tables with named thresholds and concrete examples are in the exemplar.

- **Impact Score** (1-5): 5=Transformative (forces strategic pivot), 4=High (requires major response), 3=Moderate (planned response), 2=Low (monitor), 1=Minimal (awareness only)
- **Timeline Horizon**: Near (<1yr, must be in roadmap), Medium (1-3yr, must be in strategic plan), Far (3+yr, monitor only)
- **Eneve Impact**: Positive (creates opportunity) / Neutral (market-wide, no disproportionate effect) / Negative (threatens position) -- always with explanation
- **Confidence**: Confirmed (official institutional source) / Estimated (credible secondary source) / Speculative (directional inference, flag prominently)

See `.cursor/exemplars/analysis/market/research-market-trends-exemplar.md` for the complete rubric tables with examples.

---

## Examples (Few-Shot)

One compact example showing expected trend table depth:

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| MARI platform full go-live across all EU balancing areas | 4 | Near (<1yr) | Negative: Requires automated mFRR bid submission via standardized API. Eneve's batch-based EDSN interface needs real-time API upgrade. | Confirmed | FD-015, FD-020 | ENTSO-E MARI implementation report, Jan 2026 |

For additional few-shot examples (category analysis paragraphs, dashboard feed mapping entries, and scoring edge cases), see `.cursor/exemplars/analysis/market/research-market-trends-exemplar.md`.

---

## Output Format

Structure output as a **standalone markdown file** saved to `tickets/COMPETITION/market-trends.md`:

```markdown
# Market Trends & Regulatory Landscape

**Research Date**: YYYY-MM-DD
**Research Mode**: Full / Quick Refresh / Quarterly Review
**Confidence Level**: High / Medium / Low (based on source quality and coverage)
**Data Sources**: [count] sources consulted

---

## Executive Summary

[3-5 sentences capturing the most critical trends and their combined implications for Eneve. This is the "meteor warning" distillation -- what keeps us up at night?]

---

## Regulatory Timeline

`` `mermaid
gantt
    title EU Energy Regulatory Milestones
    dateFormat YYYY-MM
    axisFormat %Y-%m

    section Balancing
    MARI Go-Live (full)           :milestone, m1, YYYY-MM, 0d
    PICASSO Go-Live (full)        :milestone, m2, YYYY-MM, 0d
    TERRE Go-Live                 :milestone, m3, YYYY-MM, 0d

    section Network Codes
    Network Code Harmonization    :active, nc1, YYYY-MM, YYYY-MM
    CIM/CGMES Adoption Deadline   :milestone, nc2, YYYY-MM, 0d

    section Market Design
    Clean Energy Package Impl     :active, cep1, YYYY-MM, YYYY-MM
    Flexibility Markets Framework :active, fm1, YYYY-MM, YYYY-MM

    section Compliance
    REMIT II Enforcement          :milestone, r1, YYYY-MM, 0d
    NIS2 Compliance Deadline      :milestone, n1, YYYY-MM, 0d
`` `

---

## 1. EU Regulatory Changes

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| [Trend name] | [score] | Near/Medium/Far | Positive/Neutral/Negative: [explanation] | Confirmed/Estimated/Speculative | FD-015/019/020 | [source] |

### Analysis

[2-3 paragraphs analyzing the regulatory landscape, key deadlines, and combined implications for energy software vendors. Specific Eneve implications highlighted.]

---

## 2. Protocol Convergence

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| [Trend name] | [score] | Near/Medium/Far | Positive/Neutral/Negative: [explanation] | Confirmed/Estimated/Speculative | FD-015/019/020 | [source] |

### Analysis

[2-3 paragraphs on protocol convergence trajectory and Eneve EDSN moat erosion timeline.]

---

## 3. Technology Shifts

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| [Trend name] | [score] | Near/Medium/Far | Positive/Neutral/Negative: [explanation] | Confirmed/Estimated/Speculative | FD-015/019/020 | [source] |

### Analysis

[2-3 paragraphs on technology adoption curves and implications for Eneve's migration strategy.]

---

## 4. Market Structure Changes

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| [Trend name] | [score] | Near/Medium/Far | Positive/Neutral/Negative: [explanation] | Confirmed/Estimated/Speculative | FD-015/019/020 | [source] |

### Analysis

[2-3 paragraphs on consolidation patterns, investment trends, and new entrant dynamics.]

---

## 5. Customer Behavior Shifts

| Trend | Impact (1-5) | Timeline | Eneve Impact | Confidence | Dashboard Feed | Source |
|---|---|---|---|---|---|---|
| [Trend name] | [score] | Near/Medium/Far | Positive/Neutral/Negative: [explanation] | Confirmed/Estimated/Speculative | FD-015/019/020 | [source] |

### Analysis

[2-3 paragraphs on how buyer preferences are shifting and what this means for Eneve's go-to-market.]

---

## Dashboard Feed Mapping

### FD-015: Threat Convergence Timeline

Trends feeding this sheet (convergence of multiple forces creating compounding threat):

| Trend | Category | Impact | Timeline | Convergence With |
|---|---|---|---|---|
| [Trend] | [Cat #] | [1-5] | [Near/Med/Far] | [Other trends it amplifies] |

### FD-019: Scenario Projections

Trends feeding this sheet (branching outcomes requiring scenario analysis):

| Trend | Category | Optimistic Scenario | Pessimistic Scenario |
|---|---|---|---|
| [Trend] | [Cat #] | [What if trend is slow/delayed?] | [What if trend accelerates?] |

### FD-020: Portfolio Risk Dashboard

Trends feeding this sheet (direct risk to Eneve's product portfolio):

| Trend | Category | Risk Type | Affected Products/Modules | Mitigation |
|---|---|---|---|---|
| [Trend] | [Cat #] | [Obsolescence/Competition/Regulatory] | [Which Eneve modules?] | [Possible response] |

---

## Quality Assessment

- Data completeness: [X/5 categories with substantive data]
- Source quality: [primary/secondary/mixed]
- Key data gaps: [what couldn't be found and why]
- Recommended follow-up: [specific research that would fill gaps]
```

---

## Search Query Templates

Use current year. Replace `[YEAR]` with 2026, `[YEAR-1]` with 2025.

| Category | Query Templates |
|---|---|
| Regulatory | `ACER electricity balancing guideline [YEAR]`, `ENTSO-E MARI PICASSO go-live`, `Clean Energy Package implementation status [YEAR]` |
| Protocol | `ENTSO-E CIM CGMES adoption`, `EDSN protocol roadmap`, `ebIX CIM convergence energy` |
| Technology | `AI energy trading adoption [YEAR]`, `cloud migration energy utilities Europe`, `energy software API-first architecture` |
| Market Structure | `energy software M&A Europe [YEAR]`, `energy tech venture capital investment [YEAR]`, `energy software startup funding` |
| Customer Behavior | `utility SaaS adoption Europe`, `energy software buyer preferences [YEAR]`, `multi-market energy platform demand` |

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

## Reasoning Process (for AI Agent)

When this prompt is invoked, the AI should:

1. **Read Eneve positioning**: Load `tickets/COMPETITION/README.md` to understand Eneve's vulnerabilities
2. **Scan existing competitor data**: Skim competitor files for context on what competitors are doing (feeds Category 4 and 5)
3. **Determine mode**: Full Research / Quick Refresh / Quarterly Review -- scope research effort accordingly
4. **Plan search strategy**: For each in-scope category, formulate 2-3 web search queries per research question
5. **Execute searches systematically**: Work through categories in order, recording findings with sources
6. **Score each trend**: Apply the Impact (1-5), Timeline (Near/Medium/Far), and Confidence (Confirmed/Estimated/Speculative) rubric consistently
7. **Assess Eneve impact**: For each trend, evaluate through the NL-focused / EDSN-dependent / on-premise / single-market lens
8. **Build regulatory timeline**: Extract concrete dates for the Mermaid gantt chart from regulatory sources
9. **Map to dashboard feeds**: Classify each trend into FD-015, FD-019, and/or FD-020 based on its nature
10. **Write executive summary**: Distill the 3-5 most dangerous trends into a punchy strategic warning
11. **Self-review before finalizing**: Before writing the output file, verify:
    - Every trend has all 6 columns filled (Impact, Timeline, Eneve Impact, Confidence, Dashboard Feed, Source)
    - No category has fewer than 3 trends (unless documented why)
    - Confidence levels are realistic (not everything is "Confirmed")
    - Analysis paragraphs provide synthesis beyond table repetition
    - Executive summary captures genuinely critical threats, not just a list
12. **Format and write**: Structure findings in the output template and save to `tickets/COMPETITION/market-trends.md`

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

---

## Downstream Prompt Chaining

After this prompt completes, the following prompts consume its output:

| Next Prompt | What It Uses | When to Run |
|---|---|---|
| `analysis/market/generate-financial-dashboard.prompt.md` | All 5 category tables + dashboard feed mapping | After market-trends.md is complete |
| `analysis/market/research-competitor.prompt.md` | Market structure trends (Category 4) as context for individual competitor deep-dives | When refreshing specific competitor files |
| `analysis/market/research-customer-intelligence.prompt.md` | Customer behavior trends (Category 5) as context for buyer intelligence | When analyzing customer segments |

---

## Usage

**Full Research** (initial build or annual refresh):

```
@research-market-trends
```

**Quick Refresh** (after specific event):

```
@research-market-trends -- quick refresh Category 1 after ACER Q1 2026 report
```

**Quarterly Review** (re-score and update):

```
@research-market-trends -- quarterly review
```

---

## Related Prompts

- `analysis/market/research-competitor.prompt.md` - Individual competitor deep-dive (companion prompt)
- `analysis/market/research-customer-intelligence.prompt.md` - Customer intelligence per competitor
- `analysis/market/research-protocols.prompt.md` - Deep protocol analysis (overlaps with Category 2)
- `analysis/market/research-financial-growth.prompt.md` - Financial metrics per competitor (feeds Category 4)
- `analysis/market/generate-financial-dashboard.prompt.md` - Dashboard generation from all research data

---

## Related Rules

- `.cursor/rules/prompts/prompt-creation-rule.mdc` - Prompt creation standards
- `.cursor/rules/prompts/prompt-registry-integration-rule.mdc` - Registry format requirements

## Pattern Used

This prompt follows: `.cursor/templars/analysis/market/landscape-trend-scanning-templar.md`

## Reference Example

See exemplar: `.cursor/exemplars/analysis/market/research-market-trends-exemplar.md`

---

**Created**: 2026-02-17  
**Improved**: 2026-02-17 (improve-prompt + enhance-prompt applied)  
**Extracted**: 2026-02-17 (templar + exemplar extracted via extract-templar-exemplar)  
**Context**: tickets/FINANCIALDASHBOARD/FD-028-market-trends-prompt  
**Follows**: `.cursor/rules/prompts/prompt-creation-rule.mdc` v1.0.0  
**Fills Gap**: No existing prompt captures market-wide forces; all prior prompts focus on individual competitors
