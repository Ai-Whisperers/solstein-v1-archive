# Solstein Project - Complete Data & Architecture Analysis

**Date**: 2026-02-27  
**Scope**: Database schema, backend architecture, JSON usage, improvement recommendations

---

## 📊 EXECUTIVE SUMMARY

The Solstein project has a **sophisticated PostgreSQL database** with 14+ tables but still relies on **JSON files** for core company data. The backend uses a **mix of repository patterns** (sync/async, SQLAlchemy/Supabase client/JSON files) creating inconsistency.

**Key Findings:**
- ✅ 14 database tables with proper migrations
- ✅ Good use of JSONB for flexible data
- ✅ Row Level Security (RLS) enabled
- ❌ Company data still stored in JSON file (data/input/competitor_data.json)
- ❌ FactRepository uses sync pattern (should be async)
- ❌ JsonFileRepository still used instead of database
- ❌ Mix of repository patterns across codebase

---

## 🗄️ DATABASE SCHEMA (14 Tables)

### Core Tables

#### 1. **companies** (Main entity table)
```sql
- id: UUID PRIMARY KEY
- name: VARCHAR(255) NOT NULL
- industry: VARCHAR(100) NOT NULL
- tier: VARCHAR(50) NOT NULL
- growth_score: NUMERIC(5,2)
- financial_health_score: NUMERIC(5,2)
- competitive_position_score: NUMERIC(5,2)
- classification: VARCHAR(50)
- scoring_breakdown: JSONB DEFAULT '{}'
- financials: JSONB DEFAULT '{}'
- revenue: NUMERIC
- growth_rate: NUMERIC
- profit_margin: NUMERIC
- valuation: NUMERIC
- employees: INTEGER
- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()
```
**Indexes**: tier, industry, classification, revenue  
**RLS**: Enabled with anon read/insert/update policies

#### 2. **research_runs** (Research workflow runs)
```sql
- id: UUID PRIMARY KEY
- run_id: VARCHAR(255) NOT NULL UNIQUE
- market: VARCHAR(255) NOT NULL
- seed_company: VARCHAR(500) NOT NULL
- status: VARCHAR(50) DEFAULT 'completed'
- strict_provenance: BOOLEAN DEFAULT TRUE
- min_readiness_score: NUMERIC
- max_contradictions: INTEGER
- min_total_sources: INTEGER
- summary: JSONB
- created_at: TIMESTAMPTZ DEFAULT NOW()
```

#### 3. **research_stages** (Workflow stages)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- stage_name: VARCHAR(100) NOT NULL
- stage_order: INTEGER NOT NULL
- status: VARCHAR(50)
- metrics: JSONB
- created_at: TIMESTAMPTZ DEFAULT NOW()
- UNIQUE: (run_id, stage_name)
```
**Index**: run_id, stage_order

#### 4. **research_artifacts** (Artifacts from research)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- artifact_name: VARCHAR(255) NOT NULL
- artifact_path: VARCHAR(1000)
- payload: JSONB
- created_at: TIMESTAMPTZ DEFAULT NOW()
- UNIQUE: (run_id, artifact_name)
```

#### 5. **source_documents** (Web sources)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- company_id: VARCHAR(255) NOT NULL
- source_url: VARCHAR(2000) NOT NULL
- source_domain: VARCHAR(255)
- source_type: VARCHAR(100)
- observed_at: TIMESTAMPTZ DEFAULT NOW()
- status: VARCHAR(50) DEFAULT 'observed'
- fetched_at: TIMESTAMPTZ
- content_hash: VARCHAR(128)
- extract_hash: VARCHAR(128)
- UNIQUE: (run_id, company_id, source_url)
```
**Indexes**: company_id, source_domain

#### 6. **metric_observations** (Extracted metrics)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- company_id: VARCHAR(255) NOT NULL
- metric_key: VARCHAR(100) NOT NULL
- metric_value: NUMERIC
- metric_value_raw: JSONB
- source_url: VARCHAR(2000)
- created_at: TIMESTAMPTZ DEFAULT NOW()
- UNIQUE: (run_id, company_id, metric_key, source_url, metric_value)
```
**Index**: company_id, metric_key

#### 7. **evidence_readiness** (Data quality scores)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- company_id: VARCHAR(255) NOT NULL
- company_name: VARCHAR(500) NOT NULL
- readiness_score: NUMERIC NOT NULL
- readiness_level: VARCHAR(100) NOT NULL
- source_count: INTEGER DEFAULT 0
- source_domain_count: INTEGER DEFAULT 0
- metric_source_coverage: NUMERIC DEFAULT 0
- metric_explainability: NUMERIC DEFAULT 0
- unsupported_metrics: INTEGER DEFAULT 0
- created_at: TIMESTAMPTZ DEFAULT NOW()
- UNIQUE: (run_id, company_id)
```
**Index**: readiness_level

#### 8. **research_contradictions** (Data contradictions)
```sql
- id: UUID PRIMARY KEY
- run_id: UUID NOT NULL → FK research_runs(id) ON DELETE CASCADE
- company_id: VARCHAR(255) NOT NULL
- metric_key: VARCHAR(100) NOT NULL
- contradiction_type: VARCHAR(100) NOT NULL
- details: JSONB
- status: VARCHAR(50) DEFAULT 'open' CHECK ('open','resolved','ignored')
- updated_at: TIMESTAMPTZ DEFAULT NOW()
- resolved_at: TIMESTAMPTZ
- ignored_at: TIMESTAMPTZ
- created_at: TIMESTAMPTZ DEFAULT NOW()
- UNIQUE: (run_id, company_id, metric_key, contradiction_type)
```

#### 9. **research_contradiction_transitions** (Status history)
```sql
- id: UUID PRIMARY KEY
- contradiction_id: UUID NOT NULL → FK research_contradictions(id) ON DELETE CASCADE
- from_status: VARCHAR(50) NOT NULL
- to_status: VARCHAR(50) NOT NULL
- changed_at: TIMESTAMPTZ DEFAULT NOW()
- changed_by: VARCHAR(255)
- reason: TEXT
```
**Index**: contradiction_id

#### 10. **outbox_records** (Event outbox pattern)
```sql
- id: UUID PRIMARY KEY
- event_key: VARCHAR(255) NOT NULL UNIQUE
- event_type: VARCHAR(100) NOT NULL
- status: VARCHAR(50) DEFAULT 'pending' CHECK ('pending','in_progress','succeeded','failed')
- payload: JSONB NOT NULL
- attempt_count: INTEGER DEFAULT 0
- available_at: TIMESTAMPTZ DEFAULT NOW()
- created_at: TIMESTAMPTZ DEFAULT NOW()
- updated_at: TIMESTAMPTZ DEFAULT NOW()
- last_error: JSONB
```
**Indexes**: event_type, status, available_at, (status, available_at)

---

## 🔄 SQLALCHEMY MODELS (18 Models)

In addition to the 14 migration tables, `database_models.py` defines 18 SQLAlchemy models:

### Additional Models (Not in Migrations Yet):
1. **CompanyRecord** - Extended company data with revenue_timeline, funding_rounds
2. **ScoringRecord** - Scoring results with data_sources_used
3. **SignalRecord** - Individual signals with evidence JSON
4. **MarketSnapshot** - Market state snapshots
5. **AuditTrailRecord** - Complete audit trail
6. **EnrichmentAuditRecord** - Enrichment audit
7. **EnrichmentCacheRecord** - Enrichment cache with TTL
8. **EnrichmentJobRecord** - Async enrichment jobs

### Migration vs Model Discrepancy:
- **Migrations**: 14 tables (research-focused)
- **Models**: 18 tables (includes scoring/enrichment)
- **Gap**: Scoring and enrichment tables exist as models but may not have migrations

---

## 📁 JSON FILE USAGE

### Primary JSON Data File

**File**: `data/input/competitor_data.json`
**Content**: 3 competitor companies with full profiles

```json
{
  "competitors": [
    {
      "company_name": "Eneve",
      "folder": "eneve",
      "revenue": {
        "timeline": [{"year": 2023, "eur_millions": 5.0, "yoy_growth_pct": 35}, ...],
        "cagr_3yr_pct": 45.0
      },
      "profitability": {...},
      "employees": 150,
      "founded_year": 2015,
      "country": "Germany",
      "industry": "Energy Software",
      "ai_maturity_score": 7.5,
      "classification": "Phoenix",
      "classification_confidence": 0.95
    }
  ]
}
```

**❌ PROBLEM**: This data should be in the `companies` table, not a JSON file

### JSON Usage in Code (12 files):
- `src/solstein/data/loaders.py` - Loads competitor_data.json
- `src/solstein/data/additional_sources.py` - JSON serialization
- `src/solstein/agents/github_agent.py` - JSON parsing
- `src/solstein/research/pipeline.py` - JSON contracts
- `src/solstein/infrastructure/research_dual_write.py` - JSON payloads
- And 7 more files...

### JSONB Columns in Database:
- companies.scoring_breakdown
- companies.financials
- research_runs.summary
- research_stages.metrics
- research_artifacts.payload
- metric_observations.metric_value_raw
- research_contradictions.details
- outbox_records.payload, outbox_records.last_error
- All enrichment tables use JSONB extensively

**✅ GOOD**: JSONB used appropriately for flexible/schemaless data

---

## 🏛️ BACKEND ARCHITECTURE

### Repository Pattern Analysis

#### 1. **FactRepository** (`infrastructure/repositories.py`)
```python
class FactRepository:
    """❌ SYNC PATTERN - NEEDS CONVERSION"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_batch(self, company_id: str) -> GatheringBatch:
        session = self.db_manager.get_session()
        # ... sync operations
        session.commit()  # ❌ Not async
        session.close()   # ❌ Not async
```

**Problems**:
- Uses sync SQLAlchemy session
- Methods not async
- Should use async/await pattern like test files

#### 2. **JsonFileRepository** (`data/repositories.py`)
```python
class JsonFileRepository(CompanyRepository):
    """❌ READS FROM JSON FILE - SHOULD USE DATABASE"""
    
    def __init__(self, file_path: str = "data/input/competitor_data.json"):
        self.loader = CompetitorDataLoader(file_path)
    
    def get_all(self) -> list[Company]:
        return self.loader.load_companies()
```

**Problems**:
- Reads from JSON instead of database
- No database persistence
- Filters applied in Python (slow)

#### 3. **SupabaseRepository** (`data/repositories.py`)
```python
class SupabaseRepository(CompanyRepository):
    """⚠️ USES SUPABASE CLIENT - MIXED PATTERN"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    def get_all(self) -> list[Company]:
        response = self.client.table("companies").select("*").execute()
        # ... convert to Company objects
```

**Problems**:
- Uses Supabase client instead of SQLAlchemy
- Different pattern from other repositories
- Harder to test and mock

#### 4. **Enrichment Repositories** (`infrastructure/enrichment_repositories.py`)
```python
class EnrichmentAuditRepository:
    """✅ ASYNC PATTERN - CORRECT"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_operation(self, ...) -> EnrichmentAuditRecord:
        record = EnrichmentAuditRecord(...)
        self.session.add(record)
        await self.session.commit()  # ✅ Async
        return record
```

**✅ GOOD**: Proper async pattern with AsyncSession

### Service Layer

#### DatabaseService (`infrastructure/database_service.py`)
```python
class DatabaseService:
    """✅ ASYNC PATTERN - CORRECT"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_scoring_record(self, ...) -> ScoringRecord:
        record = ScoringRecord(...)
        self.session.add(record)
        await self.session.commit()  # ✅ Async
        return record
```

**Methods**:
- save_scoring_record()
- save_signal()
- save_market_snapshot()
- save_audit_trail()
- get_audit_trail()
- get_company_scores()
- get_latest_score()
- get_signals_for_score()
- get_market_snapshots()
- commit(), rollback()

**✅ GOOD**: Proper async pattern

---

## ⚠️ CRITICAL ISSUES & RECOMMENDATIONS

### HIGH PRIORITY (Fix Immediately)

#### 1. **Migrate Company Data from JSON to Database**
**Current**: Company data stored in `data/input/competitor_data.json`  
**Should Be**: Stored in `companies` table

**Migration Plan**:
```python
# 1. Create migration script
# 2. Read JSON file
# 3. Insert into companies table
# 4. Update JsonFileRepository to use SQLAlchemy
# 5. Deprecate JSON file
```

**Files to Update**:
- `data/repositories.py` - JsonFileRepository → SqlAlchemyRepository
- `data/loaders.py` - Remove JSON loading, use database
- Delete `data/input/competitor_data.json`

#### 2. **Convert FactRepository to Async**
**Current**: Sync pattern with session.commit()  
**Should Be**: Async pattern with await session.commit()

**Changes Needed**:
```python
# BEFORE (Sync)
def create_batch(self, company_id: str) -> GatheringBatch:
    session = self.db_manager.get_session()
    batch = GatheringBatch(...)
    session.add(batch)
    session.commit()  # ❌ Sync
    return batch

# AFTER (Async)
async def create_batch(self, company_id: str) -> GatheringBatch:
    async with self.db_manager.get_session() as session:
        batch = GatheringBatch(...)
        session.add(batch)
        await session.commit()  # ✅ Async
        return batch
```

#### 3. **Unify Repository Pattern**
**Current**: 3 different patterns (SQLAlchemy sync, Supabase client, JSON file)  
**Should Be**: Single async SQLAlchemy pattern

**Recommendation**: Standardize on:
- Async SQLAlchemy with AsyncSession
- Repository pattern with dependency injection
- Consistent error handling

### MEDIUM PRIORITY (Fix Soon)

#### 4. **Add Missing Migrations**
**Gap**: 18 SQLAlchemy models but only 14 migration tables  
**Missing Tables**:
- scoring_records
- signal_records
- market_snapshots
- audit_trail_records
- enrichment_audit_records
- enrichment_cache_records
- enrichment_job_records

#### 5. **Add Foreign Key Constraints**
**Current**: Some relationships use string references without FK constraints  
**Should Be**: Proper foreign keys with ON DELETE CASCADE

#### 6. **Improve Index Strategy**
**Current**: Basic indexes on tier, industry, classification  
**Should Add**:
- Index on companies.name (for search)
- Index on companies.created_at (for sorting)
- Composite indexes for common query patterns
- Partial indexes for filtered queries

### LOW PRIORITY (Nice to Have)

#### 7. **Implement Event Outbox Pattern**
**Current**: outbox_records table exists but may not be fully utilized  
**Should**: Use for all async operations to ensure eventual consistency

#### 8. **Add Database Constraints**
- CHECK constraints for numeric ranges (e.g., confidence 0-1)
- NOT NULL constraints where appropriate
- Default values for timestamps

---

## 📈 DATA FLOW DIAGRAM

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Endpoint  │────▶│  Service Layer   │────▶│   Repository    │
│   (FastAPI)     │     │  (Async)         │     │   (SQLAlchemy)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                           │
                              ▼                           ▼
                       ┌──────────────────┐     ┌─────────────────┐
                       │   Domain Models  │     │   PostgreSQL    │
                       │   (Pydantic)     │     │   (Supabase)    │
                       └──────────────────┘     └─────────────────┘

CURRENT PROBLEM:
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Endpoint  │────▶│  Service Layer   │────▶│   Repository    │
│                 │     │                  │     │   (MIXED!)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                       ┌────────────┐          ┌──────────────┐          ┌──────────────┐
                       │ SQLAlchemy │          │ Supabase     │          │ JSON File    │
                       │ (Async)    │          │ Client       │          │ (Sync)       │
                       │ ✅         │          │ ⚠️          │          │ ❌          │
                       └────────────┘          └──────────────┘          └──────────────┘
```

---

## 🎯 RECOMMENDED ACTION PLAN

### Phase 1: Database Migration (Week 1)
1. ✅ **COMPLETED**: Create database configuration module
2. ✅ **COMPLETED**: Create async test infrastructure
3. 🔄 **NEXT**: Create migration script to load JSON data into companies table
4. 🔄 **NEXT**: Add missing table migrations (scoring, enrichment)

### Phase 2: Repository Unification (Week 2)
1. Convert FactRepository to async
2. Deprecate JsonFileRepository
3. Standardize all repositories on async SQLAlchemy
4. Update all services to use unified repositories

### Phase 3: Code Cleanup (Week 3)
1. Remove JSON file dependencies
2. Add missing database constraints
3. Optimize indexes
4. Update documentation

### Phase 4: Testing & Validation (Week 4)
1. Run full test suite
2. Verify data integrity
3. Performance testing
4. Deploy to production

---

## 📊 SUMMARY STATISTICS

| Metric | Count | Status |
|--------|-------|--------|
| Database Tables (Migrations) | 14 | ✅ |
| SQLAlchemy Models | 18 | ⚠️ (4 not in migrations) |
| Repository Classes | 5 | ⚠️ (mixed patterns) |
| Service Classes | 6 | ✅ |
| JSON Files with Data | 1 | ❌ (should be database) |
| Files Using JSON | 12 | ⚠️ (some appropriate) |
| API Endpoints | 20+ | ✅ |
| Test Files | 30+ | ✅ (recently converted to async) |

---

## ✅ WHAT'S ALREADY DONE

From the recent work:
1. ✅ Database configuration module (database_config.py)
2. ✅ Async test infrastructure (conftest.py, factories.py)
3. ✅ 4 test files converted to async/real database
4. ✅ CI/CD pipeline for database tests
5. ✅ Comprehensive documentation

---

## 🚀 NEXT IMMEDIATE ACTIONS

1. **Create data migration script** to load competitor_data.json into companies table
2. **Add missing migrations** for scoring/enrichment tables
3. **Convert FactRepository** from sync to async
4. **Deprecate JsonFileRepository** in favor of database queries
5. **Add foreign key constraints** to SQLAlchemy models

---

## 📚 RELATED DOCUMENTATION

- [SETUP.md](SETUP.md) - Project setup
- [TESTING.md](TESTING.md) - Testing guide
- [DATABASE.md](DATABASE.md) - Database schema
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

---

**Report Generated**: 2026-02-27  
**Analysis By**: Atlas Orchestrator  
**Status**: Ready for implementation phase
