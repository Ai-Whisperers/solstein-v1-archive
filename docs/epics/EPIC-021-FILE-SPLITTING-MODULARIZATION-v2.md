# Epic: File Splitting and Modularization (EPIC-021) - UPDATED v2.0

## Overview
Split 25 large files (>500 lines) into smaller, focused modules to improve maintainability, testability, and reduce merge conflicts.

**Status:** 🔄 Ready for Implementation  
**Dependencies:** EPIC-020 (COMPLETE), EPIC-019  
**Last Updated:** 2026-03-06

---

## Current State - UPDATED

### Before Any Work:
- ❌ 25 files exceed 500 lines
- ❌ 6 files exceed 1,000 lines (god files)
- ❌ Worst: `generator.py` at 1,403 lines

### After EPIC-020 (God Functions):
- ✅ **PARTIALLY COMPLETE:** 10 new helper modules created (2,825 lines total)
- ✅ **PARTIALLY COMPLETE:** `domain/models/` package structure created
- 🔄 **REMAINING:** 15 files still need splitting
- 🔄 **NEW ISSUE:** Some files may have grown due to imports

### Updated File Inventory:

| File | Lines | Status | EPIC-020 Impact |
|------|-------|--------|-----------------|
| `exporters/markdown/generator.py` | 1,403 | 🔴 NEEDS SPLIT | None |
| `data/unified_loader.py` | 1,066 | 🔴 NEEDS SPLIT | None |
| `data/loaders.py` | 939 | 🔴 NEEDS SPLIT | None |
| `worker_tasks.py` | 903 | 🔴 NEEDS SPLIT | None |
| `infrastructure/database_models.py` | 836 | 🔴 NEEDS SPLIT | None |
| `domain/models.py` | 818 | 🟡 PARTIALLY DONE | Package created |
| `api/routers/enrichment.py` | 802 | 🔴 NEEDS SPLIT | None |
| `agents/github_agent.py` | 777 | 🔴 NEEDS SPLIT | None |
| `data/additional_sources.py` | 769 | 🔴 NEEDS SPLIT | None |
| `llm/health_checker.py` | 704 | 🟡 PARTIALLY DONE | Strategies extracted |
| `research/aggregate.py` | 664 | 🔴 NEEDS SPLIT | None |
| `research/discovery.py` | 654 | 🟡 PARTIALLY DONE | Catalogs extracted |
| `research/gather.py` | 648 | 🔴 NEEDS SPLIT | None |
| `llm/enhanced_client.py` | 611 | 🟡 PARTIALLY DONE | Strategies extracted |
| `extractors/markdown_extractor.py` | 578 | 🔴 NEEDS SPLIT | None |
| `infrastructure/research_dual_write.py` | 572 | 🔴 NEEDS SPLIT | Helpers extracted |
| `exporters/excel_improved.py` | 562 | 🔴 NEEDS SPLIT | None |
| `api/schemas/enrichment.py` | 549 | 🔴 NEEDS SPLIT | None |
| `data/enrichment_orchestrator.py` | 547 | 🔴 NEEDS SPLIT | Executors extracted |
| `research/ai_research_orchestrator.py` | 543 | 🔴 NEEDS SPLIT | None |
| `research/pipeline.py` | 533 | 🟡 PARTIALLY DONE | Stages extracted |
| `core/monitoring.py` | 516 | 🔴 NEEDS SPLIT | None |
| `analytics/signals/models.py` | 514 | 🔴 NEEDS SPLIT | None |
| `data/markets.py` | 511 | 🔴 NEEDS SPLIT | None |
| `data/normalization.py` | 506 | 🔴 NEEDS SPLIT | None |

---

## Goals
- [ ] No files >500 lines remaining
- [ ] Clear module boundaries
- [ ] Single Responsibility Principle compliance
- [ ] Reduced merge conflicts
- [ ] Faster test execution (parallel loading)
- [ ] **NEW:** Consistent naming conventions (EPIC-020 patterns)
- [ ] **NEW:** No circular imports between modules

---

## Stories - UPDATED

### Story 1: Split exporters/markdown/generator.py (1,403 lines)
**Points:** 13  
**Priority:** P0  
**Status:** 🔴 NOT STARTED

Split the 1,403-line mega file into focused modules.

**Current Structure:**
```
exporters/markdown/
└── generator.py (1,403 lines, 45 functions)
```

**Target Structure:**
```
exporters/markdown/
├── __init__.py
├── generator.py (200 lines - orchestration only)
├── templates.py (250 lines - template definitions)
├── formatters.py (300 lines - formatting logic)
├── tables.py (200 lines - table generation)
├── charts.py (150 lines - chart embedding)
├── sections/
│   ├── __init__.py
│   ├── executive_summary.py (100 lines)
│   ├── competitive_analysis.py (150 lines)
│   └── financial_analysis.py (150 lines)
└── utils.py (100 lines - shared utilities)
```

**Acceptance Criteria:**
- [ ] 8 modules created
- [ ] Each module <300 lines
- [ ] Clear imports work: `from exporters.markdown import ReportGenerator`
- [ ] All tests pass
- [ ] No functionality lost
- [ ] **NEW:** Uses EPIC-020 section generator pattern

---

### Story 2: Split data/unified_loader.py (1,066 lines)
**Points:** 8  
**Priority:** P0  
**Status:** 🔴 NOT STARTED

Split unified loader into data source-specific loaders.

**Target Structure:**
```
data/loaders/
├── __init__.py
├── unified.py (200 lines - orchestration)
├── sec_edgar.py (250 lines - SEC EDGAR loading)
├── companies_house.py (200 lines - UK Companies House)
├── linkedin.py (150 lines - LinkedIn loading)
├── news.py (150 lines - News loading)
└── merger.py (150 lines - Data merging logic)
```

**Acceptance Criteria:**
- [ ] 6 modules created
- [ ] Each module <300 lines
- [ ] Unified loader orchestrates specific loaders
- [ ] Uses EPIC-020 helper modules where applicable
- [ ] No circular imports

---

### Story 3: Split data/loaders.py (939 lines)
**Points:** 8  
**Priority:** P0  
**Status:** 🔴 NOT STARTED

Split into competitor loader and field mapper modules.

**Target Structure:**
```
data/
├── loaders/
│   ├── __init__.py
│   ├── competitor_loader.py (200 lines)
│   ├── field_mappers/
│   │   ├── __init__.py
│   │   ├── financial_mapper.py (150 lines)
│   │   ├── metadata_mapper.py (100 lines)
│   │   └── score_mapper.py (100 lines)
│   └── utils.py (100 lines)
```

**Acceptance Criteria:**
- [ ] 6 modules created
- [ ] Leverages EPIC-020 `company_extractors.py` patterns
- [ ] Clear separation between loading and mapping
- [ ] All imports updated

---

### Story 4: Split worker_tasks.py (903 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED

Split Celery tasks by domain.

**Target Structure:**
```
worker/
├── __init__.py
├── enrichment_tasks.py (250 lines)
├── research_tasks.py (250 lines)
├── export_tasks.py (200 lines)
├── scoring_tasks.py (150 lines)
└── utils.py (100 lines)
```

**Acceptance Criteria:**
- [ ] 6 modules created
- [ ] Tasks grouped by domain
- [ ] Uses EPIC-020 executor patterns
- [ ] Celery configuration updated

---

### Story 5: Split infrastructure/database_models.py (836 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED

Split ORM models by domain.

**Target Structure:**
```
infrastructure/models/
├── __init__.py
├── company.py (150 lines)
├── research.py (200 lines)
├── enrichment.py (150 lines)
├── scoring.py (150 lines)
├── audit.py (150 lines)
└── base.py (100 lines - shared base classes)
```

**Acceptance Criteria:**
- [ ] 6 modules created
- [ ] Each domain has its own module
- [ ] Base classes in separate module
- [ ] No circular imports between model modules
- [ ] All relationships preserved

---

### Story 6: Complete domain/models.py Migration ⭐ UPDATED
**Points:** 5 → **REDUCED to 2**  
**Priority:** P1  
**Status:** 🟡 PARTIALLY COMPLETE (EPIC-020)

**EPIC-020 Progress:**
- ✅ Created `domain/models/` package structure
- ✅ Fixed circular import with `importlib` workaround
- ✅ `__init__.py` re-exports from `models.py`

**Remaining Work:**
- 🔄 Migrate classes from `models.py` to individual files
- 🔄 Remove `importlib` workaround
- 🔄 Update all imports
- 🔄 Deprecate monolithic `models.py`

**Target Structure:**
```
domain/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── company.py (200 lines)
│   ├── financial.py (150 lines)
│   ├── scoring.py (150 lines)
│   ├── research.py (150 lines)
│   └── enums.py (100 lines)
```

**Acceptance Criteria:**
- [ ] All classes migrated from models.py
- [ ] `importlib` workaround removed
- [ ] Clean imports without circular dependencies
- [ ] All tests pass
- [ ] Deprecation warning added to models.py

---

### Story 7: Split api/routers/enrichment.py (802 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED

Split fat router into service layer.

**Target Structure:**
```
api/
├── routers/
│   ├── enrichment.py (150 lines - thin router)
│   └── ...
services/
├── __init__.py
├── enrichment_service.py (400 lines)
└── enrichment_validation.py (150 lines)
```

**Acceptance Criteria:**
- [ ] Router <200 lines
- [ ] Service layer extracted
- [ ] Validation logic separated
- [ ] Uses EPIC-020 enrichment executors
- [ ] Clear separation of concerns

---

### Story 8: Split agents/github_agent.py (777 lines)
**Points:** 5  
**Priority:** P2  
**Status:** 🔴 NOT STARTED

Split GitHub agent into focused modules.

**Target Structure:**
```
agents/
├── github/
│   ├── __init__.py
│   ├── agent.py (200 lines - main agent)
│   ├── repository_analyzer.py (200 lines)
│   ├── security_scanner.py (200 lines)
│   └── api_client.py (150 lines)
```

**Acceptance Criteria:**
- [ ] 4 modules created
- [ ] Each has single responsibility
- [ ] Main agent orchestrates sub-modules
- [ ] Uses EPIC-020 Strategy pattern

---

### Story 9: Split data/additional_sources.py (769 lines)
**Points:** 5  
**Priority:** P2  
**Status:** 🔴 NOT STARTED

Split into source-specific modules.

**Target Structure:**
```
data/sources/
├── __init__.py
├── patents.py (150 lines)
├── trademarks.py (150 lines)
├── regulations.py (150 lines)
├── events.py (150 lines)
└── aggregator.py (150 lines)
```

**Acceptance Criteria:**
- [ ] 6 modules created
- [ ] Each source type has own module
- [ ] Aggregator orchestrates sources
- [ ] Consistent interface across sources

---

### Story 10: Complete llm/health_checker.py Migration ⭐ UPDATED
**Points:** 5 → **REDUCED to 2**  
**Priority:** P2  
**Status:** 🟡 PARTIALLY COMPLETE (EPIC-020)

**EPIC-020 Progress:**
- ✅ Strategies extracted to `provider_strategies.py`
- ✅ Provider-specific logic moved out

**Remaining Work:**
- 🔄 Extract metrics collection
- 🔄 Extract health check orchestration
- 🔄 Create clean module structure

**Target Structure:**
```
llm/
├── health/
│   ├── __init__.py
│   ├── checker.py (200 lines)
│   ├── providers.py (250 lines) ← Uses EPIC-020 strategies
│   └── metrics.py (150 lines)
```

**Acceptance Criteria:**
- [ ] Health checker <250 lines
- [ ] Uses EPIC-020 provider strategies
- [ ] Metrics collection separated
- [ ] Clean module boundaries

---

### Story 11-15: Split Remaining Large Files (500-700 lines)
**Points:** 3 each  
**Priority:** P2  
**Status:** 🔴 NOT STARTED

Files to split:
- `research/aggregate.py` (664 lines)
- `research/discovery.py` (654 lines) - Partially done via EPIC-020
- `research/gather.py` (648 lines)
- `llm/enhanced_client.py` (611 lines) - Partially done via EPIC-020
- `extractors/markdown_extractor.py` (578 lines)

**Acceptance Criteria (per file):**
- [ ] Split into 3-5 focused modules
- [ ] Each module <300 lines
- [ ] Clear module boundaries
- [ ] Uses EPIC-020 patterns where applicable

---

### Story 16-25: Split Files Approaching Limit (500-570 lines)
**Points:** 2 each  
**Priority:** P3  
**Status:** 🔴 NOT STARTED

Files to split:
- `infrastructure/research_dual_write.py` (572 lines) - EPIC-020 helpers extracted
- `exporters/excel_improved.py` (562 lines)
- `api/schemas/enrichment.py` (549 lines)
- `data/enrichment_orchestrator.py` (547 lines) - EPIC-020 executors extracted
- `research/ai_research_orchestrator.py` (543 lines)
- `research/pipeline.py` (533 lines) - EPIC-020 stages extracted
- `core/monitoring.py` (516 lines)
- `analytics/signals/models.py` (514 lines)
- `data/markets.py` (511 lines)
- `data/normalization.py` (506 lines)

**Acceptance Criteria (per file):**
- [ ] Split into 2-3 focused modules
- [ ] Each module <350 lines
- [ ] Leverages EPIC-020 work where applicable

---

### Story 26: Consolidate and Optimize Helper Modules ⭐ NEW
**Points:** 5  
**Priority:** P2  
**Status:** 🟡 READY

Review and optimize the 10 helper modules created in EPIC-020:
- `pipeline_stages.py` (491 lines)
- `company_extractors.py` (447 lines)
- `market_catalogs.py` (169 lines)
- `report_sections.py` (299 lines)
- `research_persistence.py` (291 lines)
- `reconciliation_helpers.py` (202 lines)
- `provider_strategies.py` (322 lines)
- `enrichment_executors.py` (221 lines)
- `company_builder.py` (225 lines)
- `sec_edgar_helpers.py` (158 lines)

**Tasks:**
- [ ] Review for code duplication across modules
- [ ] Consolidate related helpers if needed
- [ ] Ensure consistent naming conventions
- [ ] Verify all functions are used (no dead code)
- [ ] Add module-level documentation
- [ ] Create index/exports for clean imports

**Acceptance Criteria:**
- [ ] All modules reviewed
- [ ] Duplication eliminated
- [ ] Naming consistent
- [ ] Documentation complete
- [ ] Import paths clean

---

### Story 27: Create Module Index and Public API ⭐ NEW
**Points:** 3  
**Priority:** P2  
**Status:** 🟡 READY

Create clean public API for all new modules:

**Tasks:**
- [ ] Define public exports in each `__init__.py`
- [ ] Create module index documentation
- [ ] Document import paths
- [ ] Provide migration guide for old imports
- [ ] Add deprecation warnings for old locations

**Acceptance Criteria:**
- [ ] Clean imports: `from solstein.research import PipelineStage`
- [ ] All public APIs documented
- [ ] Migration guide created
- [ ] Deprecation warnings in place

---

### Story 28: Circular Import Prevention ⭐ NEW
**Points:** 5  
**Priority:** P1  
**Status:** 🟡 READY

Prevent circular imports during and after splitting:

**Tasks:**
- [ ] Map current import dependencies
- [ ] Identify potential cycles
- [ ] Define module boundaries
- [ ] Create import order guidelines
- [ ] Add CI check for circular imports

**Acceptance Criteria:**
- [ ] Import dependency graph created
- [ ] Module boundaries documented
- [ ] No circular imports introduced
- [ ] CI blocks new circular imports
- [ ] Guidelines added to AGENTS.md

---

## Migration Strategy - UPDATED

### Phase 1: Internal Extraction (No API Changes) ✅ EPIC-020 DONE
1. ✅ Create new module files
2. ✅ Move classes/functions to new modules
3. ✅ Import in original file for backward compatibility
4. 🔄 Update tests

### Phase 2: Complete Partial Work (EPIC-021 Focus)
1. Complete domain/models migration (Story 6)
2. Complete llm/health_checker migration (Story 10)
3. Consolidate helper modules (Story 26)
4. Create module index (Story 27)

### Phase 3: Split Remaining Files
1. Split P0 files (Stories 1-5)
2. Split P1 files (Stories 7-9)
3. Split P2 files (Stories 11-15)
4. Split P3 files (Stories 16-25)

### Phase 4: Update Imports and Deprecate
1. Update internal imports
2. Update external imports
3. Add deprecation warnings
4. Remove compatibility shims (future sprint)

---

## Testing Strategy
- Golden tests for behavior preservation
- Import tests for each new module
- Integration tests for cross-module calls
- Performance regression tests
- **NEW:** Circular import detection tests
- **NEW:** Module boundary violation tests

---

## Definition of Done
- [ ] All 25 files split into smaller modules
- [ ] No files >500 lines remain
- [ ] Clear module boundaries established
- [ ] All imports updated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] **NEW:** No circular imports
- [ ] **NEW:** Helper modules consolidated
- [ ] **NEW:** Public API documented

---

## Estimated Effort - UPDATED

### Phase 1: Complete Partial Work (Sprints 1-2)
- Story 6 (domain/models): 2 points
- Story 10 (health_checker): 2 points
- Story 26 (consolidate helpers): 5 points
- Story 27 (module index): 3 points
- Story 28 (circular import prevention): 5 points
- **Subtotal:** 17 points (2 weeks)

### Phase 2: Split P0 Files (Sprints 3-5)
- Stories 1-5: 39 points
- **Subtotal:** 39 points (4 weeks)

### Phase 3: Split P1-P2 Files (Sprints 6-9)
- Stories 7-15: 32 points
- **Subtotal:** 32 points (4 weeks)

### Phase 4: Split P3 Files (Sprints 10-11)
- Stories 16-25: 20 points
- **Subtotal:** 20 points (2 weeks)

### **Total:** 108 points (12 weeks) - REDUCED from 99 due to EPIC-020 progress

---

## Dependencies
- ✅ EPIC-020 (God functions) - COMPLETE - Patterns established
- 🔄 EPIC-019 (Automated detection) - For circular import detection
- 🔄 EPIC-022 (God classes) - Coordinate on class extraction

---

## Impact Summary

### What EPIC-020 Enables:
1. **Established Patterns:** Helper modules, extractors, strategies
2. **Partial Completion:** domain/models, health_checker, enrichment
3. **Code Reduction:** Some files already reduced by EPIC-020
4. **Pattern Library:** Examples for remaining work

### What EPIC-021 Must Address:
1. Complete partial migrations
2. Consolidate helper modules
3. Prevent circular imports
4. Create clean public API

---

*Updated: 2026-03-06*  
*Version: 2.0*  
*Based on: EPIC-020 Completion Analysis*
