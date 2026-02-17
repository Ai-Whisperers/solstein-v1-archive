# Roadmap -- FINANCIALDASHBOARD

**Last Updated**: 2026-02-17

## Objective

Transform the competitor financial dashboard from a developer-grade data dump into a board-ready, PE-firm-grade strategic intelligence workbook -- then migrate to C# and a web interface for long-term maintainability and interactive access.

**Out of scope**: Real-time data feeds, automated competitor monitoring, third-party SaaS integrations, mobile-native app.

## Status Summary

| Phase | Description | Tickets | Complete | Remaining | Status |
|-------|-------------|---------|----------|-----------|--------|
| 1 | Board-Ready Dashboard | 8 | 8 | 0 | COMPLETE |
| 2 | Advanced Quality Level | 4 | 3 | 1 | IN PROGRESS |
| 3 | PE-Firm-Ready Intelligence | 12 | 9 | 3 | IN PROGRESS |
| 4 | Data Collection & Prompts | 7+3 | 4 | 6 | IN PROGRESS |
| 5 | Nuclear Intelligence | 1 | 0 | 1 | PLANNING |
| 6 | C# Migration | 1 | 0 | 1 | PLANNING |
| 7 | Web Interface & API | 1 | 0 | 1 | PLANNING |

**Overall**: 23 of 37 tickets complete (62%). Active work on Phases 2-4.

## Milestones

### Milestone 1: Board-Ready Dashboard -- COMPLETE

**Date**: 2026-02-15 (delivered)

- **Scope**: FD-001 through FD-008
- **Owner(s)**: Team
- **Dependencies**: None
- **DOD**: 12-sheet Excel workbook with executive summary, charts, styling, methodology, sparklines, and Eneve positioning. All scripts at Standard quality level.
- **Result**: All 8 tickets delivered. 12 sheets, 62 KB workbook. 24 competitors extracted. All 3 scripts exit 0.

### Milestone 2: Advanced Quality Level

**Window**: Current -- targeting completion within 1 week

- **Scope**: FD-009 (superseded), FD-010, FD-011, FD-042
- **Owner(s)**: Team
- **Dependencies**: Phase 1 complete (met). FD-042 also benefits from Phase 3 being mostly complete.
- **DOD**: pytest suite with 50%+ coverage, Rich progress bars with MD5 caching, performance profiled and documented in PERFORMANCE.md.

| Ticket | Summary | Status | Effort |
|--------|---------|--------|--------|
| FD-009 | ~~Unit Tests (original Phase 1 scope)~~ | DONE (superseded by FD-042) | -- |
| FD-010 | Progress Reporting + Smart Caching | Complete | -- |
| FD-011 | Performance Measurement & Optimization | Complete | -- |
| FD-042 | Unit Tests Revisited (Phase 3 scope, ~4,200 lines) | Ready for Implementation | 4-6h |

**Remaining work**: FD-042 only (unit tests covering full Phase 1+3 codebase).

### Milestone 3: PE-Firm-Ready Intelligence Sheets

**Window**: Current -- targeting completion within 2-3 weeks

- **Scope**: FD-012 through FD-023 (12 tickets)
- **Owner(s)**: Team
- **Dependencies**: FD-033 (Geographic prompt) blocks FD-017 and FD-023. FD-017 blocks FD-023. All feature tickets block FD-022 (styling pass).
- **DOD**: 18+ sheet workbook with AI maturity, investment efficiency, M&A vulnerability, threat timeline, competitive overlap, geographic tracker, confidence dashboard, scenario projections, portfolio risk, dynamic filters, styling, and embedded European map. Complete PE-ready competitive intelligence story.

| Ticket | Summary | Status | Effort | Blocker |
|--------|---------|--------|--------|---------|
| FD-012 | AI Maturity Matrix | Complete | -- | -- |
| FD-013 | Investment Efficiency Ratios | Complete | -- | -- |
| FD-014 | M&A Vulnerability Map | Complete | -- | -- |
| FD-015 | Threat Convergence Timeline | Complete | -- | -- |
| FD-016 | Competitive Overlap Heatmap | Complete | -- | -- |
| FD-017 | Geographic Expansion Tracker | Planning | 1-2h | FD-033 (geographic prompt) |
| FD-018 | Confidence Dashboard | Complete | -- | -- |
| FD-019 | Scenario Projections | Complete | -- | -- |
| FD-020 | Portfolio Risk Dashboard | Complete | -- | -- |
| FD-021 | Dynamic Filters / Slicers | Complete | -- | -- |
| FD-022 | Phase 3 Styling Pass | Not Started | 2-3h | FD-017, FD-023 |
| FD-023 | European Geographic Map | Planning | 2-3h | FD-017 |

**Remaining work**: FD-017 -> FD-023 -> FD-022 (sequential chain). FD-033 should be completed first to provide data for FD-017.

### Milestone 4: Data Collection Completeness & Prompt Library

**Window**: Current (parallel with Milestone 3) -- targeting completion within 2-3 weeks

- **Scope**: FD-024 through FD-030 + FD-032, FD-033, FD-034
- **Owner(s)**: Team
- **Dependencies**: FD-024 (audit) should run first to confirm gaps. FD-033 blocks Phase 3 FD-017.
- **DOD**: All Phase 3 dashboard sheets have dedicated upstream research prompts. Perplexity AI integrated. Dashboard prompt updated to 18-sheet scope.

| Ticket | Summary | Status | Effort | Dependency |
|--------|---------|--------|--------|------------|
| FD-024 | Prompt-Dashboard Data Alignment Audit | Not Started | 1-2h | -- |
| FD-025 | AI Maturity Research Prompt | Not Started | 2-3h | FD-024 |
| FD-026 | Competitive Overlap Research Prompt | Complete | -- | -- |
| FD-027 | Data Confidence Assessment Prompt | Complete | -- | -- |
| FD-028 | Market Trends & Regulatory Research Prompt | Complete | -- | -- |
| FD-029 | Customer Intelligence Research Prompt | Complete | -- | -- |
| FD-030 | Perplexity AI Integration | Planning | 3-4h | -- |
| FD-032 | Update Dashboard Prompt to 18-Sheet Scope | Planning | 1-2h | -- |
| FD-033 | Geographic Intelligence Research Prompt | Planning | 2-3h | Blocks FD-017, FD-023 |
| FD-034 | Portfolio Risk Synthesis Prompt | Planning | 1-2h | -- |

**Critical path**: FD-033 -> FD-017 -> FD-023 -> FD-022. Start FD-033 immediately to unblock Phase 3 completion.

### Milestone 5: Nuclear Intelligence (CONFIDENTIAL)

**Window**: After Milestone 4 -- 1 week

- **Scope**: FD-031
- **Owner(s)**: Team (CTO/Board consumption only)
- **Dependencies**: FD-024 (prompt-data alignment audit)
- **DOD**: AI Talent Map sheet with per-competitor AI team size, leadership, concentration risk, acqui-hire scoring. Marked CONFIDENTIAL. Ethical guardrails enforced (public data only).

| Ticket | Summary | Status | Effort |
|--------|---------|--------|--------|
| FD-031 | AI Talent Tracker | Planning | 4-6h |

### Milestone 6: C# Migration

**Window**: After Milestones 2-4 stable -- 5-8 days

- **Scope**: FD-040
- **Owner(s)**: Team
- **Dependencies**: Phase 1 as reference implementation. Benefits from Phase 2 test coverage.
- **DOD**: C# solution compiles with zero warnings. CLI produces Excel workbook matching Python output sheet-for-sheet. ClosedXML for Excel generation. xUnit tests with 60%+ coverage. Clean architecture.

| Ticket | Summary | Status | Effort |
|--------|---------|--------|--------|
| FD-040 | Rewrite Dashboard Scripts to C# | Planning | 5-8 days |

### Milestone 7: Web Interface & API Service

**Window**: After Milestone 6 complete -- 10-15 days

- **Scope**: FD-041
- **Owner(s)**: Team
- **Dependencies**: FD-040 (shared C# data layer and models)
- **DOD**: ASP.NET Core Web API with Swagger, 8+ API endpoints, SPA frontend with interactive charts, competitor detail pages, authentication, responsive design, Excel export, <200ms API response times, 60%+ test coverage.

| Ticket | Summary | Status | Effort |
|--------|---------|--------|--------|
| FD-041 | Web Interface & API Service | Planning | 10-15 days |

## Timeline

### Now (Week of 2026-02-17)

- **FD-042**: Implement unit tests revisited (4-6h) -- last Phase 2 item (supersedes FD-009)
- **FD-033**: Create geographic intelligence research prompt (2-3h) -- unblocks Phase 3 chain
- **FD-024**: Run prompt-dashboard data alignment audit (1-2h) -- unblocks Phase 4 prompts

### Next (Week of 2026-02-24)

- **FD-025**: AI Maturity Research Prompt (2-3h)
- **FD-017**: Geographic Expansion Tracker sheet (1-2h) -- after FD-033
- **FD-023**: European Geographic Map (2-3h) -- after FD-017
- **FD-030**: Perplexity AI Integration (3-4h) -- independent
- **FD-032**: Update dashboard prompt to 18-sheet scope (1-2h)
- **FD-034**: Portfolio Risk Synthesis Prompt (1-2h)

### Later (Week of 2026-03-03)

- **FD-022**: Phase 3 Styling Pass (2-3h) -- after all Phase 3 feature tickets
- **FD-031**: AI Talent Tracker (4-6h) -- confidential intelligence
- Phase 2-4 wrap-up, validation, and stabilization

### Future (2026-03 to 2026-04)

- **FD-040**: C# Migration (5-8 days) -- port Python to .NET
- **FD-041**: Web Interface & API (10-15 days) -- interactive dashboard

## Critical Path

```
FD-033 (Geographic Prompt) ─> FD-017 (Geographic Tracker) ─> FD-023 (European Map) ─> FD-022 (Styling Pass)
                                                                                          ^
FD-012..FD-021 (all complete) ────────────────────────────────────────────────────────────┘
```

The critical path for Phase 3 completion runs through the geographic chain. FD-033 is the key unblocking ticket.

## Effort Summary

| Phase | Remaining Effort | Tickets Remaining |
|-------|-----------------|-------------------|
| Phase 2 | ~4-6h | 1 (FD-042) |
| Phase 3 | ~5-8h | 3 (FD-017, FD-022, FD-023) |
| Phase 4 | ~12-17h | 6 (FD-024, FD-025, FD-030, FD-032, FD-033, FD-034) |
| Phase 5 | ~4-6h | 1 (FD-031) |
| Phase 6 | ~5-8 days | 1 (FD-040) |
| Phase 7 | ~10-15 days | 1 (FD-041) |
| **Total (Phases 2-5)** | **~25-37h** | **11 tickets** |
| **Total (incl. 6-7)** | **~15-23 additional days** | **+2 tickets** |

## Risks & Blockers

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| FD-033 not yet created -- blocks geographic chain (FD-017, FD-023, FD-022) | Phase 3 cannot complete | Prioritize FD-033 this week | Team |
| FD-042 unit tests may surface bugs in existing code | Could expand scope of Phase 2 | Budget extra 1-2h for bug fixes discovered by tests | Team |
| Geographic data quality unknown -- FD-017 depends on research prompt output | Geographic sheet may have sparse data | FD-033 prompt should include data completeness assessment | Team |
| Perplexity AI MCP integration (FD-030) depends on external service availability | May delay research acceleration | Can proceed without Perplexity; prompts work with manual research | Team |
| C# migration (FD-040) scope may grow once ClosedXML limitations are encountered | 5-8 day estimate could stretch | Start with core sheets, iterate; use EPPlus as fallback | Team |
| Phase 3 styling (FD-022) scope depends on how many new sheets diverge from Phase 1 palette | Could take longer than 2-3h | Establish style guide early; reuse Phase 1 patterns | Team |

## Open Questions / Unknowns

| Question | Owner | Expected Answer |
|----------|-------|-----------------|
| Should FD-021 (Dynamic Filters) be re-validated after FD-017 adds geographic data? | Team | After FD-017 implementation |
| Is Perplexity AI MCP server available and configured? | Team | Before starting FD-030 |
| Which ClosedXML version supports all required chart types for FD-040? | Team | During FD-040 planning |
| Should Phase 5 (FD-031 AI Talent) use a separate confidential data source? | Team | Before starting FD-031 |
| How should the 18-sheet scope in FD-032 align with any new sheets added in Phases 4-5? | Team | After FD-024 audit |

## Actions (Next 48h)

| Action | Owner | Due |
|--------|-------|-----|
| Start FD-042: Implement pytest suite for market analysis pipeline (revisited) | Team | 2026-02-18 |
| Start FD-033: Create geographic intelligence research prompt | Team | 2026-02-18 |
| Start FD-024: Run prompt-dashboard data alignment audit | Team | 2026-02-19 |
| Review FD-017 plan and confirm geographic data requirements | Team | 2026-02-19 |
