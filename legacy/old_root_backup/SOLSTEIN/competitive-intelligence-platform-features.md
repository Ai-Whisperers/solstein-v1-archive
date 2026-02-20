# Eneve Competitive Intelligence Platform -- Feature Overview

---

## What It Is

An AI-powered competitive intelligence platform that tracks 33+ European energy software competitors across financial, strategic, and market dimensions. Currently delivered as an automated Excel workbook + markdown dashboard generated from structured research data. Built to give a CTO or Board instant clarity on where Eneve stands and where threats are coming from.

---

## V1 Features

- **7-sheet Excel workbook** with Summary, Revenue Leaderboard, Funding Leaderboard, Employee Growth, SaaS Maturity, Classification Matrix, and Raw Data
- Revenue CAGR bar chart
- Competitor classification: Rocket / Riser / Steady / Dinosaur (based on composite 6-dimension scoring)
- Hyperlinks from every competitor row to source research files
- Basic color-coding (green = Rocket, red = Dinosaur, yellow = Eneve)
- Data extracted from 25+ competitor markdown research files via Python pipeline

---

## What's New Since V1

### Board-Ready Presentation Quality (Phase 1 -- Complete)

- **Executive Summary Sheet** -- KPI tiles (total competitors, Rockets count, CAGR comparison, composite scores), Top 5 Competitive Threats table, dynamic insight callouts. Opens as first sheet.
- **Charts on Every Sheet** -- Bar charts for Employee Growth, Funding, Summary, SaaS Maturity; doughnut chart for Classification Matrix. 6+ native Excel charts total.
- **Eneve vs Market Sheet** -- Side-by-side comparison of Eneve metrics against market averages, medians, and best-in-class. Conditional green/red coloring showing where Eneve leads or trails. Grouped bar chart.
- **Efficiency & Profitability Sheet** -- Revenue per employee, EBITDA margin, capital efficiency ratios.
- **Market Reach Sheet** -- International revenue %, countries active, geographic expansion signals.
- **Professional Styling** -- Dark navy/gold color palette, alternating row shading, merged-cell headers, trend indicators, print-ready layout with confidentiality footer.
- **Sparklines** -- Mini inline trend charts showing revenue and employee growth trajectories per competitor.
- **Methodology Sheet** -- Full documentation of data sources, confidence levels, scoring methodology, classification thresholds, currency conversion, and caveats.

### Engineering Quality (Phase 2 -- Complete)

- **84% automated test coverage** -- 157 pytest unit tests across all 4 Python modules.
- **Smart caching** -- MD5-based change detection; only re-extracts competitors whose source data changed. Sub-second re-runs.
- **Performance profiled** -- Full pipeline runs in ~0.56s for 33 competitors. Bottleneck analysis documented.
- **Progress bars** -- Rich terminal UI during extraction and generation.

### PE-Firm-Ready Intelligence Sheets (Phase 3 -- In Progress)

- **AI Maturity Matrix** -- Every competitor scored 1-10 on AI adoption across 6 dimensions. Heatmap formatting.
- **Investment Efficiency Ratios** -- Revenue per employee, capital efficiency, hiring efficiency. Quartile markers.
- **M&A Vulnerability Map** -- Classifies each competitor as Acquirer, Target, Neutral, or Self-Sustaining. 9 Acquirers, 1 Target, 17 Neutral, 2 Self-Sustaining identified.
- **Threat Convergence Timeline** -- Gantt-style 2024-2029 timeline showing when competitive threats arrive or intensify. Color-coded by proximity.
- **Competitive Overlap Heatmap** -- 33x33 pairwise overlap matrix. Scores overlap across product, geography, segment, customer base, and technology.
- **Confidence Dashboard** -- Research quality score per competitor. Traffic-light rating (High/Medium/Low). Portfolio-level confidence: 46.2%.
- **Scenario Projections** -- 3-year forward extrapolation of revenue and headcount at current CAGR rates. Threshold highlighting for competitors crossing key milestones.
- **Portfolio Risk Dashboard** -- Aggregate risk matrix with probability x severity scoring, bubble chart visualization, top-5 risk summary.
- **Data Explorer** -- Interactive Excel Table with autofilter dropdowns for ad-hoc exploration across all data dimensions.
- **Geographic Expansion Tracker** -- Country-vs-competitor matrix (14+ European markets). *(Planned)*
- **Geographic Map Visualization** -- Embedded European map with HQ/subsidiary/market markers. *(Planned)*

### Research Automation Pipeline (Phase 4 -- In Progress)

- **10 structured research prompts** -- Each produces consistent, source-attributed, confidence-scored output across: competitor deep-dive, financial growth, corporate history, customer intelligence, AI talent mapping, competitive overlap, data confidence, market trends, protocol mapping, and financial dashboard synthesis.
- **Templars and exemplars library** -- 7 reusable prompt structure templates + 10 "exceptional" quality reference implementations ensuring every research output follows proven patterns.
- **AI-powered research pipeline** -- Prompts drive systematic web research with scoring rubrics, few-shot examples, self-correction loops, and search query templates. Turns a 60-minute manual research task into a 15-minute guided session.

---

## What's Coming Next (Roadmap)

### Web-Based Dashboard

- Browser-based interactive dashboard replacing the Excel workbook
- Real-time filtering, sorting, and drill-down across all intelligence dimensions
- Responsive design for board presentations on any device
- Role-based access (CTO view, Board view, Analyst view)

### Database Backing

- Structured database replacing JSON/markdown as the data layer
- Full audit trail of every data point change with timestamp and source
- Queryable API for downstream integrations (financial modeling, board decks, investor materials)
- Historical trend storage enabling true time-series competitive tracking

### Perplexity AI Integration

- Perplexity AI as MCP-connected research accelerator
- Automated citation-to-confidence mapping (Perplexity sources mapped to Confirmed/Estimated/Speculative)
- Batch research workflows -- update all 33 competitors in a single session
- Real-time data freshness monitoring with alerts when competitor data goes stale

### Nuclear Intelligence Module *(CTO/Board Eyes Only)*

- AI Talent Tracker -- maps key AI/ML personnel at each competitor
- Talent concentration risk scoring and acqui-hire attractiveness assessment
- Confidential classification with ethical guardrails (public data only)

---

## By the Numbers

| Metric | Value |
|---|---|
| Competitors tracked | 33 (across 8 European countries) |
| Data dimensions per competitor | 60+ structured fields |
| Research prompts | 10 specialized prompts |
| Dashboard sheets | 18+ (and growing) |
| Test coverage | 84% (157 tests) |
| Pipeline speed | 0.56 seconds for full generation |
| Revenue data coverage | EUR 32M (Eneve) to EUR 14.5B (largest competitor) |
| Classification bands | Rocket / Riser / Steady / Dinosaur |
| Confidence scoring | 5-dimension quality assessment per competitor |

---

## What Makes This Different

1. **Eneve is on every chart** -- not just tracking competitors, but showing exactly where Eneve stands relative to each one
2. **Source-attributed and confidence-scored** -- every data point traces back to a source with a reliability rating, not just "we think"
3. **AI-augmented, human-validated** -- structured prompts drive systematic research, but human judgment validates every classification
4. **Board-ready out of the box** -- not a raw data dump; it tells a strategic story with executive KPIs, narrative sections ("The Meteor Warning"), and professional formatting
5. **Built for the energy vertical** -- understands energy protocols, TSO/DSO market structure, balancing/settlement, and the specific dynamics of European energy software M&A
