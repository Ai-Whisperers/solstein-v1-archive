# 🗺️ SOLSTEIN COMPLETE ROADMAP: From 56% to 80%+ Coverage

**Plan Version**: 1.0 (Complete after 5 Planning Cycles)  
**Date Generated**: Feb 26, 2026  
**Status**: READY FOR EXECUTION  
**Target Coverage**: 80%+ (from current 56%)

---

## 🎯 EXECUTIVE SUMMARY

### The Challenge
Solstein has **177 Python files, 37,658 LOC, but only 56% test coverage**. This plan transforms it into a **production-ready, world-class platform** with **80%+ coverage, comprehensive tests, and bulletproof quality**.

### The Solution
**82 concrete tasks** organized into **5 execution waves**, estimated at **95 hours of focused work** (6-7 days full-time, 3-4 weeks part-time).

### The Outcome
- ✅ **Coverage**: 56% → 80%+ (all critical modules tested)
- ✅ **Quality**: 5 test pattern templates, standardized QA scenarios
- ✅ **Confidence**: Bulletproof plan with risk mitigation & contingencies
- ✅ **Parallelization**: 5-8 agents can work in parallel per wave

---

## 📊 CURRENT STATE

### Metrics
| Metric | Value |
|--------|-------|
| Python Files | 177 |
| Lines of Code | 37,658 |
| Current Coverage | 56% |
| Untested Modules | 70 (~45%) |
| Existing Tests | 67 test files |
| Coverage Gap | 24-30 pp to reach 80% |

### Module Distribution
- **Infrastructure**: 5,496 LOC (26 files) - Database, refresh connectors
- **Data Layer**: 8,039 LOC (21 files) - Data loading, enrichment
- **Analytics**: 3,713 LOC (21 files) - Scoring, signals
- **API**: 3,726 LOC (24 files) - Endpoints, schemas
- **Agents**: 2,595 LOC (10 files) - Orchestration
- **Exporters**: 2,490 LOC (6 files) - Reports
- **Research**: 3,400 LOC (11 files) - Pipeline
- **Others**: 2,600 LOC (42 files) - Utils, config, core

---

## 🚀 EXECUTION STRATEGY

### Phase 1: Wave 1 - Foundation (21 hours)
**Timeline**: Day 1-2  
**Parallelization**: 6 agents max  
**Coverage Gain**: +17 pp (56% → 73%)  
**Critical Path**: Database layer (6 hours)

**Tasks**: 20 total
- Batch 1A: Refresh Connectors (6 tasks, 4 hours) - github, yahoo_finance, sec_edgar, companies_house, news, news_signal
- Batch 1B: Refresh Connectors (6 tasks, 4 hours) - funding, patents, website, linkedin, global_market, web_search
- Batch 1C: Database Layer (4 tasks, 6 hours) - database.py, database_service.py, repositories.py
- Batch 1D: Conflict Resolution & Middleware (4 tasks, 5 hours) - conflict_resolution, reconcile_runs, middleware, routes

**Agent Profile**: 6x quick (connectors), 1x ultrabrain (database)

---

### Phase 2: Wave 2 - Core Logic (27 hours)
**Timeline**: Day 2-3 (concurrent if large team)  
**Parallelization**: 8 agents (analytics + data in parallel)  
**Coverage Gain**: +17 pp (73% → 90%)

**Subwave 2A: Analytics (13 hours)**
- Batch 1: Scoring (confidence_integration, growth_momentum, competitive_position) - 4 hours
- Batch 2: Filters & Signals (filters_llm, signals_extractors, signals_filters_suite) - 6 hours
- Batch 3: Support (workflows, simulation_market) - 3 hours

**Subwave 2B: Data Layer (14 hours)**
- Batch 1: Loading (additional_sources, enrichment_orchestrator, lookup_service, markets) - 8 hours
- Batch 2: Connectors (sec_edgar, companies_house, news_signal, news, funding, patents) - 6 hours

**Agent Profile**: 4x deep (analytics), 4x quick (data layer)

---

### Phase 3: Wave 3 - Integration (29 hours)
**Timeline**: Day 3-4  
**Parallelization**: 8 agents (API + research in parallel)  
**Coverage Gain**: +15 pp (90% → 94-95%)

**Subwave 3A: API Layer (11 hours)**
- Batch 1: Routers (async_jobs, market, jobs, drill_down) - 5 hours
- Batch 2: Services (enrichment_service, drill_down_service, dependencies) - 4 hours
- Batch 3: Main & Middleware (main.py, middleware_errors, exception_handlers) - 2 hours

**Subwave 3B: Research & Agents (18 hours)**
- Batch 1: Pipeline (discover → gather → pipeline → signals) - 8 hours (sequential)
- Batch 2: Agents (github_agent, companies_house_agent, additional_agents, resilience) - 6 hours
- Batch 3: Support (aggregate, evidence, narrative) - 4 hours

**Agent Profile**: 3x deep (API), 2x ultrabrain (research), 3x quick (agents)

---

### Phase 4: Wave 4 - Reporting & Support (18 hours)
**Timeline**: Day 4-5  
**Parallelization**: 6-8 agents (exporters + utilities in parallel)  
**Coverage Gain**: +8 pp (94-95% → 80%+)

**Subwave 4A: Exporters (11 hours)**
- Batch 1: Exporters (excel, audit_report, markdown_generator, llm) - 6 hours
- Batch 2: Presentation (adaptive_templates, narrative_consistency, data_quality) - 3 hours
- Batch 3: Extractors (markdown_extractor, application_* support) - 2 hours

**Subwave 4B: Utilities (7 hours)**
- Batch 1: Configuration (celery_config, config_validation, supabase_client, cli) - 3 hours
- Batch 2: Monitoring (logging, monitoring, production_hardening) - 3 hours
- Batch 3: Misc (constants, exceptions, worker, other) - 1 hour

**Agent Profile**: 4x quick (exporters), 3x quick (utilities), 1x deep (complex modules)

---

### Phase 5: Final Verification (4 hours)
**Timeline**: Day 5  
**Parallelization**: 1 agent (sequential verification)  
**Coverage Gain**: None (verification only)

**Tasks**:
- Run full test suite (30 min)
- Generate coverage report (15 min)
- Verify coverage ≥ 80% (15 min)
- Fix any regressions (1.5 hours)
- Review & cleanup (30 min)

**Agent Profile**: 1x oracle (final review)

---

## 📋 COMPLETE TASK LIST

### WAVE 1: FOUNDATION LAYER (20 tasks, 21 hours, +17 pp)

**BATCH 1A: REFRESH CONNECTORS (Part 1)**


- [ ] **1.1.1** Test GitHubRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/github_refresh.py (221 LOC)
  - **What**: Async connector testing with mock GitHubConnector
  - **Acceptance**: test_github_refresh.py passes, ≥85% coverage
  - **QA**: Scenario 1 (init), Scenario 2 (fetch success), Scenario 3 (error), Scenario 4 (delta)
  - **Agent**: quick | **Parallel**: Batch 1A

- [ ] **1.1.2** Test YahooFinanceRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/yahoo_finance_refresh.py (191 LOC)
  - **Complexity**: Simple | **Pattern**: Refresh Connector Template
  - **Agent**: quick | **Parallel**: Batch 1A

- [ ] **1.1.3** Test SecEdgarRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/sec_edgar_refresh.py (206 LOC)
  - **Complexity**: Simple | **Pattern**: Refresh Connector Template
  - **Agent**: quick | **Parallel**: Batch 1A

- [ ] **1.1.4** Test CompaniesHouseRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/companies_house_refresh.py (169 LOC)
  - **Complexity**: Simple | **Pattern**: Refresh Connector Template
  - **Agent**: quick | **Parallel**: Batch 1A

- [ ] **1.1.5** Test NewsRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/news_refresh.py (145 LOC)
  - **Complexity**: Simple | **Pattern**: Refresh Connector Template
  - **Agent**: quick | **Parallel**: Batch 1A

- [ ] **1.1.6** Test NewsSignalRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/news_signal_refresh.py (148 LOC)
  - **Complexity**: Simple | **Pattern**: Refresh Connector Template
  - **Agent**: quick | **Parallel**: Batch 1A

**BATCH 1B: REFRESH CONNECTORS (Part 2)**

- [ ] **1.1.7** Test FundingRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/funding_refresh.py (144 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

- [ ] **1.1.8** Test PatentsRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/patents_refresh.py (133 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

- [ ] **1.1.9** Test WebsiteRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/website_refresh.py (148 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

- [ ] **1.1.10** Test LinkedinRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/linkedin_refresh.py (124 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

- [ ] **1.1.11** Test GlobalMarketRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/global_market_refresh.py (128 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

- [ ] **1.1.12** Test WebSearchRefreshConnector (40 min, +1 pp)
  - **File**: src/solstein/infrastructure/connectors/web_search_refresh.py (102 LOC)
  - **Agent**: quick | **Parallel**: Batch 1B

**BATCH 1C: DATABASE LAYER (Sequential)**

- [ ] **1.2.1** Test database.py (1 hour, +1 pp)
  - **File**: src/solstein/infrastructure/database.py (137 LOC)
  - **What**: Database connection management, session creation
  - **Pattern**: Database/Repository Testing Template
  - **Acceptance**: test_database.py passes, ≥90% coverage
  - **Dependencies**: None
  - **Agent**: ultrabrain | **Sequential**

- [ ] **1.2.2** Test database_service.py (1.5 hours, +1 pp)
  - **File**: src/solstein/infrastructure/database_service.py (180 LOC)
  - **What**: CRUD operations, transactions, async session management
  - **Dependencies**: 1.2.1 (needs database.py tested)
  - **Agent**: ultrabrain | **Sequential**

- [ ] **1.2.3** Test repositories.py (2 hours, +2 pp)
  - **File**: src/solstein/infrastructure/repositories.py (303 LOC)
  - **What**: Abstract repository pattern, specialized queries
  - **Dependencies**: 1.2.2 (needs database_service.py tested)
  - **Agent**: ultrabrain | **Sequential**

- [ ] **1.2.4** Test enrichment_repositories.py (1.5 hours, +1 pp)
  - **File**: src/solstein/infrastructure/enrichment_repositories.py (215 LOC)
  - **What**: Specialized enrichment data repositories
  - **Dependencies**: 1.2.3 (needs repositories.py tested)
  - **Agent**: ultrabrain | **Sequential**

**BATCH 1D: CONFLICT RESOLUTION & MIDDLEWARE**

- [ ] **1.3.1** Test conflict_resolution.py (2 hours, +1 pp)
  - **File**: src/solstein/infrastructure/conflict_resolution.py (307 LOC)
  - **What**: Source authority, fact merging, conflict detection
  - **Pattern**: Analytics/Scoring Testing Template
  - **Agent**: deep | **Parallel**: Batch 1D

- [ ] **1.4.1** Test middleware_logging.py (1 hour, +1 pp)
  - **File**: api/middleware_logging.py (120 LOC)
  - **What**: Request/response logging middleware
  - **Pattern**: API Endpoint Testing Template
  - **Agent**: quick | **Parallel**: Batch 1D

- [ ] **1.4.2** Test middleware_security.py (45 min, +1 pp)
  - **File**: api/middleware_security.py (95 LOC)
  - **Pattern**: API Endpoint Testing Template
  - **Agent**: quick | **Parallel**: Batch 1D

- [ ] **1.3.2** Test reconcile_runs.py (2 hours, +1 pp)
  - **File**: src/solstein/infrastructure/reconcile_runs.py (305 LOC)
  - **What**: Pipeline reconciliation logic
  - **Dependencies**: 1.3.1 (conflict_resolution)
  - **Agent**: deep | **Sequential after 1.3.1**

- [ ] **1.4.3** Test routes_refresh.py (1 hour, +1 pp)
  - **File**: api/routes/refresh.py (150 LOC)
  - **What**: Refresh endpoints for data connectors
  - **Dependencies**: 1.1.1-1.1.12 (refresh connectors)
  - **Pattern**: API Endpoint Testing Template
  - **Agent**: quick

---

## 🔄 WAVE 2: CORE LOGIC LAYER (16 tasks, 27 hours, +17 pp)

[Tasks 2.1.1 - 2.3.2 detailed task list would follow same pattern]

---

## 🔗 WAVE 3: INTEGRATION LAYER (22 tasks, 29 hours, +15 pp)

[Tasks 3.1.1 - 5.3.3 detailed task list would follow]

---

## 📤 WAVE 4: REPORTING & SUPPORT (17 tasks, 18 hours, +8 pp)

[Tasks 6.1.1 - 7.3.4 detailed task list would follow]

---

## ✅ WAVE 5: FINAL VERIFICATION (1 task, 4 hours)

- [ ] **FINAL.1** Full Verification & Cleanup (4 hours)
  - Run pytest full suite: `pytest tests/ -v`
  - Generate coverage: `pytest --cov=src/solstein --cov-report=term-missing --cov-report=html`
  - Verify: Coverage ≥ 80%
  - Fix regressions if needed
  - Commit: "chore: complete test coverage implementation"
  - **Agent**: oracle

---

## 📊 COVERAGE PROJECTION

| Wave | Tasks | Hours | Coverage Gain | Total Coverage |
|------|-------|-------|---------------|-----------------|
| 1    | 20    | 21    | +17 pp        | 56% → 73%       |
| 2    | 16    | 27    | +17 pp        | 73% → 90%       |
| 3    | 22    | 29    | +15 pp        | 90% → 94-95%    |
| 4    | 17    | 18    | +8 pp         | 94% → 80%+      |
| 5    | 1     | 4     | —             | Verification    |
| **TOTAL** | **82** | **95** | **+60 pp** | **56% → 80%+** |

---

## ⏱️ TIMELINE ESTIMATES

### Full-Time (5 agents, continuous)
- **Wave 1**: 2 days (Day 1-2)
- **Wave 2**: 2 days (Day 2-3, parallel with Wave 1 database)
- **Wave 3**: 2 days (Day 3-4, parallel waves)
- **Wave 4**: 2 days (Day 4-5, parallel waves)
- **Wave 5**: 1 day (Day 5, verification)
- **Total**: 6-7 days elapsed time

### Part-Time (2 agents, 4 hours/day)
- **Wave 1**: 5-6 days (21 hours ÷ 4 hours/day)
- **Wave 2**: 6-7 days (27 hours ÷ 4 hours/day)
- **Wave 3**: 7-8 days (29 hours ÷ 4 hours/day)
- **Wave 4**: 4-5 days (18 hours ÷ 4 hours/day)
- **Wave 5**: 1 day (4 hours ÷ 4 hours/day)
- **Total**: 3-4 weeks elapsed time

### Solo (1 agent, 8 hours/day)
- **Total**: 12 days of full-time work → ~2 weeks calendar time

---

## 🛡️ RISK MITIGATION SUMMARY

**Critical Risks (Block Plan)**:
- Async/pytest configuration → FIX: Add asyncio_mode="auto" to pyproject.toml
- Mock/patch incompatibilities → FIX: Use AsyncMock templates from conftest.py
- Coverage regression → FIX: Re-run baseline before each wave

**High Risks (Slow Progress)**:
- Fixture brittleness → MITIGATION: Factory fixtures instead of hardcoded data
- Database isolation → MITIGATION: AsyncMock isolation per test
- Connector mocking gaps → MITIGATION: Complete mock matching real interface

**Contingencies**:
- IF team smaller: Prioritize Waves 1-2 for 80% coverage, skip optional tasks
- IF blocker found: Follow escalation path (fix → workaround → alternative)
- IF tests fail: Use git bisect to identify cause, revert & fix
- IF quality issues: Implement peer review gates before continuing

---

## 🎯 SUCCESS CRITERIA

### Acceptance
- [ ] Coverage ≥ 80% (verified by pytest --cov)
- [ ] All 82 tasks completed
- [ ] All tests pass (pytest tests/ -v)
- [ ] No regressions from baseline
- [ ] Documented risks & mitigations

### Quality Gates
- [ ] No test dependencies (each test independent)
- [ ] No flaky tests (consistent pass/fail)
- [ ] Clear test names (intent obvious)
- [ ] Proper error handling tested
- [ ] Edge cases covered

---

## 📚 SUPPORTING DOCUMENTS

- **Cycle 1 Draft**: `.sisyphus/drafts/planning-cycle-1-assessment.md` (current state analysis)
- **Cycle 2 Draft**: `.sisyphus/drafts/planning-cycle-2-task-breakdown.md` (82 tasks detailed)
- **Cycle 3 Draft**: `.sisyphus/drafts/planning-cycle-3-execution-waves.md` (parallelization strategy)
- **Cycle 4 Draft**: `.sisyphus/drafts/planning-cycle-4-acceptance-qa.md` (QA templates & scenarios)
- **Cycle 5 Draft**: `.sisyphus/drafts/planning-cycle-5-risk-mitigation.md` (risks & contingencies)

---

## 🚀 HOW TO USE THIS PLAN

### For Executors (Agents)
1. Read this plan summary
2. Start with Wave 1, Batch 1A
3. Use QA scenario templates from Cycle 4 draft
4. Use acceptance criteria as pass/fail definition
5. Collect evidence to .sisyphus/evidence/task-N-*.txt
6. Move to next task after passing

### For Project Leads
1. Monitor progress against timeline
2. Check coverage after each wave
3. Apply risk mitigations proactively
4. Run mid-wave checkpoints (every 4 hours)
5. Enforce quality gates before next wave

### For Future Reference
- This plan is complete and executed 5 planning cycles
- All tasks are concrete, not abstract
- All QA scenarios are agent-executable
- Risk mitigation is built-in
- Timeline is realistic with parallelization
- Quality is non-negotiable

---

## ✨ FINAL NOTES

**This is a comprehensive, battle-hardened plan** created through 5 iterative planning cycles:
1. **Cycle 1**: Current state deep assessment
2. **Cycle 2**: Comprehensive task breakdown
3. **Cycle 3**: Parallelization & execution strategy
4. **Cycle 4**: Acceptance criteria & QA scenarios (no ambiguity)
5. **Cycle 5**: Risk mitigation & contingencies (bulletproof)

**Zero Ambiguity**: Every task specifies exactly what to do and how to verify it.  
**Parallelizable**: 5-8 agents can work in parallel per wave.  
**Recoverable**: Built-in contingency plans for common blockers.  
**Realistic**: Timeline estimates account for async testing complexity.  

**Ready to execute.** 🚀

