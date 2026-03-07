# Solstein Module Index

> **EPIC-021: File Splitting - Module Index**
> 
> This document maps the public API surface and module dependencies to guide file splitting work.
> Last Updated: 2026-03-07

## Overview

Solstein follows a **layered architecture** with clear module boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI routers, schemas, middleware)           │
├─────────────────────────────────────────────────────────────┤
│  Application Layer (services, orchestrators)                │
├─────────────────────────────────────────────────────────────┤
│  Domain Layer (models, value objects, repository interfaces)│
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Layer (database, cache, external APIs)      │
├─────────────────────────────────────────────────────────────┤
│  Research Layer (pipeline, aggregation, extraction)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Public API Surface

### Top-Level Exports (`solstein`)

**File:** `src/solstein/__init__.py`

| Export | Type | Description |
|--------|------|-------------|
| `Company` | Class | Core domain model |
| `CompanyTier` | Enum | Company classification tiers |
| `ThreatLevel` | Enum | Competitive threat levels |
| `AIMaturity` | Enum | AI maturity levels |
| `UnifiedCompanyLoader` | Class | Data loading (lazy import) |
| `ExcelExporter` | Class | Excel export (lazy import) |
| `SolsteinError` | Exception | Base exception |
| `DataLoadError` | Exception | Data loading errors |
| `ValidationError` | Exception | Validation errors |
| `LLMAvailabilityError` | Exception | LLM provider errors |
| `ScoringWeights` | Constants | Scoring configuration |
| `Thresholds` | Constants | Business thresholds |
| `logger` | Logger | Loguru logger instance |

### Domain Models (`solstein.domain.models`)

**File:** `src/solstein/domain/models/__init__.py`

| Export | Type | Description |
|--------|------|-------------|
| `Company` | Pydantic Model | Company with financials, scores |
| `FinancialMetric` | Pydantic Model | Revenue, growth, etc. |
| `MarketAnalysis` | Pydantic Model | Market position analysis |
| `ScoreComponent` | Pydantic Model | Individual score breakdown |
| `ScoringExplanation` | Pydantic Model | Why a score was given |
| `CompetitiveOverlap` | Pydantic Model | Competitor overlap data |
| `RawDataSource` | Pydantic Model | Data source metadata |
| `RawDataRecord` | Pydantic Model | Raw data record |
| `AggregatedFact` | Pydantic Model | Reconciled fact |
| `AggregatedDataRecord` | Pydantic Model | Aggregated data |
| `SignalExtraction` | Pydantic Model | Extracted signal |
| `SignalExtractionRecord` | Pydantic Model | Signal with metadata |
| `GatheringBatch` | Pydantic Model | Batch of gathered data |
| `CompanyAnalysisAuditTrail` | Pydantic Model | Audit trail |
| `ConfidenceLevel` | Enum | Confidence in data |
| `AIMaturity` | Enum | AI maturity classification |
| `ThreatLevel` | Enum | Threat level classification |
| `CompanyTier` | Enum | Company tier classification |
| `CompanyClassification` | Enum | Phoenix/Salt/Lead classification |
| `ErrorCategory` | Enum | Error categories |
| `ErrorSeverity` | Enum | Error severity levels |
| `DataSourceType` | Enum | Data source types |

### Research Module (`solstein.research`)

**File:** `src/solstein/research/__init__.py`

| Export | Type | Description |
|--------|------|-------------|
| `AIResearchOrchestrator` | Class | Main research orchestrator |
| `ResearchPlannerAgent` | Class | Plans research strategy |
| `WebSearchAgent` | Class | Performs web searches |
| `ContentExtractorAgent` | Class | Extracts content from pages |
| `DataValidatorAgent` | Class | Validates extracted data |
| `ResearchPlan` | Dataclass | Research plan structure |
| `ResearchReport` | Dataclass | Research report structure |
| `SearchResult` | Dataclass | Search result structure |
| `ExtractedData` | Dataclass | Extracted data structure |
| `ValidationResult` | Dataclass | Validation result structure |

---

## Module Dependencies

### Critical Dependency Chains

```
domain/models.py
  ↓ (imported by)
api/schemas/*.py, research/*.py, analytics/*.py, exporters/*.py
  ↓ (imported by)
api/routers/*.py
```

### Circular Import Risks

**Known Issue:** `domain/models/__init__.py` uses dynamic import to avoid circular imports with the legacy `domain/models.py` file.

**Safe Import Pattern:**
```python
# ✅ Always import from the package, not the file
from solstein.domain.models import Company

# ❌ Avoid direct file imports
from solstein.domain.models import Company  # This works via __init__.py
```

---

## Files Requiring Splitting (EPIC-021)

### P0 - Must Split (>600 lines)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `infrastructure/database_models.py` | 59 lines | ✅ COMPLETE | Split into models/ package |
| `domain/models.py` | 818 lines | 🔄 IN PROGRESS | Package structure exists |
| `research/aggregate.py` | 664 lines | ⏳ PENDING | Next target |

| File | Lines | Target | Strategy |
|------|-------|--------|----------|
| `infrastructure/database_models.py` | 836 | 3-4 files | By entity group |
| `domain/models.py` | 818 | Package | Already in progress |
| `research/aggregate.py` | 664 | 2-3 files | By aggregation stage |

### P1 - Should Split (500-600 lines)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `research/pipeline_stages.py` | 576 lines | ✅ COMPLETE | Already modularized in EPIC-020 |
| `extractors/markdown_extractor.py` | 573 lines | ⏳ PENDING | |
| `exporters/excel_improved.py` | 562 lines | ⏳ PENDING | |
| `api/schemas/enrichment.py` | 549 lines | ⏳ PENDING | |
| `research/ai_research_orchestrator.py` | 543 lines | ⏳ PENDING | |
| `monitoring/alerts.py` | 538 lines | ⏳ PENDING | |
| `core/monitoring.py` | 516 lines | ⏳ PENDING | |
| `analytics/signals/models.py` | 514 lines | ⏳ PENDING | |
| `research/market_catalogs.py` | 505 lines | ✅ COMPLETE | Already modular |

| File | Lines | Target | Strategy |
|------|-------|--------|----------|
| `research/pipeline_stages.py` | 576 | 2 files | Already modularized |
| `extractors/markdown_extractor.py` | 573 | 2 files | Separate BatchExtractor |
| `exporters/excel_improved.py` | 562 | 2 files | By export type |
| `api/schemas/enrichment.py` | 549 | 2 files | By schema group |
| `research/ai_research_orchestrator.py` | 543 | 2 files | By agent type |
| `monitoring/alerts.py` | 538 | 2 files | By alert type |
| `core/monitoring.py` | 516 | 2 files | By concern |
| `analytics/signals/models.py` | 514 | 2 files | By signal type |
| `research/market_catalogs.py` | 505 | 2 files | Already modular |

### P2 - Monitor (400-500 lines)

These files should be monitored and split when they approach 500 lines:

- `analytics/scoring.py` (484)
- `data/web_research_pipeline.py` (475)
- `evidence/graph.py` (469)
- `monitoring/incidents.py` (458)
- And 15 more...

---

## Internal vs Public API

### Public (Stable)

These should maintain backward compatibility:

- `solstein.Company`
- `solstein.domain.models.*`
- `solstein.research.AIResearchOrchestrator`
- All Pydantic models in `domain/models`

### Internal (May Change)

These are implementation details:

- Helper functions in `research/pipeline_stages.py`
- Internal methods in `exporters/markdown/generator.py`
- Database models in `infrastructure/database_models.py`
- Celery tasks in `worker_tasks.py`

---

## Migration Guidelines

### When Splitting Files:

1. **Maintain backward compatibility** - Keep old imports working via `__init__.py`
2. **Update this index** - Document new module locations
3. **Run quality checks** - Ensure no circular imports introduced
4. **Update tests** - Ensure all tests pass after split

### Import Patterns to Follow:

```python
# ✅ Public API imports
from solstein.domain.models import Company
from solstein.research import AIResearchOrchestrator

# ✅ Internal imports (within same module)
from .pipeline_stages import DiscoveryStage

# ❌ Deep imports (brittle)
from solstein.domain.models.company import Company  # Don't do this
```

---

## Quality Gates

Before marking EPIC-021 complete:

- [ ] All files <500 lines
- [ ] No circular imports (verified by `detect_import_cycles.py`)
- [ ] All public APIs still importable
- [ ] All tests passing
- [ ] This index updated with final module locations

---

*Part of EPIC-021: File Splitting*
