# Planning Cycle 2: Comprehensive Task Breakdown & Sequencing

**Date**: Feb 26, 2026  
**Status**: IN PROGRESS  
**Agent**: Prometheus (Plan Builder)

---

## Executive Summary

- **Total Untested Modules**: 70 files (~14,000+ LOC untested)
- **Estimated Coverage Gain**: 20-25 percentage points (56% → 76-81%)
- **Estimated Total Effort**: 80-120 hours
- **Recommended Timeline**: 3-4 weeks (full-time) or 8-12 weeks (part-time)

---

## Task Grouping Strategy

### Group 1: INFRASTRUCTURE LAYER (Critical Foundation - 12 modules, ~2,000 LOC)

**Why First**: Database, refresh connectors, and repositories are depended on by everything else.

#### 1.1 - Refresh Connector Suite (12 connectors, ~1,668 LOC)
**Modules**: github_refresh.py, yahoo_finance_refresh.py, sec_edgar_refresh.py, companies_house_refresh.py, news_refresh.py, news_signal_refresh.py, funding_refresh.py, patents_refresh.py, website_refresh.py, linkedin_refresh.py, global_market_refresh.py, web_search_refresh.py

**Size**: 100-200 lines each  
**Complexity**: SIMPLE (pattern is consistent across all)  
**Effort**: 8 hours (40 min per connector, parallel testing)  
**Coverage Gain**: +8 pp  
**Pattern**: Each inherits from BaseRefreshConnector, implements fetch_facts(), has similar test structure

**Acceptance Criteria**:
- [ ] Each connector has 3-5 test methods (init, fetch_facts, error handling, delta detection)
- [ ] Mock external connectors (GitHubConnector, YahooFinanceConnector, etc.)
- [ ] Test both success and failure paths
- [ ] Verify async/await handling with AsyncMock

**Task Breakdown**:
- 1.1.1: github_refresh_connector.py (221 lines, 40 min)
- 1.1.2: yahoo_finance_refresh_connector.py (191 lines, 40 min)
- 1.1.3: sec_edgar_refresh_connector.py (206 lines, 40 min)
- 1.1.4: companies_house_refresh_connector.py (169 lines, 40 min)
- 1.1.5: news_refresh_connector.py (145 lines, 40 min)
- 1.1.6: news_signal_refresh_connector.py (148 lines, 40 min)
- 1.1.7: funding_refresh_connector.py (144 lines, 40 min)
- 1.1.8: patents_refresh_connector.py (133 lines, 40 min)
- 1.1.9: website_refresh_connector.py (148 lines, 40 min)
- 1.1.10: linkedin_refresh_connector.py (124 lines, 40 min)
- 1.1.11: global_market_refresh_connector.py (128 lines, 40 min)
- 1.1.12: web_search_refresh_connector.py (102 lines, 40 min)

#### 1.2 - Database Layer (3 modules, ~1,000 LOC)
**Modules**: database.py, database_service.py, repositories.py, enrichment_repositories.py

**Effort**: 6 hours  
**Coverage Gain**: +4 pp  
**Dependencies**: None (foundation)

**Task Breakdown**:
- 1.2.1: database.py (137 lines, 1 hour) - Connection management, schema setup
- 1.2.2: database_service.py (180 lines, 1.5 hours) - CRUD operations, transactions
- 1.2.3: repositories.py (303 lines, 2 hours) - Abstract repository pattern
- 1.2.4: enrichment_repositories.py (215 lines, 1.5 hours) - Specialized repositories

#### 1.3 - Conflict Resolution & Reconciliation (2 modules, ~600 LOC)
**Modules**: conflict_resolution.py, reconcile_runs.py

**Effort**: 4 hours  
**Coverage Gain**: +3 pp  

**Task Breakdown**:
- 1.3.1: conflict_resolution.py (307 lines, 2 hours) - Source authority, fact merging
- 1.3.2: reconcile_runs.py (305 lines, 2 hours) - Pipeline reconciliation

#### 1.4 - Middleware & Routes (3 modules, ~400 LOC)
**Modules**: api_middleware_logging.py, api_middleware_security.py, api_routes_refresh.py

**Effort**: 3 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 1.4.1: middleware_logging.py (120 lines, 1 hour)
- 1.4.2: middleware_security.py (95 lines, 45 min)
- 1.4.3: routes_refresh.py (150 lines, 1 hour)

---

### Group 2: ANALYTICS LAYER (Core Logic - 8 modules, ~2,500 LOC)

**Why Second**: Depends on infrastructure, needed before API testing

#### 2.1 - Scoring Utilities (3 modules, ~700 LOC)
**Modules**: confidence_integration.py, growth_momentum.py, competitive_position.py

**Effort**: 4 hours  
**Coverage Gain**: +3 pp

**Task Breakdown**:
- 2.1.1: confidence_integration.py (220 lines, 1.5 hours) - Complex scoring logic
- 2.1.2: growth_momentum.py (193 lines, 1 hour) - Growth scoring
- 2.1.3: competitive_position.py (287 lines, 1.5 hours) - Competition analysis

#### 2.2 - Filters & Signals (3 modules, ~1,200 LOC)
**Modules**: filters_llm.py, signals_extractors.py, signals_filters/*

**Effort**: 6 hours  
**Coverage Gain**: +4 pp

**Task Breakdown**:
- 2.2.1: filters_llm.py (393 lines, 2 hours) - LLM-based filtering
- 2.2.2: signals_extractors.py (309 lines, 1.5 hours) - Signal extraction
- 2.2.3: signals_filters_suite.py (500 lines, 2.5 hours) - Multiple filter implementations

#### 2.3 - Analytics Support (2 modules, ~600 LOC)
**Modules**: workflows.py, simulation_market.py

**Effort**: 3 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 2.3.1: workflows.py (240 lines, 1.5 hours) - Workflow orchestration
- 2.3.2: simulation_market.py (360 lines, 1.5 hours) - Market simulation

---

### Group 3: DATA LAYER (Complex Logic - 8 modules, ~3,500 LOC)

**Why Third**: Depends on infrastructure, feeds into analytics

#### 3.1 - Data Loading (4 modules, ~2,200 LOC)
**Modules**: additional_sources.py, enrichment_orchestrator.py, connectors_lookup_service.py, markets.py

**Effort**: 8 hours  
**Coverage Gain**: +5 pp

**Task Breakdown**:
- 3.1.1: additional_sources.py (768 lines, 2.5 hours) - Alternative data sources
- 3.1.2: enrichment_orchestrator.py (533 lines, 2 hours) - Enrichment coordination
- 3.1.3: connectors_lookup_service.py (180 lines, 1 hour) - Connector registry
- 3.1.4: markets.py (510 lines, 2 hours) - Market data aggregation

#### 3.2 - Data Connectors (4 modules, ~1,300 LOC)
**Modules**: connectors/sec_edgar/, connectors/companies_house/, connectors/news_signal/, etc.

**Effort**: 6 hours  
**Coverage Gain**: +3 pp

**Task Breakdown**:
- 3.2.1: sec_edgar_connector.py (206 lines, 1.5 hours)
- 3.2.2: companies_house_connector.py (169 lines, 1 hour)
- 3.2.3: news_signal_detector.py (248 lines, 1.5 hours)
- 3.2.4: news_connector.py (180 lines, 1 hour)
- 3.2.5: funding_connector.py (150 lines, 1 hour)
- 3.2.6: patents_connector.py (145 lines, 1 hour)

---

### Group 4: API LAYER (Contract Testing - 10 modules, ~2,000 LOC)

**Why Fourth**: Depends on analytics, most visible to users

#### 4.1 - Router Endpoints (4 modules, ~1,000 LOC)
**Modules**: routers/async_jobs.py, routers/market.py, routers/jobs.py, routers/drill_down.py

**Effort**: 5 hours  
**Coverage Gain**: +3 pp

**Task Breakdown**:
- 4.1.1: async_jobs.py (277 lines, 1.5 hours) - Background job endpoints
- 4.1.2: market.py (148 lines, 1 hour) - Market analysis endpoints
- 4.1.3: jobs.py (185 lines, 1 hour) - Job management endpoints
- 4.1.4: drill_down.py (226 lines, 1 hour) - Drill-down endpoints

#### 4.2 - Services & Dependencies (3 modules, ~600 LOC)
**Modules**: services_enrichment_service.py, services_drill_down_service.py, dependencies.py

**Effort**: 4 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 4.2.1: enrichment_service.py (240 lines, 1.5 hours)
- 4.2.2: drill_down_service.py (195 lines, 1 hour)
- 4.2.3: dependencies.py (165 lines, 1.5 hours)

#### 4.3 - Main & Middleware (3 modules, ~400 LOC)
**Modules**: main.py, middleware_errors.py, exception_handlers.py

**Effort**: 2 hours  
**Coverage Gain**: +1 pp

**Task Breakdown**:
- 4.3.1: main.py (180 lines, 1 hour)
- 4.3.2: middleware_errors.py (120 lines, 45 min)
- 4.3.3: exception_handlers.py (100 lines, 15 min)

---

### Group 5: RESEARCH & AGENTS (Orchestration - 12 modules, ~2,000 LOC)

**Why Fifth**: Depends on analytics & data, feeds into API

#### 5.1 - Research Pipeline (4 modules, ~1,600 LOC)
**Modules**: research/discover.py, research/gather.py, research/pipeline.py, research/signals.py

**Effort**: 8 hours  
**Coverage Gain**: +4 pp

**Task Breakdown**:
- 5.1.1: discover.py (653 lines, 2.5 hours) - Discovery process
- 5.1.2: gather.py (647 lines, 2.5 hours) - Gathering coordination
- 5.1.3: pipeline.py (532 lines, 2 hours) - Pipeline orchestration
- 5.1.4: signals.py (417 lines, 1 hour) - Signal processing

#### 5.2 - Agents (5 modules, ~1,200 LOC)
**Modules**: agents/github_agent.py (already tested?), agents/companies_house_agent.py, agents/additional_agents.py, agents/resilience.py, agents/coordinator.py (status TBD)

**Effort**: 6 hours  
**Coverage Gain**: +3 pp

**Task Breakdown**:
- 5.2.1: github_agent.py (771 lines, 2 hours) - If gaps exist
- 5.2.2: companies_house_agent.py (310 lines, 1.5 hours)
- 5.2.3: additional_agents.py (268 lines, 1 hour)
- 5.2.4: resilience_agent.py (316 lines, 1.5 hours)

#### 5.3 - Research Support (3 modules, ~800 LOC)
**Modules**: research/aggregate.py, research/evidence.py, research/narrative.py

**Effort**: 4 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 5.3.1: aggregate.py (663 lines, 2 hours)
- 5.3.2: evidence.py (137 lines, 1 hour)
- 5.3.3: narrative.py (200 lines, 1 hour)

---

### Group 6: EXPORTERS & PRESENTATION (Reporting - 10 modules, ~1,500 LOC)

**Why Sixth**: Depends on analytics, optional for core functionality

#### 6.1 - Exporters (4 modules, ~1,200 LOC)
**Modules**: exporters/excel.py, exporters/audit_report.py, exporters/markdown/generator.py, exporters/llm.py

**Effort**: 6 hours  
**Coverage Gain**: +3 pp

**Task Breakdown**:
- 6.1.1: excel.py (352 lines, 1.5 hours)
- 6.1.2: audit_report.py (285 lines, 1.5 hours)
- 6.1.3: markdown_generator.py (1223 lines, 2 hours - split across tests)
- 6.1.4: llm.py (593 lines, 1 hour)

#### 6.2 - Presentation & Templates (3 modules, ~600 LOC)
**Modules**: presentation/adaptive_templates.py, presentation/narrative_consistency.py, presentation/data_quality_indicators.py

**Effort**: 3 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 6.2.1: adaptive_templates.py (287 lines, 1.5 hours)
- 6.2.2: narrative_consistency.py (238 lines, 1 hour)
- 6.2.3: data_quality_indicators.py (221 lines, 30 min)

#### 6.3 - Extractors & Support (3 modules, ~500 LOC)
**Modules**: extractors/markdown_extractor.py, application_exporters_llm.py, application_analytics_filters_llm.py

**Effort**: 2 hours  
**Coverage Gain**: +1 pp

**Task Breakdown**:
- 6.3.1: markdown_extractor.py (486 lines, 1.5 hours)
- 6.3.2: application_exporters.py (50 lines, 15 min)
- 6.3.3: application_filters.py (40 lines, 15 min)

---

### Group 7: UTILITIES & SUPPORT (Low Priority - 14 modules, ~1,000 LOC)

**Why Seventh**: Optional, low impact on core functionality

#### 7.1 - Configuration & Setup (4 modules, ~700 LOC)
**Modules**: celery_config.py, config_validation.py, core_supabase_client.py, cli_coverage.py

**Effort**: 3 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 7.1.1: celery_config.py (135 lines, 45 min)
- 7.1.2: config_validation.py (180 lines, 1 hour)
- 7.1.3: core_supabase_client.py (44 lines, 15 min)
- 7.1.4: cli_coverage.py (341 lines, 1 hour)

#### 7.2 - Utilities & Monitoring (5 modules, ~600 LOC)
**Modules**: utils/logging.py, core/monitoring.py, core/production_hardening.py, etc.

**Effort**: 3 hours  
**Coverage Gain**: +2 pp

**Task Breakdown**:
- 7.2.1: logging.py (106 lines, 30 min)
- 7.2.2: monitoring.py (421 lines, 1.5 hours)
- 7.2.3: production_hardening.py (306 lines, 1 hour)

#### 7.3 - Miscellaneous (5 modules, ~200 LOC)
**Modules**: constants.py, exceptions.py, worker.py, etc.

**Effort**: 1 hour  
**Coverage Gain**: +1 pp

**Task Breakdown**:
- 7.3.1: constants.py (70 lines, 15 min)
- 7.3.2: exceptions.py (43 lines, 10 min)
- 7.3.3: worker.py (24 lines, 5 min)
- 7.3.4: miscellaneous.py (63 lines, 20 min)

---

## Task Summary by Group

| Group | Category | Tasks | LOC | Hours | Coverage | Dependencies |
|-------|----------|-------|-----|-------|----------|--------------|
| 1 | INFRASTRUCTURE | 20 | 4,000 | 21 | +17 pp | None |
| 2 | ANALYTICS | 8 | 2,500 | 13 | +9 pp | Group 1 |
| 3 | DATA LAYER | 8 | 3,500 | 14 | +8 pp | Group 1 |
| 4 | API LAYER | 10 | 2,000 | 11 | +6 pp | Groups 2-3 |
| 5 | RESEARCH/AGENTS | 12 | 2,000 | 18 | +9 pp | Groups 1-2 |
| 6 | EXPORTERS/PRESENTATION | 10 | 2,300 | 11 | +6 pp | Group 2 |
| 7 | UTILITIES | 14 | 1,200 | 7 | +5 pp | All groups |
| **TOTAL** | | **82 tasks** | **~17,500 LOC** | **95 hours** | **+60 pp** | **Parallel** |

---

## Critical Path & Dependencies

```
Group 1 (Infrastructure) [21 hours]
    ↓
Group 2 (Analytics) [13 hours] + Group 3 (Data) [14 hours] [Parallel]
    ↓
Group 4 (API) [11 hours] + Group 5 (Research/Agents) [18 hours] [Parallel]
    ↓
Group 6 (Exporters) [11 hours] + Group 7 (Utilities) [7 hours] [Parallel]
```

**Total Critical Path**: 21 + 14 + 18 + 11 = 64 hours (with parallelization)  
**Sequential Time**: 95 hours  
**Parallelization Savings**: 31 hours (~32% faster)

---

## Quick Wins (High Impact, Low Effort)

1. **Refresh Connectors** (12 modules, 8 hours, +8 pp) - Consistent pattern, high ROI
2. **Database Layer** (4 modules, 6 hours, +4 pp) - Foundation for everything
3. **API Endpoints** (4 modules, 5 hours, +3 pp) - Clear contract testing
4. **Configuration** (4 modules, 3 hours, +2 pp) - Simple utilities

---

## Cycle 2 Conclusions

✅ **Task breakdown complete**: 82 tasks across 7 groups  
✅ **Coverage estimate**: 56% + 25 pp = ~81% total coverage  
✅ **Effort estimate**: 95 hours (full-time: 2-3 weeks, part-time: 6-8 weeks)  
✅ **Parallelization potential**: 32% speedup with parallel execution  
✅ **No blockers identified**: All modules are independently testable

**Next: Cycle 3 will create execution waves and parallelization strategy**

