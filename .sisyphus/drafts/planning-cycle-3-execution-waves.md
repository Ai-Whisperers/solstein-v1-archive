# Planning Cycle 3: Parallelization Strategy & Execution Waves

**Date**: Feb 26, 2026  
**Status**: IN PROGRESS  
**Agent**: Prometheus (Plan Builder)

---

## Execution Wave Strategy

**Goal**: Maximize parallel work while respecting dependencies. Target 5-8 agents working in parallel per wave.

**Wave Structure**:
- **Wave 1**: Foundation (Infrastructure) - NO DEPENDENCIES
- **Wave 2**: Core Logic (Analytics + Data) - Depends on Wave 1, CAN RUN IN PARALLEL
- **Wave 3**: Integration (API + Research) - Depends on Waves 1-2, CAN RUN IN PARALLEL
- **Wave 4**: Reporting & Support (Exporters + Utilities) - Depends on Waves 1-3, CAN RUN IN PARALLEL
- **Final**: Verification & Cleanup - ALL PREVIOUS WAVES COMPLETE

---

## WAVE 1: FOUNDATION LAYER (21 hours, 20 tasks)

**Timeline**: Day 1-2 (1 agent full-time or 5 agents part-time)  
**Parallelization**: 5 tasks in parallel, 4 sequential batches  
**Coverage Gain**: +17 pp (56% → 73%)

### Batch 1A: Refresh Connectors (Part 1 of 3)
**Duration**: 4 hours | **Parallel**: 6 tasks | **Coverage**: +4 pp

```
Task 1.1.1: github_refresh.py (40 min)
Task 1.1.2: yahoo_finance_refresh.py (40 min)
Task 1.1.3: sec_edgar_refresh.py (40 min)
Task 1.1.4: companies_house_refresh.py (40 min)
Task 1.1.5: news_refresh.py (40 min)
Task 1.1.6: news_signal_refresh.py (40 min)
```

**Agent Profile**: 6x `quick` (pattern-based)  
**Execution**: Sequential or parallel (independent modules)

### Batch 1B: Refresh Connectors (Part 2 of 3)
**Duration**: 4 hours | **Parallel**: 6 tasks | **Coverage**: +4 pp

```
Task 1.1.7: funding_refresh.py (40 min)
Task 1.1.8: patents_refresh.py (40 min)
Task 1.1.9: website_refresh.py (40 min)
Task 1.1.10: linkedin_refresh.py (40 min)
Task 1.1.11: global_market_refresh.py (40 min)
Task 1.1.12: web_search_refresh.py (40 min)
```

**Agent Profile**: 6x `quick`  
**Execution**: Parallel (same pattern as Batch 1A)

### Batch 1C: Database Layer
**Duration**: 6 hours | **Sequential**: 4 tasks | **Coverage**: +4 pp

```
Task 1.2.1: database.py (1 hour)
  → Task 1.2.2: database_service.py (1.5 hours) [depends on 1.2.1]
  → Task 1.2.3: repositories.py (2 hours) [depends on 1.2.2]
  → Task 1.2.4: enrichment_repositories.py (1.5 hours) [depends on 1.2.3]
```

**Agent Profile**: 1x `ultrabrain` (foundation, critical logic)  
**Execution**: Sequential (dependencies)

### Batch 1D: Conflict Resolution & Middleware
**Duration**: 5 hours | **Parallel**: 3 tasks (2 parallel, 1 sequential) | **Coverage**: +3 pp

```
Task 1.3.1: conflict_resolution.py (2 hours)
Task 1.4.1: middleware_logging.py (1 hour) [parallel with 1.3.1]
Task 1.4.2: middleware_security.py (45 min) [parallel with 1.3.1]
  → Task 1.3.2: reconcile_runs.py (2 hours) [depends on 1.3.1]
  → Task 1.4.3: routes_refresh.py (1 hour) [depends on 1.4.1, 1.4.2]
```

**Agent Profile**: 1x `deep`, 2x `quick`  
**Execution**: Mixed (parallel + sequential)

### Wave 1 Summary
- **Total Hours**: 21 hours
- **Coverage Gain**: +17 pp
- **Parallel Capacity**: 6 agents max
- **Sequential Bottleneck**: Database layer (6 hours critical path)
- **Earliest Completion**: 6 hours (with 6-person team)

---

## WAVE 2: CORE LOGIC LAYER (27 hours, 16 tasks)

**Timeline**: Day 2-3 (concurrent with Wave 1 Batch 1C if using large team)  
**Depends On**: Wave 1 complete  
**Parallelization**: 2 subwaves (Analytics & Data) in parallel  
**Coverage Gain**: +17 pp (73% → 90%)

### Subwave 2A: ANALYTICS (13 hours, 8 tasks)
**Duration**: 13 hours | **Parallel**: 3 tasks per batch | **Coverage**: +9 pp

#### Analytics Batch 1: Scoring
**Duration**: 4 hours | **Parallel**: 3 tasks

```
Task 2.1.1: confidence_integration.py (1.5 hours)
Task 2.1.2: growth_momentum.py (1 hour)
Task 2.1.3: competitive_position.py (1.5 hours)
```

**Agent Profile**: 3x `deep` (complex scoring logic)  
**Dependencies**: Wave 1 (database infrastructure)

#### Analytics Batch 2: Filters & Signals
**Duration**: 6 hours | **Parallel**: 3 tasks

```
Task 2.2.1: filters_llm.py (2 hours)
Task 2.2.2: signals_extractors.py (1.5 hours)
Task 2.2.3: signals_filters_suite.py (2.5 hours)
```

**Agent Profile**: 1x `ultrabrain`, 2x `deep`  
**Execution**: Parallel (independent modules)

#### Analytics Batch 3: Support
**Duration**: 3 hours | **Sequential**: 2 tasks

```
Task 2.3.1: workflows.py (1.5 hours)
Task 2.3.2: simulation_market.py (1.5 hours)
```

**Agent Profile**: 2x `deep`

---

### Subwave 2B: DATA LAYER (14 hours, 10 tasks)
**Duration**: 14 hours | **Parallel**: 4 tasks per batch | **Coverage**: +8 pp

#### Data Batch 1: Loading
**Duration**: 8 hours | **Parallel**: 4 tasks

```
Task 3.1.1: additional_sources.py (2.5 hours)
Task 3.1.2: enrichment_orchestrator.py (2 hours)
Task 3.1.3: connectors_lookup_service.py (1 hour)
Task 3.1.4: markets.py (2 hours)
```

**Agent Profile**: 1x `ultrabrain`, 2x `deep`, 1x `quick`  
**Execution**: Parallel (independent modules)

#### Data Batch 2: Connectors
**Duration**: 6 hours | **Parallel**: 6 tasks (or 3 sequential pairs)

```
Task 3.2.1: sec_edgar_connector.py (1.5 hours)
Task 3.2.2: companies_house_connector.py (1 hour)
Task 3.2.3: news_signal_detector.py (1.5 hours)
Task 3.2.4: news_connector.py (1 hour) [parallel with previous]
Task 3.2.5: funding_connector.py (1 hour)
Task 3.2.6: patents_connector.py (1 hour)
```

**Agent Profile**: 6x `quick` (pattern-based connectors)  
**Execution**: Parallel

---

### Wave 2 Summary
- **Total Hours**: 27 hours
- **Coverage Gain**: +17 pp (73% → 90%)
- **Parallel Capacity**: 8 agents (4 analytics + 4 data)
- **Critical Path**: 14 hours (Data layer slightly longer)
- **Earliest Completion**: 14 hours (with 4-person team)

---

## WAVE 3: INTEGRATION LAYER (29 hours, 22 tasks)

**Timeline**: Day 3-4  
**Depends On**: Waves 1-2 complete  
**Parallelization**: 2 subwaves (API & Research) in parallel  
**Coverage Gain**: +15 pp (90% → 94-95%)

### Subwave 3A: API LAYER (11 hours, 10 tasks)
**Duration**: 11 hours | **Parallel**: 3-4 tasks per batch

#### API Batch 1: Routers
**Duration**: 5 hours | **Parallel**: 4 tasks

```
Task 4.1.1: async_jobs.py (1.5 hours)
Task 4.1.2: market.py (1 hour)
Task 4.1.3: jobs.py (1 hour)
Task 4.1.4: drill_down.py (1 hour)
```

**Agent Profile**: 2x `deep`, 2x `quick`  
**Execution**: Parallel (independent endpoints)

#### API Batch 2: Services
**Duration**: 4 hours | **Sequential**: 3 tasks

```
Task 4.2.1: enrichment_service.py (1.5 hours)
Task 4.2.2: drill_down_service.py (1 hour)
Task 4.2.3: dependencies.py (1.5 hours)
```

**Agent Profile**: 1x `deep`  
**Execution**: Sequential (services may have interdependencies)

#### API Batch 3: Main & Middleware
**Duration**: 2 hours | **Parallel**: 3 tasks

```
Task 4.3.1: main.py (1 hour)
Task 4.3.2: middleware_errors.py (45 min)
Task 4.3.3: exception_handlers.py (15 min)
```

**Agent Profile**: 1x `quick`, 1x `quick`

---

### Subwave 3B: RESEARCH & AGENTS (18 hours, 12 tasks)
**Duration**: 18 hours | **Parallel**: 3-4 tasks per batch

#### Research Batch 1: Pipeline
**Duration**: 8 hours | **Sequential**: 4 tasks (linear dependency)

```
Task 5.1.1: discover.py (2.5 hours)
  → Task 5.1.2: gather.py (2.5 hours) [depends on discover]
  → Task 5.1.3: pipeline.py (2 hours) [depends on gather]
  → Task 5.1.4: signals.py (1 hour) [depends on pipeline]
```

**Agent Profile**: 1x `ultrabrain`  
**Execution**: Sequential (discovery → gathering → pipeline → signals)

#### Research Batch 2: Agents
**Duration**: 6 hours | **Parallel**: 4 tasks

```
Task 5.2.1: github_agent.py (2 hours)
Task 5.2.2: companies_house_agent.py (1.5 hours)
Task 5.2.3: additional_agents.py (1 hour)
Task 5.2.4: resilience_agent.py (1.5 hours)
```

**Agent Profile**: 2x `deep`, 2x `quick`  
**Execution**: Parallel (independent agents)

#### Research Batch 3: Support
**Duration**: 4 hours | **Parallel**: 3 tasks

```
Task 5.3.1: aggregate.py (2 hours)
Task 5.3.2: evidence.py (1 hour)
Task 5.3.3: narrative.py (1 hour)
```

**Agent Profile**: 1x `deep`, 2x `quick`  
**Execution**: Parallel

---

### Wave 3 Summary
- **Total Hours**: 29 hours
- **Coverage Gain**: +15 pp (90% → 94-95%)
- **Parallel Capacity**: 8 agents (4 API + 4 Research)
- **Critical Path**: 18 hours (Research pipeline is sequential)
- **Earliest Completion**: 18 hours (with large team)

---

## WAVE 4: REPORTING & SUPPORT LAYER (18 hours, 17 tasks)

**Timeline**: Day 4  
**Depends On**: Waves 1-3 complete  
**Parallelization**: 2 subwaves (Exporters & Utilities) in parallel  
**Coverage Gain**: +8 pp (94-95% → 80%+) *Note: utilities are low priority*

### Subwave 4A: EXPORTERS & PRESENTATION (11 hours, 7 tasks)
**Duration**: 11 hours | **Parallel**: 3-4 tasks per batch

#### Exporters Batch 1: Core Exporters
**Duration**: 6 hours | **Parallel**: 4 tasks

```
Task 6.1.1: excel.py (1.5 hours)
Task 6.1.2: audit_report.py (1.5 hours)
Task 6.1.3: markdown_generator.py (2 hours)
Task 6.1.4: llm.py (1 hour)
```

**Agent Profile**: 2x `deep`, 2x `quick`  
**Execution**: Parallel (independent exporters)

#### Exporters Batch 2: Presentation
**Duration**: 3 hours | **Parallel**: 3 tasks

```
Task 6.2.1: adaptive_templates.py (1.5 hours)
Task 6.2.2: narrative_consistency.py (1 hour)
Task 6.2.3: data_quality_indicators.py (30 min)
```

**Agent Profile**: 1x `deep`, 2x `quick`  
**Execution**: Parallel

#### Exporters Batch 3: Extractors
**Duration**: 2 hours | **Parallel**: 3 tasks

```
Task 6.3.1: markdown_extractor.py (1.5 hours)
Task 6.3.2: application_exporters.py (15 min)
Task 6.3.3: application_filters.py (15 min)
```

**Agent Profile**: 1x `quick`

---

### Subwave 4B: UTILITIES & SUPPORT (7 hours, 10 tasks)
**Duration**: 7 hours | **Parallel**: 3-5 tasks per batch

#### Utilities Batch 1: Configuration
**Duration**: 3 hours | **Parallel**: 4 tasks

```
Task 7.1.1: celery_config.py (45 min)
Task 7.1.2: config_validation.py (1 hour)
Task 7.1.3: core_supabase_client.py (15 min)
Task 7.1.4: cli_coverage.py (1 hour)
```

**Agent Profile**: 4x `quick`

#### Utilities Batch 2: Monitoring & Logging
**Duration**: 3 hours | **Parallel**: 3 tasks

```
Task 7.2.1: logging.py (30 min)
Task 7.2.2: monitoring.py (1.5 hours)
Task 7.2.3: production_hardening.py (1 hour)
```

**Agent Profile**: 1x `deep`, 2x `quick`

#### Utilities Batch 3: Miscellaneous
**Duration**: 1 hour | **Parallel**: 4 tasks

```
Task 7.3.1: constants.py (15 min)
Task 7.3.2: exceptions.py (10 min)
Task 7.3.3: worker.py (5 min)
Task 7.3.4: miscellaneous.py (20 min)
```

**Agent Profile**: 4x `quick`

---

### Wave 4 Summary
- **Total Hours**: 18 hours
- **Coverage Gain**: +8 pp
- **Parallel Capacity**: 6-8 agents
- **Critical Path**: 11 hours (Exporters)
- **Earliest Completion**: 11 hours

---

## WAVE 5: FINAL VERIFICATION & CLEANUP (4 hours)

**Timeline**: Day 5  
**Depends On**: All previous waves complete  
**Purpose**: Verify all tasks, run full test suite, generate coverage report

### Tasks:
```
Task F1.1: Run full test suite (pytest with coverage) [30 min]
Task F1.2: Generate coverage report (term + HTML) [15 min]
Task F1.3: Verify coverage ≥ 80% [15 min]
Task F1.4: Fix any failing tests [1.5 hours]
Task F1.5: Review acceptance criteria per task [1 hour]
Task F1.6: Final git cleanup & documentation [30 min]
```

**Agent Profile**: 1x `oracle` (verification)

---

## Complete Execution Timeline

### Full-Time (5 agents, 7 days)
```
Day 1:   Wave 1 Batches 1A-1B (Refresh Connectors, parallel)
Day 2:   Wave 1 Batch 1C-1D (Database & Middleware) + Wave 2A Start
Day 3:   Wave 2A-2B Complete (Analytics & Data, parallel)
Day 4:   Wave 3A-3B Complete (API & Research, parallel)
Day 5:   Wave 4A-4B Complete (Exporters & Utilities, parallel)
Day 6:   Wave 5 Verification & Cleanup
Day 7:   Buffer / Final QA
```

**Estimated Completion**: 6-7 days (full-time, 5 agents)  
**Estimated Completion**: 3-4 weeks (part-time, 1 agent)

### Parallel Team Deployment (Optimal)
```
Wave 1: 6 agents (refresh connectors run in parallel)
  → Stream A: Database layer (1 agent)
  → Stream B: Conflict resolution & middleware (3 agents)

Wave 2: 8 agents in parallel
  → Stream A: Analytics (3 agents, 13 hours)
  → Stream B: Data layer (5 agents, 14 hours)

Wave 3: 8 agents in parallel
  → Stream A: API (3 agents, 11 hours)
  → Stream B: Research (5 agents, 18 hours)

Wave 4: 6 agents in parallel
  → Stream A: Exporters (3 agents, 11 hours)
  → Stream B: Utilities (3 agents, 7 hours)

Wave 5: 1 agent (final verification)
```

**With 8-person team**: ~6-7 days elapsed time  
**With 5-person team**: ~10-12 days elapsed time  
**With 2-person team**: ~3-4 weeks elapsed time  
**With 1-person team**: ~6-8 weeks elapsed time

---

## Agent Role Assignments

### Recommended Agent Profiles per Task Type

| Task Type | Profile | Reason |
|-----------|---------|--------|
| Refresh Connectors | `quick` | Pattern-based, consistent interface |
| Database/ORM | `ultrabrain` | Critical foundation, complex state |
| Analytics/Scoring | `deep` | Complex math, traceability important |
| API Endpoints | `quick` or `deep` | Quick for CRUD, deep for complex logic |
| Research Pipeline | `ultrabrain` | Sequential dependencies, orchestration |
| Exporters | `quick` | Templated work |
| Utilities/Config | `quick` | Simple, straightforward |
| Verification | `oracle` | Final review, quality gates |

---

## Cycle 3 Conclusions

✅ **Execution waves defined**: 5 waves + final verification  
✅ **Parallelization mapped**: 6-8 agents can work in parallel per wave  
✅ **Timeline estimates**: 6-7 days (full-time team) to 6-8 weeks (solo)  
✅ **Dependency graph**: Clear sequential requirements identified  
✅ **Agent allocation**: Role assignments per task type  

**Coverage Projection**:
- Wave 1: 56% → 73% (+17 pp)
- Wave 2: 73% → 90% (+17 pp)  
- Wave 3: 90% → 94% (+4 pp)
- Wave 4: 94% → 97% (+3 pp)

**Target**: 80%+ achieved after Wave 2 (27 hours of work, Day 2-3)

---

## Next: Cycle 4 will add detailed acceptance criteria & QA scenarios per task

