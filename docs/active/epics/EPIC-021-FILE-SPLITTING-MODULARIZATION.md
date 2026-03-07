# Epic: File Splitting and Modularization (EPIC-021)

## Overview
Split 25 large files (>500 lines) into smaller, focused modules to improve maintainability, testability, and reduce merge conflicts.

## Current State
- 25 files exceed 500 lines
- 6 files exceed 1,000 lines (god files)
- Worst: `generator.py` at 1,403 lines

## Goals
- [ ] No files >500 lines remaining
- [ ] Clear module boundaries
- [ ] Single Responsibility Principle compliance
- [ ] Reduced merge conflicts
- [ ] Faster test execution (parallel loading)

## Worst Offenders
1. `exporters/markdown/generator.py` - 1,403 lines, 45 functions
2. `data/unified_loader.py` - 1,066 lines, 23 functions
3. `data/loaders.py` - 939 lines, 25 functions
4. `worker_tasks.py` - 903 lines, 20 functions
5. `infrastructure/database_models.py` - 836 lines, 10 functions

---

## Stories

### Story 1: Split exporters/markdown/generator.py (1,403 lines)
**Points:** 13
**Priority:** P0

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

### Story 2: Split data/unified_loader.py (1,066 lines)
**Points:** 8
**Priority:** P0

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

### Story 3: Split data/loaders.py (939 lines)
**Points:** 8
**Priority:** P0

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

### Story 4: Split worker_tasks.py (903 lines)
**Points:** 5
**Priority:** P1

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

### Story 5: Split infrastructure/database_models.py (836 lines)
**Points:** 5
**Priority:** P1

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

### Story 6: Split domain/models.py (818 lines)
**Points:** 5
**Priority:** P1

Split domain models into logical groups.

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

### Story 7: Split api/routers/enrichment.py (802 lines)
**Points:** 5
**Priority:** P1

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

### Story 8: Split agents/github_agent.py (777 lines)
**Points:** 5
**Priority:** P2

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

### Story 9: Split data/additional_sources.py (769 lines)
**Points:** 5
**Priority:** P2

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

### Story 10: Split llm/health_checker.py (704 lines)
**Points:** 5
**Priority:** P2

Split health checker into provider-specific checks.

**Target Structure:**
```
llm/
├── health/
│   ├── __init__.py
│   ├── checker.py (200 lines)
│   ├── providers.py (250 lines)
│   └── metrics.py (150 lines)
```

### Story 11-15: Remaining Large Files (500-700 lines)
**Points:** 3 each
**Priority:** P2

- `research/aggregate.py` (664 lines)
- `research/discovery.py` (654 lines)
- `research/gather.py` (648 lines)
- `llm/enhanced_client.py` (611 lines)
- `extractors/markdown_extractor.py` (578 lines)

### Story 16-25: Files Approaching Limit (500-570 lines)
**Points:** 2 each
**Priority:** P3

- `infrastructure/research_dual_write.py` (572 lines)
- `exporters/excel_improved.py` (562 lines)
- `api/schemas/enrichment.py` (549 lines)
- `data/enrichment_orchestrator.py` (547 lines)
- `research/ai_research_orchestrator.py` (543 lines)
- `research/pipeline.py` (533 lines)
- `core/monitoring.py` (516 lines)
- `analytics/signals/models.py` (514 lines)
- `data/markets.py` (511 lines)
- `data/normalization.py` (506 lines)

---

## Migration Strategy

### Phase 1: Internal Extraction (No API Changes)
1. Create new module files
2. Move classes/functions to new modules
3. Import in original file for backward compatibility
4. Update tests

### Phase 2: Update Imports
1. Update internal imports
2. Update external imports
3. Deprecate original locations

### Phase 3: Remove Original Files
1. After all imports updated
2. Remove compatibility shims

---

## Testing Strategy
- Golden tests for behavior preservation
- Import tests for each new module
- Integration tests for cross-module calls
- Performance regression tests

---

## Definition of Done
- [ ] All 25 files split into smaller modules
- [ ] No files >500 lines remain
- [ ] Clear module boundaries established
- [ ] All imports updated
- [ ] Tests passing
- [ ] Documentation updated

## Estimated Effort
- **Stories 1-3:** 29 points (3 weeks)
- **Stories 4-10:** 35 points (4 weeks)
- **Stories 11-15:** 15 points (2 weeks)
- **Stories 16-25:** 20 points (2 weeks)
- **Total:** 99 points (11 weeks)

## Dependencies
- EPIC-019 (Automated detection) - For monitoring
- EPIC-020 (God functions) - Coordinate refactoring

---

*Created: 2026-03-06*  
*Based on: COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md*
