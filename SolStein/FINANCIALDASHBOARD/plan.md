# FINANCIALDASHBOARD: Board-Ready Excel Financial Dashboard

**Part of**: [Solstein](../SOLSTEIN/README.md) -- Module 4 (Financial Dashboard) tooling

## Objective

Elevate the competitor financial dashboard from a developer-grade data dump to a board-ready strategic intelligence workbook. The CTO and potentially the Board will use this to understand Eneve's competitive position at a glance.

## Current State

7 sheets: Summary, Revenue Leaderboard, Funding Leaderboard, Employee Growth, SaaS Maturity, Classification Matrix, Raw Data. One bar chart (Revenue CAGR). Basic color-coding (Rocket=green, Dinosaur=red, Eneve=yellow). Hyperlinks to source files.

## Target State

A polished, multi-sheet workbook that tells a compelling competitive story with executive-level KPIs, rich visualizations, professional styling, and data-backed Eneve positioning -- ready for board presentation.

## Complexity Assessment

- **Classification**: Complex Implementation
- **Effort**: 3-5 days total across all subtasks
- **Risk**: Low-Medium (additive changes, no breaking modifications)
- **Components**: `extract_competitor_data.py`, `generate_excel_report.py`, `competitor_utils.py`

## Subtasks -- Phase 1: Board-Ready Dashboard (COMPLETE)

| # | Ticket | Summary | Effort | Status |
|---|--------|---------|--------|--------|
| 1 | [FD-001](DONE/FD-001-executive-summary/plan.md) | Executive Summary Sheet | 2-3h | DONE |
| 2 | [FD-002](DONE/FD-002-charts/plan.md) | Charts for All Sheets | 1-2h | DONE |
| 3 | [FD-003](DONE/FD-003-extract-data/plan.md) | Extract Additional Data | 2-3h | DONE |
| 4 | [FD-004](DONE/FD-004-new-sheets/plan.md) | New Sheets (Efficiency & Market Reach) | 2h | DONE |
| 5 | [FD-005](DONE/FD-005-styling/plan.md) | Professional Styling | 2-3h | DONE |
| 6 | [FD-006](DONE/FD-006-eneve-positioning/plan.md) | Eneve vs Market Sheet | 1-2h | DONE |
| 7 | [FD-007](DONE/FD-007-sparklines/plan.md) | Sparklines | 1h | DONE |
| 8 | [FD-008](DONE/FD-008-methodology/plan.md) | Methodology Sheet | 30min | DONE |

## Subtasks -- Phase 2: Advanced Quality Level

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 9 | [FD-009](DONE/FD-009-unit-tests/plan.md) | ~~Unit Tests (original scope)~~ | -- | DONE (superseded by FD-042) |
| 10 | [FD-010](FD-010-progress-caching/plan.md) | Progress Reporting + Smart Caching | 2-3h | FD-001 to FD-008 |
| 11 | [FD-011](FD-011-performance-measurement/plan.md) | Performance Measurement & Optimization | 2-3h | FD-009, FD-010 |
| 42 | [FD-042](FD-042-unit-tests-revisited/plan.md) | Unit Tests Revisited (pytest, 50%+ coverage, Phase 3 scope) | 4-6h | FD-001 to FD-008, Phase 3 |

### Advanced Quality Level Criteria

Scripts currently meet **Standard** quality level. To reach **Advanced**, all three must be completed:

| Criterion | Ticket | Current State |
|---|---|---|
| 2+ Advanced Features | FD-010 | DONE (Rich progress bars + MD5 caching) |
| Unit Tests (50%+ coverage) | FD-042 | 0% coverage (FD-009 superseded, FD-042 scoped for Phase 3) |
| Performance Optimized | FD-011 | DONE (profiled and documented) |

## Subtasks -- Phase 3: PE-Firm-Ready Intelligence Sheets

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 12 | [FD-012](FD-012-ai-maturity-matrix/plan.md) | AI Maturity Matrix -- score every competitor on AI adoption | 2-3h | -- |
| 13 | [FD-013](FD-013-investment-efficiency/plan.md) | Investment Efficiency Ratios -- revenue/employee, capital efficiency | 1-2h | -- |
| 14 | [FD-014](FD-014-mna-vulnerability/plan.md) | M&A Vulnerability Map -- acquirers vs targets classification | 2-3h | -- |
| 15 | [FD-015](FD-015-threat-timeline/plan.md) | Threat Convergence Timeline -- Gantt-style threat calendar | 2h | -- |
| 16 | [FD-016](FD-016-competitive-overlap/plan.md) | Competitive Overlap Heatmap -- 33x33 overlap matrix | 2h | -- |
| 17 | [FD-017](FD-017-geographic-tracker/plan.md) | Geographic Expansion Tracker -- country-vs-competitor matrix | 1-2h | -- |
| 18 | [FD-018](FD-018-confidence-dashboard/plan.md) | Confidence Dashboard -- data quality and research depth per competitor | 1h | -- |
| 19 | [FD-019](FD-019-scenario-projections/plan.md) | Scenario Projections -- 3-year extrapolation at current CAGR | 2h | -- |
| 20 | [FD-020](FD-020-portfolio-risk/plan.md) | Portfolio Risk Dashboard -- aggregate risk matrix with KPIs | 2-3h | -- |
| 21 | [FD-021](FD-021-dynamic-filters/plan.md) | Dynamic Filters / Slicers -- pivot table with interactive exploration | 2-3h | FD-012, FD-017 |
| 22 | [FD-022](FD-022-phase3-styling/plan.md) | Phase 3 Styling Pass -- consistent styling across all new sheets | 2-3h | FD-012 to FD-021 |
| 23 | [FD-023](FD-023-geographic-map/plan.md) | European Geographic Map -- embedded map with HQ/subsidiary/market markers | 2-3h | FD-017 |

**Phase 3 Total Effort**: ~20-28h

## Subtasks -- Phase 4: Data Collection Completeness & Research Acceleration

Ensures all dashboard sheets have complete, structured data pipelines from research prompts, fills prompt gaps, and integrates Perplexity AI as a research accelerator.

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 24 | [FD-024](FD-024-prompt-data-alignment/plan.md) | Prompt-Dashboard Data Alignment Audit -- gap analysis between prompts and dashboard data needs | 1-2h | -- |
| 25 | [FD-025](FD-025-ai-maturity-prompt/plan.md) | AI Maturity Research Prompt -- structured AI scoring per competitor | 2-3h | FD-024 |
| 26 | [FD-026](FD-026-competitive-overlap-prompt/plan.md) | Competitive Overlap Research Prompt -- pairwise overlap matrix | 2-3h | FD-024 |
| 27 | [FD-027](FD-027-data-confidence-prompt/plan.md) | Data Confidence Assessment Prompt -- per-competitor data quality scores | 1-2h | FD-024 |
| 28 | [FD-028](FD-028-market-trends-prompt/plan.md) | Market Trends & Regulatory Research Prompt -- macro trends and regulatory tracking | 2-3h | FD-024 |
| 29 | [FD-029](FD-029-customer-intelligence-prompt/plan.md) | Customer Intelligence Research Prompt -- win/loss, switching, reference clients | 2-3h | FD-024 |
| 30 | [FD-030](FD-030-perplexity-integration/plan.md) | Perplexity AI Integration -- MCP server + prompt adaptation for research acceleration | 3-4h | -- |

**Phase 4 Total Effort**: ~14-20h

## Subtasks -- Phase 5: Nuclear Intelligence (CONFIDENTIAL)

Strategic intelligence sheets for CTO/Board consumption only. Handle with care.

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 31 | [FD-031](FD-031-ai-talent-tracker/plan.md) | AI Talent Tracker -- key AI personnel, acqui-hire targets, talent concentration risk | 4-6h | FD-024 |

**Phase 5 Total Effort**: ~4-6h (excluding per-competitor research time)

## Subtasks -- Phase 6: C# Migration

Rewrites the Python dashboard scripts to C# for integration with the .NET ecosystem.

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 40 | [FD-040](FD-040-rewrite-csharp/plan.md) | Rewrite Dashboard Scripts to C# -- port extraction, report generation, and utilities to .NET with ClosedXML | 5-8d | Phase 1 (reference impl) |

**Phase 6 Total Effort**: ~5-8 days

## Subtasks -- Phase 7: Web Interface & API Service

Interactive web dashboard and REST API replacing static Excel distribution.

| # | Ticket | Summary | Effort | Dependencies |
|---|--------|---------|--------|--------------|
| 41 | [FD-041](FD-041-web-interface-api/plan.md) | Web Interface & API Service -- ASP.NET Core API + SPA frontend with interactive charts and drill-down | 10-15d | FD-040 (shared C# data layer) |

**Phase 7 Total Effort**: ~10-15 days

## Recommended Execution Order

**Phase 1 COMPLETE.** Phase 2: **FD-009 first** (tests protect against regressions), then **FD-010** (new features with test safety net), then **FD-011** (measure and optimize with full test coverage). Phase 3: independent sheets can be built in any order; FD-021 (slicers) depends on FD-012 and FD-017 data being in Raw Data; FD-022 (styling) goes last. Phase 4: **FD-024 first** (audit identifies exact gaps), then FD-025 to FD-029 (new prompts, can be done in parallel), **FD-030 in parallel** (Perplexity integration is independent). Phase 4 prompts should be created before running Phase 3 data-heavy sheets (FD-012, FD-016, FD-018 need the data these prompts produce). **Phase 6**: FD-040 (C# rewrite) can start once Phase 1 is stable as reference implementation; benefits from Phase 2 test coverage. **Phase 7**: FD-041 (Web Interface & API) depends on FD-040 for shared C# data models -- start API foundation once FD-040 Phase A models are defined.

## Files Modified

- `.cursor/scripts/analysis/market/extract_competitor_data.py` -- FD-003
- `.cursor/scripts/analysis/market/generate_excel_report.py` -- FD-001, FD-002, FD-004, FD-005, FD-006, FD-007, FD-008
- `.cursor/scripts/analysis/market/competitor_utils.py` -- FD-003
- `.cursor/prompts/analysis/market/*.prompt.md` -- FD-025 to FD-029 (new prompts), FD-030 (Perplexity adaptation)
- `src/CompetitiveIntelligence/**` -- FD-040 (new C# solution: models, services, CLI)
- `src/CompetitiveIntelligence.Api/**` -- FD-041 (new ASP.NET Core Web API)
- `src/CompetitiveIntelligence.Web/**` -- FD-041 (new SPA frontend)

## Acceptance Criteria

### Phase 1: Board-Ready Dashboard (COMPLETE)

- [x] All 8 subtasks completed and verified
- [x] Excel opens with Executive Summary as first sheet
- [x] Charts present on 6+ sheets
- [x] Professional color palette and formatting throughout
- [x] Eneve highlighted and positioned against market
- [x] Print-ready with confidential footer
- [x] Scripts pass `py_compile` and `--help` validation

### Phase 2: Advanced Quality Level

- [ ] FD-009: pytest test suite with 50%+ code coverage
- [ ] FD-010: Progress reporting (Rich) and smart caching (MD5 hashing)
- [ ] FD-011: Performance profiled, bottlenecks identified, optimizations applied and documented
- [ ] All 3 scripts meet Advanced quality level criteria
- [ ] PERFORMANCE.md documents baseline, optimizations, and scaling

### Phase 3: PE-Firm-Ready Intelligence

- [ ] FD-012: AI Maturity Matrix with heatmap and bar chart
- [ ] FD-013: Investment Efficiency Ratios with scatter plot
- [ ] FD-014: M&A Vulnerability Map with quadrant chart
- [ ] FD-015: Threat Convergence Timeline (Gantt-style)
- [ ] FD-016: Competitive Overlap Heatmap (33x33 matrix)
- [ ] FD-017: Geographic Expansion Tracker with country matrix
- [ ] FD-018: Confidence Dashboard with stacked bar chart
- [ ] FD-019: Scenario Projections (3-year extrapolation)
- [ ] FD-020: Portfolio Risk Dashboard with bubble chart
- [ ] FD-021: Dynamic Filters / Slicers for interactive exploration
- [ ] FD-022: Phase 3 styling consistent with Phase 1 quality
- [ ] FD-023: European map image embedded on Geographic Reach sheet with HQ, subsidiary, and market markers
- [ ] Workbook tells a complete PE-ready competitive intelligence story

### Phase 5: Nuclear Intelligence (CONFIDENTIAL)

- [ ] FD-031: AI Talent Map sheet with per-competitor AI team size, leadership, concentration risk, and acqui-hire scoring
- [ ] Sheet marked CONFIDENTIAL with sensitivity header
- [ ] Ethical guardrails enforced (public data only)

### Phase 4: Data Collection Completeness

- [ ] FD-024: Prompt-dashboard data alignment audit completed
- [ ] FD-025: AI Maturity research prompt created and tested
- [ ] FD-026: Competitive Overlap research prompt created and tested
- [ ] FD-027: Data Confidence assessment prompt created and tested
- [ ] FD-028: Market Trends & Regulatory research prompt created and tested
- [ ] FD-029: Customer Intelligence research prompt created and tested
- [ ] FD-030: Perplexity AI integrated as MCP tool, at least 3 prompts adapted
- [ ] All Phase 3 dashboard sheets have dedicated upstream data collection prompts

### Phase 6: C# Migration

- [ ] FD-040: C# solution compiles with zero warnings
- [ ] FD-040: CLI produces Excel workbook matching Python output (sheet-for-sheet, chart-for-chart)
- [ ] FD-040: All Phase 1 features preserved in C# (Executive Summary, Charts, Sparklines, Styling, Methodology)
- [ ] FD-040: Unit tests with 60%+ coverage (xUnit)
- [ ] FD-040: ClosedXML (or EPPlus) used for Excel generation
- [ ] FD-040: Clean architecture with separation of extraction, generation, utilities

### Phase 7: Web Interface & API Service

- [ ] FD-041: ASP.NET Core Web API running with Swagger UI
- [ ] FD-041: Minimum 8 API endpoints covering all major data areas
- [ ] FD-041: Web frontend displays executive summary dashboard with KPIs
- [ ] FD-041: Interactive charts for Revenue, Funding, Employee, SaaS metrics
- [ ] FD-041: Competitor list with filter/sort/search functional
- [ ] FD-041: Competitor detail page shows full profile
- [ ] FD-041: Authentication implemented (API key minimum)
- [ ] FD-041: Responsive on desktop and tablet
- [ ] FD-041: Excel export from dashboard matches Phase 1 output
- [ ] FD-041: API response times < 200ms for list endpoints
- [ ] FD-041: Unit tests with 60%+ coverage on API layer
