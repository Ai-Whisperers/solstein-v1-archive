# EPIC-020: Folder Structure Reorganization

> **Status**: Proposed  
> **Priority**: P2 - High  
> **Effort**: 2-3 sprints  
> **Reporter**: AI Code Analysis  
> **Created**: 2026-03-06

---

## 1. Problem Statement

Code quality analysis has identified **5 directories** with organizational issues that violate the project's code quality standards:

| Severity | Directory | Files | Folders | Total | Issue |
|----------|-----------|-------|---------|-------|-------|
| 🔴 **CRITICAL** | `src/solstein/data` | 35 | 2 | 37 | Severely overcrowded - 2.3x over limit |
| 🟡 **WARNING** | `src/solstein/infrastructure` | 26 | 1 | 27 | 1.7x over limit |
| 🟡 **WARNING** | `src/solstein/analytics` | 17 | 5 | 22 | Approaching limit |
| 🟡 **WARNING** | `src/solstein/core` | 16 | 1 | 17 | Approaching limit |
| 🟡 **WARNING** | `src/solstein` (root) | 14 | 19 | 33 | Root module bloated |

**Impact:**
- Reduced developer velocity (cognitive load finding files)
- Increased merge conflicts (too many files in one location)
- Harder to maintain module boundaries
- Violates project's code quality guardrails

---

## 2. Current State Analysis

### 2.1 `src/solstein/data` (CRITICAL - 35 files)

**Current contents:**
```
base_fetcher.py, company_house.py, company_registry.py, cruchbase.py,
csv_fetcher.py, data_fetcher.py, data_quality.py, data_sources.py,
enrichment_cache.py, enrichment_data.py, enrichment_sources.py,
fetcher_factory.py, json_fetcher.py, loaders/, monitoring_fetcher.py,
pdl_fetcher.py, permid_fetcher.py, persistence.py, prefill_adapter.py,
redis_adapter.py, salesforce_fetcher.py, source_factory.py,
web_fetcher.py, web_scraper.py, web_search.py, yahoo_finance.py, ...
```

**Problems:**
- Mix of **fetchers** (11+), **adapters** (3+), and **loaders**
- No clear separation between data sources and data access patterns
- `connectors/` subdirectory exists but underutilized
- Test files mixed with source (`*_test.py` patterns)

### 2.2 `src/solstein/infrastructure` (WARNING - 26 files)

**Current contents:**
```
cache.py, celery_app.py, company_repository.py, connectors/,
database.py, database_models.py, enrichment_cache_repository.py,
enrichment_repositories.py, event_bus.py, event_store.py,
outbox_worker.py, repositories.py, ...
```

**Problems:**
- `connectors/` subdirectory has 11 files but flat structure persists at parent level
- Repository files scattered (company_repository.py, enrichment_repositories.py, repositories.py)
- Database-related files mixed with other infrastructure concerns

### 2.3 `src/solstein/analytics` (WARNING - 17 files, 5 folders)

**Current contents:**
```
competitive_analyzer.py, filters/, growth_calculator.py, market_analyzer.py,
position_analyzer.py, scoring_engine.py, scorers/, signals/, simulation/,
utils.py, valuation/
```

**Problems:**
- Actually well-organized with subdirectories
- Some files at root level could be moved into existing folders
- `utils.py` is a code smell (generic catch-all)

### 2.4 `src/solstein/core` (WARNING - 16 files, 1 folder)

**Current contents:**
```
base_adapter.py, base_fetcher.py, base_processor.py, base_scorer.py,
bootstrap.py, command_bus.py, entity.py, event.py, event_handler.py,
interfaces.py, pipeline.py, ports/, repository.py, unit_of_work.py,
value_object.py, workflow.py
```

**Problems:**
- `ports/` subdirectory exists but most files at root level
- Mix of base classes, interfaces, and workflow utilities
- Could benefit from clearer architectural layer separation

### 2.5 `src/solstein/` Root (WARNING - 14 files, 19 folders)

**Current contents:**
```
celery_config.py, cli.py, exceptions.py, worker.py, worker_tasks.py,
config/, adapters/, agents/, analytics/, api/, application/, core/,
data/, domain/, exporters/, extractors/, infrastructure/, llm/, ...
```

**Problems:**
- Celery/worker files at root could be consolidated
- `exceptions.py` and `cli.py` are fine at root but contribute to count
- 19 subdirectories make root module very large

---

## 3. Proposed Solution

### 3.1 Target Structure

**Thresholds (from CI/CD guardrails):**
- Max 15 files per directory
- Max 10 subdirectories per directory  
- Max 25 total items per directory

### 3.2 Reorganization Plan

#### Phase 1: `src/solstein/data` (Critical)

**New Structure:**
```
src/solstein/data/
├── fetchers/              # All fetcher implementations
│   ├── base.py           # base_fetcher.py
│   ├── company/          # company_house.py, company_registry.py
│   ├── enrichment/       # pdl_fetcher.py, permid_fetcher.py
│   ├── financial/        # yahoo_finance.py
│   ├── salesforce.py
│   └── web/              # web_fetcher.py, web_scraper.py, web_search.py
├── adapters/             # Data adapters
│   ├── base.py           # base_adapter.py, prefill_adapter.py
│   ├── cache.py          # enrichment_cache.py
│   └── persistence.py
├── loaders/              # Already exists - verify organization
├── connectors/           # Already exists - move relevant files
├── quality.py            # data_quality.py
├── sources.py            # data_sources.py, enrichment_sources.py
└── factory.py            # fetcher_factory.py, source_factory.py
```

**Files to move:** 20+ → Reduces root `data/` from 35 to ~10 files

#### Phase 2: `src/solstein/infrastructure`

**New Structure:**
```
src/solstein/infrastructure/
├── connectors/           # Expand existing (11 files)
│   └── __init__.py
├── database/             # New subdirectory
│   ├── __init__.py
│   ├── engine.py         # database.py
│   ├── models.py         # database_models.py
│   └── migrations/       # If needed
├── repositories/         # New subdirectory
│   ├── __init__.py
│   ├── company.py        # company_repository.py
│   ├── enrichment.py     # enrichment_repositories.py + enrichment_cache_repository.py
│   └── base.py           # repositories.py
├── cache.py              # Keep at root (core infrastructure)
├── event_bus.py
├── event_store.py
├── outbox_worker.py
└── celery_app.py
```

**Files to move:** 10+ → Reduces from 26 to ~12 files

#### Phase 3: `src/solstein/core`

**New Structure:**
```
src/solstein/core/
├── ports/                # Expand existing
│   ├── __init__.py
│   ├── repository.py
│   ├── unit_of_work.py
│   └── event_handler.py
├── base/                 # New subdirectory
│   ├── __init__.py
│   ├── adapter.py        # base_adapter.py
│   ├── fetcher.py        # base_fetcher.py
│   ├── processor.py      # base_processor.py
│   ├── scorer.py         # base_scorer.py
│   └── entity.py         # entity.py + value_object.py
├── workflow/             # New subdirectory
│   ├── __init__.py
│   ├── pipeline.py
│   └── workflow.py
├── bootstrap.py
├── command_bus.py
├── event.py
└── interfaces.py
```

**Files to move:** 8+ → Reduces from 16 to ~8 files

#### Phase 4: `src/solstein/analytics` (Minor cleanup)

**Changes:**
- Move `utils.py` contents into appropriate subdirectories
- Move root-level analyzer files into `analyzers/` subdirectory

#### Phase 5: `src/solstein/` Root cleanup

**Changes:**
- Create `tasks/` subdirectory for Celery/worker files:
  ```
  src/solstein/tasks/
  ├── __init__.py
  ├── celery_config.py
  ├── worker.py
  └── worker_tasks.py
  ```
- Keeps `cli.py` and `exceptions.py` at root (acceptable)

---

## 4. Implementation Stories

### Story 1: Create Data Fetchers Module
**Priority**: P0 | **Effort**: 3 points
- Create `data/fetchers/` package structure
- Move all fetcher implementations
- Update imports across codebase
- Add `__init__.py` with clean exports

### Story 2: Create Data Adapters Module  
**Priority**: P0 | **Effort**: 2 points
- Create `data/adapters/` package
- Move adapter implementations
- Update imports

### Story 3: Create Infrastructure Database Module
**Priority**: P0 | **Effort**: 2 points
- Create `infrastructure/database/` package
- Move database.py and database_models.py
- Update all model imports

### Story 4: Create Infrastructure Repositories Module
**Priority**: P0 | **Effort**: 2 points
- Create `infrastructure/repositories/` package
- Consolidate repository files
- Update service layer imports

### Story 5: Create Core Base Classes Module
**Priority**: P1 | **Effort**: 2 points
- Create `core/base/` package
- Move all base classes
- Update inheritance across codebase

### Story 6: Create Core Workflow Module
**Priority**: P1 | **Effort**: 1 point
- Create `core/workflow/` package
- Move pipeline and workflow files

### Story 7: Create Tasks Module
**Priority**: P1 | **Effort**: 2 points
- Create `tasks/` package at root
- Move Celery configuration and worker files
- Update entry points (CLI, docker-compose, etc.)

### Story 8: Analytics Utils Cleanup
**Priority**: P2 | **Effort**: 1 point
- Eliminate `analytics/utils.py` (split into appropriate modules)
- Move analyzers into `analytics/analyzers/`

### Story 9: Import Cleanup & Verification
**Priority**: P0 | **Effort**: 3 points
- Run import checker across all moved files
- Fix any broken imports
- Verify tests pass

### Story 10: Update Documentation
**Priority**: P1 | **Effort**: 1 point
- Update AGENTS.md with new structure
- Update architecture diagrams
- Update import examples in docs

---

## 5. Acceptance Criteria

- [ ] All directories have ≤15 files
- [ ] All directories have ≤10 subdirectories  
- [ ] All directories have ≤25 total items
- [ ] CI/CD `check_folder_structure.py` passes
- [ ] All tests pass
- [ ] No broken imports
- [ ] AGENTS.md updated with new structure

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import breakage | High | Use IDE refactoring tools; run full test suite |
| Circular imports | Medium | Move carefully; check dependency graph first |
| Merge conflicts | High | Coordinate with team; use short-lived branches |
| Breaking changes | Medium | This is internal reorg; no public API changes |

---

## 7. Dependencies

- **None** - This is a self-contained refactoring epic
- Can be done in parallel with feature work (different files)

---

## 8. Definition of Done

1. All 5 flagged directories restructured
2. CI/CD quality gate passes
3. Test suite green
4. Documentation updated
5. Team walkthrough completed

---

## 9. Appendix: File Inventory

### Data Module Files (35 total)
```
__init__.py
base_fetcher.py           → fetchers/base.py
company_house.py          → fetchers/company/company_house.py
company_registry.py       → fetchers/company/company_registry.py
cruchbase.py              → fetchers/company/crunchbase.py
csv_fetcher.py            → fetchers/file/csv_fetcher.py
data_fetcher.py           → fetchers/data_fetcher.py
data_quality.py           → quality.py
data_sources.py           → sources.py
enrichment_cache.py       → adapters/cache.py
enrichment_data.py        → (eliminate/consolidate)
enrichment_sources.py     → sources.py
fetcher_factory.py        → factory.py
json_fetcher.py           → fetchers/file/json_fetcher.py
loaders/                  (keep)
monitoring_fetcher.py     → fetchers/monitoring_fetcher.py
pdl_fetcher.py            → fetchers/enrichment/pdl_fetcher.py
permid_fetcher.py         → fetchers/enrichment/permid_fetcher.py
persistence.py            → adapters/persistence.py
prefill_adapter.py        → adapters/prefill.py
redis_adapter.py          → adapters/redis.py
salesforce_fetcher.py     → fetchers/salesforce_fetcher.py
source_factory.py         → factory.py
web_fetcher.py            → fetchers/web/web_fetcher.py
web_scraper.py            → fetchers/web/web_scraper.py
web_search.py             → fetchers/web/web_search.py
yahoo_finance.py          → fetchers/financial/yahoo_finance.py
```

### Infrastructure Module Files (26 total)
```
cache.py                  (keep)
celery_app.py             (keep - or move to tasks/)
company_repository.py     → repositories/company.py
connectors/               (expand)
database.py               → database/engine.py
database_models.py        → database/models.py
enrichment_cache_repository.py → repositories/enrichment.py
enrichment_repositories.py → repositories/enrichment.py
event_bus.py              (keep)
event_store.py            (keep)
outbox_worker.py          (keep)
repositories.py           → repositories/base.py
```

---

*Generated by folder structure analysis - 2026-03-06*
