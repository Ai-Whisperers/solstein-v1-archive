# Planning Cycle 1: Deep Current State Assessment

**Date**: Feb 26, 2026  
**Status**: IN PROGRESS  
**Agent**: Prometheus (Plan Builder)

---

## Current Project Metrics

### Code Inventory
- **Total Files**: 177 Python files
- **Total Lines**: 37,658 LOC
- **Coverage**: ~56% (from previous session, needs re-verification)
- **Test Files**: Unknown (being analyzed)

### Module Distribution (by size)

| Category | Files | Lines | Purpose | Priority |
|----------|-------|-------|---------|----------|
| **DATA** | 21 | 8,039 | Data loading, enrichment orchestration | HIGH (complex logic) |
| **INFRASTRUCTURE** | 26 | 5,496 | Database, conflict resolution, repositories | HIGH (critical) |
| **API** | 24 | 3,726 | FastAPI routers, schemas, endpoints | HIGH (public contract) |
| **ANALYTICS** | 21 | 3,713 | Scoring, signals, filters | HIGH (core logic) |
| **RESEARCH** | 11 | 3,400 | Discovery, gathering, pipeline | HIGH (business logic) |
| **EXPORTERS** | 6 | 2,490 | Markdown, Excel, audit reports | MEDIUM (reporting) |
| **ADAPTERS** | 25 | 2,496 | Enrichment adapters (funding, news, patents) | MEDIUM (data sources) |
| **AGENTS** | 10 | 2,595 | Coordinator, GitHub, Companies House | MEDIUM (orchestration) |
| **WORKER_TASKS** | 1 | 903 | Celery background tasks | MEDIUM (async) |
| **CLI** | 1 | 406 | Command-line interface | LOW (ops) |
| **CONFIG** | 1 | 366 | Configuration management | LOW (infra) |
| **CORE** | 5 | 947 | Monitoring, hardening, repositories | MEDIUM (support) |
| **DOMAIN** | 4 | 1,065 | Models, facts, validators, simulation | HIGH (contracts) |
| **Others** | 7 | 417 | Utils, exceptions, worker, constants | LOW (support) |

**Total**: 177 files, 37,658 LOC

---

## Testing Infrastructure Assessment

### Current Status
- **Test Directories**: 3 (unit, integration, data_quality)
- **Estimated Test Files**: ~69 (from earlier grep)
- **Known Test Patterns**:
  - ✅ Unit tests exist for: adapters, analytics, workers
  - ✅ pytest-asyncio available (installed in this session)
  - ✅ pytest.ini_options configured
  - ❓ Coverage configuration needs asyncio_mode = "auto"

### Issues Identified
- ⚠️ Test collection error: test_database_persistence.py (pytest_asyncio was missing, now fixed)
- ⚠️ pytest configuration missing `asyncio_mode = "auto"` setting
- ⚠️ Need to verify full test suite runs without errors

---

## Coverage Gap Analysis (Preliminary)

### High-Value Testing Targets (estimated 15-20 pp gain)
1. **INFRASTRUCTURE modules** (5,496 LOC)
   - refresh.py (base class, untested)
   - refresh connectors (12 x 100-150 lines each = 1,668 LOC untested)
   - database.py, database_service.py
   - repositories.py, enrichment_repositories.py
   - retry_policy.py, outbox_worker.py
   - Estimated gain: +8 pp

2. **DATA modules** (8,039 LOC)
   - company_loader.py, activities.py, workflows.py (analytics utils)
   - data/connectors/* (if untested)
   - Estimated gain: +3 pp

3. **RESEARCH modules** (3,400 LOC)
   - discover.py, gather.py (if untested)
   - pipeline.py integration
   - Estimated gain: +3 pp

### Medium-Value Testing Targets (estimated 10-15 pp gain)
4. **ANALYTICS confidence/signals** (confidence_weighting, confidence_integration, completeness)
5. **CORE modules** (monitoring, production_hardening)
6. **EXPORTERS** (if untested)
7. **Full AGENTS module** (if gaps exist)

### Low-Value Testing Targets (estimated 3-5 pp gain)
8. CLI, Config, Monitoring, Utils

---

## Architectural Patterns Observed

### Layered Architecture
```
┌─ API Layer (FastAPI routers + schemas)
├─ Application/Service Layer (agent coordination, business logic)
├─ Analytics Layer (scoring, signals, filters, valuation)
├─ Data Layer (loaders, enrichment orchestration, connectors)
├─ Infrastructure Layer (database, repositories, refresh connectors)
├─ Domain Layer (models, facts, validators)
└─ Support Layer (utils, monitoring, exceptions)
```

### Key Patterns to Maintain in Tests
1. **Dependency Injection**: DatabaseManager, mock connectors
2. **Async/Await**: Celery workers, FastAPI endpoints, refresh connectors
3. **Repository Pattern**: Abstraction over database operations
4. **Adapter Pattern**: Multiple enrichment sources (funding, news, patents, etc.)
5. **Factory Pattern**: Connector initialization

---

## Questions for Refinement

### Scope & Priorities
- [ ] Should we aim for 80%, 85%, or 90% coverage?
- [ ] Are there modules that should explicitly EXCLUDE from coverage (e.g., dev-only utilities)?
- [ ] Should we prioritize test coverage or documentation first?

### Technical Constraints
- [ ] What's the async/await testing pattern preference (AsyncMock vs pytest-asyncio)?
- [ ] Should integration tests use real database or mocks?
- [ ] Are there external APIs that need mocking (GitHub, CompaniesHouse, etc.)?

### Timeline & Resources
- [ ] Is this a sprint (2 weeks, full-time) or continuous (4 hours/week)?
- [ ] Should coverage work happen before or alongside documentation?
- [ ] Are there blocking dependencies (e.g., must fix pytest config first)?

---

## Next: Cycle 2 Preparation

**Inputs Awaiting**:
- [ ] Agent bg_ed02fd5c: Detailed module analysis
- [ ] Agent bg_04f152f4: Coverage optimization strategies
- [ ] Agent bg_4ca7daf9: Documentation best practices (ERROR - will retry)

**Actions in Cycle 2**:
1. Incorporate agent findings
2. Create comprehensive task breakdown (50+ tasks)
3. Prioritize by coverage impact
4. Identify quick wins vs long-term work
5. Draft initial execution phases

---

## Constraints & Guardrails (Learned from Phase 1-3)

From previous successful work:
1. ✅ All Pydantic models must use V2 (no deprecation warnings)
2. ✅ Test fixtures must use relative imports in conftest.py
3. ✅ Celery mocking pattern: `sys.modules['celery'] = MagicMock()` works well
4. ✅ `@mock_shared_task` decorator for task testing
5. ✅ Worker tests need specific exception handling patterns
6. ✅ Async tests need proper AsyncMock + fixture setup
7. ✅ Enrichment adapters have consistent interface (source_name, source_type, enrich())
8. ✅ Test data must match loader expectations exactly (JSON format, field names, types)

---

## Success Metrics for Complete Plan

The final plan must include:
- [ ] Clear task breakdown (50-100+ tasks)
- [ ] Parallel execution waves (4-6 waves)
- [ ] Coverage gain estimates per task
- [ ] QA scenarios (not just assertions)
- [ ] Risk mitigation strategies
- [ ] Rollback/contingency plans
- [ ] Acceptance criteria per task
- [ ] Evidence collection strategy
- [ ] Dependency matrix
- [ ] Timeline estimates (hours per task)

