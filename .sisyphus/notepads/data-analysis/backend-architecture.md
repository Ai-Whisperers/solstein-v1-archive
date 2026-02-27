# Solstein Backend Architecture Analysis

## Executive Summary

This document provides a comprehensive analysis of Solstein's backend architecture, covering repository patterns, service layers, mock usage, JSON file dependencies, API endpoints, and data flows. The analysis identifies areas where real database connections should replace mocks and JSON-based data storage.

---

## 1. Repository Pattern Implementation

### 1.1 Repository Classes Overview

| Repository | Location | Purpose | Storage Type |
|------------|----------|---------|--------------|
| `CompanyRepository` | `core/repositories.py` | Abstract interface for Company data access | ABC (Interface) |
| `JsonFileRepository` | `data/repositories.py` | JSON-based company data storage | JSON Files |
| `SupabaseRepository` | `data/repositories.py` | PostgreSQL via Supabase | Real Database |
| `FactRepository` | `infrastructure/repositories.py` | Fact/GatheringBatch/FactSource operations | Real Database (SQLAlchemy) |
| `EnrichmentAuditRepository` | `infrastructure/enrichment_repositories.py` | Enrichment audit trail operations | Real Database (Async SQLAlchemy) |
| `EnrichmentCacheRepository` | `infrastructure/enrichment_repositories.py` | Enrichment cache operations | Real Database (Async SQLAlchemy) |

### 1.2 Repository Methods Detail

#### JsonFileRepository (`data/repositories.py`)
```
- get_all(limit, offset, filters) -> list[Company]
- get_by_id(company_id) -> Company | None
- save(company) -> Company  [SIMULATION - logs only]
- delete(company_id) -> bool  [SIMULATION - logs only]
- search(query, field) -> list[Company]
- get_all_llm_filtered(criteria, limit, offset) -> tuple[list[Company], dict]
```

#### SupabaseRepository (`data/repositories.py`)
```
- get_all(limit, offset, filters) -> list[Company]
- get_by_id(company_id) -> Company | None
- save(company) -> Company  [REAL - upserts to Supabase]
- delete(company_id) -> bool  [REAL - deletes from Supabase]
- search(query, field) -> list[Company]
```

#### FactRepository (`infrastructure/repositories.py`)
```
- create_batch(company_id, status) -> GatheringBatch
- store(fact) -> str (fact_id)
- store_batch(facts, batch) -> list[str]
- get_company_facts(company_id) -> list[Fact]
- get_facts_by_type(company_id, fact_type) -> list[Fact]
- get_fact_by_id(fact_id) -> Fact | None
- add_source(fact_id, source_type, source_url, raw_content) -> FactSource
- get_batch(batch_id) -> GatheringBatch | None
- update_batch_status(batch_id, status) -> GatheringBatch
```

#### EnrichmentAuditRepository (`infrastructure/enrichment_repositories.py`)
```
- log_operation(...) -> EnrichmentAuditRecord  [ASYNC]
- get_audit_trail(company_id, limit, offset) -> List[EnrichmentAuditRecord]  [ASYNC]
- get_company_stats(company_id) -> dict  [ASYNC]
```

#### EnrichmentCacheRepository (`infrastructure/enrichment_repositories.py`)
```
- get_cached(company_id) -> Optional[EnrichmentCacheRecord]  [ASYNC]
- cache_enrichment(company_id, enriched_data, sources_used, fields_enriched, ttl_seconds)  [ASYNC]
- delete_cache(company_id) -> int  [ASYNC]
- get_cache_stats() -> dict  [ASYNC]
```

---

## 2. Service Layer Architecture

### 2.1 Service Classes

| Service | Location | Responsibilities |
|---------|----------|------------------|
| `DatabaseService` | `infrastructure/database_service.py` | Save scoring records, signals, market snapshots, audit trails |
| `DrillDownService` | `api/services/drill_down_service.py` | Detailed company analysis |
| `EnrichmentService` | `api/services/enrichment_service.py` | Orchestrate data enrichment from connectors |

### 2.2 DatabaseService Methods
```
- save_scoring_record(...) -> ScoringRecord
- save_signal(...) -> SignalRecord
- save_market_snapshot(...) -> MarketSnapshot
- save_audit_trail(...) -> AuditTrailRecord
- get_audit_trail(company_id) -> AuditTrailRecord | None
- get_company_scores(company_id, limit) -> list[ScoringRecord]
- get_latest_score(company_id) -> ScoringRecord | None
- get_signals_for_score(scoring_record_id) -> list[SignalRecord]
- get_market_snapshots(limit) -> list[MarketSnapshot]
```

### 2.3 Analytics Services

The `analytics/` directory contains business logic services:

| Module | Purpose |
|--------|---------|
| `scoring.py` | GrowthScorer - calculates company scores |
| `classification.py` | Classification logic for Phoenix/Salt/Lead |
| `company_loader.py` | Load companies for unified scoring |
| `completeness.py` | Data completeness scoring |
| `confidence_integration.py` | Confidence weighting integration |
| `confidence_weighting.py` | Signal confidence calculations |
| `scorers/` | Individual scorer modules (growth, financial, competitive) |
| `signals/` | Signal extraction and processing |
| `valuation/` | Company valuation logic |

---

## 3. Mock vs Real Database Usage

### 3.1 Current Mock Usage

#### JsonFileRepository (MOCK - JSON Storage)
**Status**: Used as fallback when Supabase is not configured

**Locations Used**:
- `api/dependencies.py` - `get_repository()` falls back to JsonFileRepository
- `api/routers/scoring.py` - Uses JsonFileRepository via dependency injection
- `api/routers/companies.py` - Uses JsonFileRepository via dependency injection

**Issues**:
- `save()` method only logs, does not persist (line 108-111)
- `delete()` method only logs, does not delete (line 113-116)
- Loads entire JSON file into memory for filtering
- No server-side pagination support

#### Mock TemporalClient (`api/routers/scoring.py`)
**Status**: Mock implementation (lines 10-23)

```python
class TemporalClient:
    """Mock-friendly stub for TemporalClient."""
    @classmethod
    async def connect(cls, *args, **kwargs):
        return cls()
    async def start_workflow(self, *args, **kwargs):
        # Returns mock handle
```

### 3.2 Real Database Usage

#### FactRepository (REAL - PostgreSQL via SQLAlchemy)
- Uses `DatabaseManager` for session management
- Synchronous SQLAlchemy operations
- Full CRUD with transaction management

#### EnrichmentAuditRepository / EnrichmentCacheRepository (REAL - PostgreSQL via Async SQLAlchemy)
- Uses `AsyncSession` for async operations
- Implements caching with TTL
- Full audit trail functionality

#### SupabaseRepository (REAL - PostgreSQL via Supabase)
- Uses Supabase Python client
- Proper upsert/delete operations
- Server-side filtering and pagination

---

## 4. JSON File Usage

### 4.1 JSON Data Files

| File | Purpose | Size |
|------|---------|------|
| `data/input/competitor_data.json` | Main company data | Large (production data) |
| `data/fixtures/envision_digital_profile.json` | Test fixture | Small |

### 4.2 JSON Loader Architecture

**CompetitorDataLoader** (`data/loaders.py`):
- Loads from `data/input/competitor_data.json`
- Converts JSON to Company domain entities
- Implements in-memory caching
- Handles multiple data formats (nested and flat)

**Key Methods**:
```
- load_companies(limit) -> list[Company]
- _load_from_json(json_path, limit) -> list[Company]
- _convert_to_domain_company(raw_data, index) -> Company
```

### 4.3 JSON Dependencies

**Direct JSON Usage**:
1. `CompetitorDataLoader` - Primary company data
2. `UnifiedCompanyLoader` - Merges JSON + Markdown data
3. `JsonFileRepository` - Wraps CompetitorDataLoader

**Fallback Chain**:
```
get_repository() 
  -> SupabaseRepository (if configured)
  -> JsonFileRepository (fallback)
```

---

## 5. API Endpoints

### 5.1 Endpoint Overview

| Method | Endpoint | Router | Data Source |
|--------|----------|--------|-------------|
| GET | `/health` | enrichment.py | Real (DB check) |
| GET | `/ready` | enrichment.py | Real (DB check) |
| GET | `/metrics` | enrichment.py | UnifiedLoader |
| POST | `/companies/{id}/enrich` | enrichment.py | UnifiedLoader |
| POST | `/companies/enrich/batch` | enrichment.py | UnifiedLoader |
| GET | `/companies/{id}/enrichment/audit` | enrichment.py | DB + In-memory fallback |
| GET | `/companies/{id}/enrichment/cache` | enrichment.py | DB + In-memory fallback |
| POST | `/enrichment/cache/clear` | enrichment.py | DB + In-memory |
| POST | `/enrichment/cache/clear/{company_id}` | enrichment.py | DB + In-memory |
| GET | `/companies` | companies.py | JsonFileRepository/SupabaseRepository |
| GET | `/companies/{company_id}` | companies.py | JsonFileRepository/SupabaseRepository |
| POST | `/companies` | companies.py | JsonFileRepository/SupabaseRepository |
| DELETE | `/companies/{company_id}` | companies.py | JsonFileRepository/SupabaseRepository |
| POST | `/scoring/company/{company_id}/score` | scoring.py | UnifiedScoreLoader + Repository |
| GET | `/scoring/stats` | scoring.py | Repository (get_all) |
| GET | `/scoring/batch` | scoring.py | Temporal (mock) or fallback |
| GET | `/market/analysis` | market.py | - |
| GET | `/market/search` | market.py | - |
| GET | `/market/overlap/{id}` | market.py | - |
| POST | `/export/` | export.py | - |

### 5.2 Data Sources Used by Endpoints

**Enrichment Endpoints** use:
- `unified_loader.UnifiedCompanyLoader` - Primary
- `EnrichmentAuditRepository` / `EnrichmentCacheRepository` - DB-backed
- In-memory fallback: `audit_logger`, `unified_loader.cache`

**Company Endpoints** use:
- Repository pattern via dependency injection
- Falls back to JsonFileRepository or uses SupabaseRepository

**Scoring Endpoints** use:
- `unified_score_loader` (from `analytics/company_loader.py`)
- Repository for persistence
- `GrowthScorer` for calculations

---

## 6. Data Flow Diagrams

### 6.1 API → Service → Repository → Database Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │ enrichment.py   │  │  companies.py   │  │   scoring.py    │       │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │
│           │                    │                    │                 │
│           ▼                    ▼                    ▼                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   dependencies.py                                │   │
│  │  get_repository() → JsonFileRepository / SupabaseRepository    │   │
│  │  get_db_session() → AsyncSession                               │   │
│  │  get_database_service() → DatabaseService                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │ EnrichmentService│  │ DrillDownService│  │ GrowthScorer    │       │
│  │ (enrichment)    │  │   (drill_down) │  │   (analytics)   │       │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │
│           │                    │                    │                 │
│           ▼                    ▼                    ▼                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │UnifiedCompanyLoader│ │DatabaseService │  │UnifiedScoreLoader│      │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        REPOSITORY LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │JsonFileRepository│ │SupabaseRepository│ │ FactRepository │       │
│  │   (MOCK)        │  │   (REAL)        │  │    (REAL)      │       │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘       │
│           │                    │                    │                 │
│           ▼                    ▼                    ▼                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │competitor_data  │  │  PostgreSQL     │  │ PostgreSQL      │       │
│  │    .json        │  │  (Supabase)     │  │ (SQLAlchemy)    │       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Enrichment Data Flow

```
POST /companies/{id}/enrich
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Rate Limit Check (rate_limiter)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Input Validation (input_validator)│
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Get Repositories (Lazy Load)     │
│   - EnrichmentAuditRepository (DB)  │
│   - EnrichmentCacheRepository (DB)  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 4. Check Cache                      │
│   - DB cache first                  │
│   - In-memory fallback               │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 5. Call unified_loader.enrich_from_ │
│    connectors(company)               │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 6. Cache Results (if not cached)    │
│   - DB cache                        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 7. Log Audit Trail                  │
│   - DB audit                        │
│   - In-memory fallback               │
└─────────────────────────────────────┘
```

---

## 7. Areas Requiring Improvement

### 7.1 High Priority

#### 1. Replace JsonFileRepository with Real Database
**Current**: JsonFileRepository is used as default, save/delete are no-ops
**Impact**: All company CRUD operations fail silently
**Recommendation**: 
- Always use SupabaseRepository when Supabase is configured
- Implement actual save/delete in JsonFileRepository or deprecate it
- Add migration path from JSON to Supabase

#### 2. Implement Proper JSON → Database Migration
**Current**: `competitor_data.json` is the source of truth
**Impact**: No persistence of changes, no concurrent access
**Recommendation**:
- Create one-time migration script to load JSON to Supabase
- Update loader to read from Supabase by default
- Keep JSON as import-only source

#### 3. Remove Mock TemporalClient
**Current**: Mock implementation in `scoring.py`
**Impact**: Batch scoring doesn't work properly
**Recommendation**:
- Implement real Temporal workflow or use Celery
- Remove mock stub

### 7.2 Medium Priority

#### 4. Centralize Repository Initialization
**Current**: Multiple places create repository instances
**Impact**: Inconsistent behavior, hard to test
**Recommendation**:
- Single factory or dependency injection container
- Clear configuration for production vs development

#### 5. Consistent Error Handling for DB Fallbacks
**Current**: Enrichment endpoints fall back to in-memory on DB failure
**Impact**: Silent failures, inconsistent behavior
**Recommendation**:
- Log all fallback events clearly
- Consider failing fast in production

#### 6. Add Connection Pooling
**Current**: New session created per request
**Impact**: Performance issues under load
**Recommendation**:
- Implement connection pooling for SQLAlchemy
- Use connection pool for Supabase client

### 7.3 Low Priority

#### 7. Deprecate Legacy Code Paths
**Current**: Multiple code paths for JSON/Markdown loading
**Impact**: Maintenance burden
**Recommendation**:
- Document all data loading paths
- Consolidate to single path after migration

---

## 8. Recommendations Summary

| Priority | Item | Current State | Target State |
|----------|------|---------------|--------------|
| HIGH | Company CRUD | JsonFileRepository (no-op save) | SupabaseRepository |
| HIGH | Batch Scoring | Mock TemporalClient | Real Celery/Temporal |
| MEDIUM | Repository DI | Scattered initialization | Centralized factory |
| MEDIUM | DB Fallbacks | Silent in-memory fallback | Explicit configuration |
| LOW | Data Loading | Multiple paths | Single unified path |

---

## Appendix: File Locations

### Core Files
- Repository Interface: `/src/solstein/core/repositories.py`
- Repository Implementations: `/src/solstein/data/repositories.py`
- Fact Repository: `/src/solstein/infrastructure/repositories.py`
- Enrichment Repositories: `/src/solstein/infrastructure/enrichment_repositories.py`
- Database Service: `/src/solstein/infrastructure/database_service.py`

### API Files
- Dependencies: `/src/solstein/api/dependencies.py`
- Enrichment Router: `/src/solstein/api/routers/enrichment.py`
- Companies Router: `/src/solstein/api/routers/companies.py`
- Scoring Router: `/src/solstein/api/routers/scoring.py`

### Data Files
- Company Loader: `/src/solstein/data/loaders.py`
- Unified Loader: `/src/solstein/data/unified_loader.py`
- JSON Data: `/data/input/competitor_data.json`

### Configuration
- Settings: `/src/solstein/config.py`
- Supabase Client: `/src/solstein/core/supabase_client.py`
