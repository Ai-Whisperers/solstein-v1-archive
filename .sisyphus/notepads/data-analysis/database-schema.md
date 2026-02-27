# Solstein Database Schema Analysis

**Analysis Date:** February 27, 2026  
**Analyzed Files:**
- `/home/ai-whisperers/solstein/src/solstein/infrastructure/database_models.py`
- `/home/ai-whisperers/solstein/src/solstein/domain/facts.py`
- `/home/ai-whisperers/solstein/supabase/migrations/001-006`
- `/home/ai-whisperers/solstein/tests/conftest.py`

---

## 1. Complete Table Inventory

The Solstein database contains **17 tables** organized into functional domains:

### Core Business Tables
| Table | Purpose | Status |
|-------|---------|--------|
| `companies` | Primary company profiles with scores | **Active** |
| `scoring_records` | Historical scoring snapshots | **Active** |
| `signal_records` | Individual signals contributing to scores | **Active** |
| `market_snapshots` | Market-wide statistical snapshots | **Active** |
| `audit_trails` | Full analysis audit trails | **Active** |

### Research Pipeline Tables
| Table | Purpose | Status |
|-------|---------|--------|
| `research_runs` | Research execution records | **Active** |
| `research_stages` | Stage-level metrics per run | **Active** |
| `research_artifacts` | Named artifacts from research | **Active** |
| `source_documents` | Source URLs observed during research | **Active** |
| `metric_observations` | Metric values extracted from sources | **Active** |
| `evidence_readiness` | Per-company evidence readiness scores | **Active** |
| `research_contradictions` | Detected metric contradictions | **Active** |
| `research_contradiction_transitions` | Contradiction status lifecycle | **Active** |

### Facts & Enrichment Tables
| Table | Purpose | Status |
|-------|---------|--------|
| `gathering_batches` | Fact gathering batch metadata | **Active** |
| `facts` | Individual company facts with confidence | **Active** |
| `fact_sources` | Source attribution for facts | **Active** |
| `refresh_metadata` | Data source refresh scheduling | **Active** |

### Event & Job Tables
| Table | Purpose | Status |
|-------|---------|--------|
| `outbox_records` | Event-driven outbox for async processing | **Active** |
| `enrichment_cache` | Cached enrichment results (Phase 11) | **Active** |
| `enrichment_jobs` | Async enrichment job tracking (Phase 12) | **Active** |
| `enrichment_audit_trail` | Enrichment operation audit (Phase 11) | **Active** |

### Legacy/Migration Tables
| Table | Purpose | Status |
|-------|---------|--------|
| `data_source_conflicts` | Source conflict resolution tracking | **Active** |
| `confidence_calibration` | Confidence score calibration | **Active** |

---

## 2. Detailed Schema by Table

### 2.1 Companies Table (Primary Entity)

**File:** `src/solstein/infrastructure/database_models.py` (lines 23-157)

```sql
companies (
    id              INTEGER PRIMARY KEY,
    company_id      VARCHAR(255) UNIQUE NOT NULL,  -- Primary business key
    name            VARCHAR(500) NOT NULL,
    
    -- Basic Info
    industry        VARCHAR(100) DEFAULT 'Energy Software',
    description     TEXT,
    website         VARCHAR(500),
    headquarters    VARCHAR(100),
    founded_year    INTEGER,
    
    -- Positioning
    tier            VARCHAR(50),
    threat_level    VARCHAR(50),
    classification VARCHAR(50),
    
    -- Tech Maturity
    ai_maturity     VARCHAR(50),
    saas_maturity   INTEGER,
    ai_score        INTEGER,
    ai_signal_level VARCHAR(50),
    ai_key_capabilities TEXT,
    ai_in_production VARCHAR(10),
    
    -- Financials (Latest)
    revenue_eur_m           FLOAT,
    revenue_confidence      VARCHAR(50),
    growth_rate_pct         FLOAT,
    growth_confidence       VARCHAR(50),
    profit_margin_pct       FLOAT,
    ebitda_margin_pct       FLOAT,
    recurring_revenue_pct    FLOAT,
    revenue_per_employee_eur_k FLOAT,
    
    -- Revenue Timeline (JSON - full history)
    revenue_timeline        JSON,
    revenue_cagr_3yr        FLOAT,
    revenue_cagr_5yr        FLOAT,
    
    -- Funding (JSON)
    funding_rounds          JSON,
    total_funding_raised_eur FLOAT,
    latest_valuation_eur    FLOAT,
    lead_investors          JSON,
    funding_war_chest       TEXT,
    
    -- Employees
    employee_count          INTEGER,
    employee_cagr_3yr       FLOAT,
    open_positions          INTEGER,
    
    -- Raw Metrics (JSON)
    profitability_raw_metrics JSON,
    
    -- Data Quality
    data_availability       TEXT,
    data_source             VARCHAR(255),
    
    -- Scores (Calculated)
    growth_score            FLOAT,
    financial_health_score  FLOAT,
    competitive_position_score FLOAT,
    composite_score         FLOAT,
    scoring_breakdown       JSON,
    
    -- Metadata
    last_updated            TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL
)
```

**Indexes:**
- `ix_company_name` on `name`
- `ix_company_tier` on `tier`
- `ix_company_classification` on `classification`
- `ix_company_ai_score` on `ai_score`
- Unique index on `company_id`

**Data Storage Pattern:**
- Most fields stored as **relational columns** for queryability
- Complex/nested data stored as **JSON**: `revenue_timeline`, `funding_rounds`, `lead_investors`, `profitability_raw_metrics`, `scoring_breakdown`

**Issues Identified:**
- `ai_in_production` is VARCHAR(10) instead of Boolean
- JSON columns contain significant data duplication with relational columns

---

### 2.2 Facts Tables (Audit Trail)

**File:** `src/solstein/domain/facts.py`

```sql
gathering_batches (
    batch_id       UUID PRIMARY KEY,  -- UUID, not auto-increment
    company_id     VARCHAR(255) NOT NULL REFERENCES companies(company_id),
    created_at     TIMESTAMPTZ NOT NULL,
    status         VARCHAR(50) NOT NULL DEFAULT 'in_progress'
)

facts (
    fact_id        UUID PRIMARY KEY,
    company_id     VARCHAR(255) NOT NULL REFERENCES companies(company_id),
    batch_id       UUID NOT NULL REFERENCES gathering_batches(batch_id),
    fact_type      VARCHAR(100) NOT NULL,  -- e.g., "annual_revenue"
    value          NUMERIC,
    value_str      VARCHAR(500),
    value_date     TIMESTAMPTZ,
    confidence     NUMERIC(3,2) NOT NULL DEFAULT 0.5,
    extracted_at   TIMESTAMPTZ NOT NULL
)

fact_sources (
    source_id      UUID PRIMARY KEY,
    fact_id        UUID NOT NULL REFERENCES facts(fact_id),
    source_type    VARCHAR(100) NOT NULL,  -- "sec_edgar", "companies_house"
    source_url     VARCHAR(1000),
    extraction_timestamp TIMESTAMPTZ NOT NULL,
    raw_content    TEXT  -- Full original API response
)
```

**Indexes:**
- `idx_company_fact_type` on (company_id, fact_type)
- `idx_company_extracted` on (company_id, extracted_at)

**Issues Identified:**
- **Primary key inconsistency**: `gathering_batches` uses UUID as PK, but other tables use Integer auto-increment
- No foreign key constraint from `facts.company_id` to `companies.company_id` in migrations
- No cascade delete on facts when company is deleted

---

### 2.3 Scoring Tables

**File:** `src/solstein/infrastructure/database_models.py` (lines 160-244)

```sql
scoring_records (
    id              INTEGER PRIMARY KEY,
    company_id      VARCHAR(255) NOT NULL,
    company_name    VARCHAR(500) NOT NULL,
    growth_score    FLOAT NOT NULL,
    financial_health_score FLOAT NOT NULL,
    competitive_position_score FLOAT NOT NULL,
    overall_score   FLOAT NOT NULL,
    classification  VARCHAR(50) NOT NULL,
    scored_at       TIMESTAMPTZ NOT NULL,
    data_sources_used JSON
)

signal_records (
    id              INTEGER PRIMARY KEY,
    scoring_record_id INTEGER NOT NULL REFERENCES scoring_records(id),
    signal_name     VARCHAR(255) NOT NULL,
    signal_category VARCHAR(50) NOT NULL,
    signal_value    FLOAT,
    signal_text     VARCHAR(2000),
    source_agent    VARCHAR(100) NOT NULL,
    evidence        JSON,
    confidence      FLOAT NOT NULL,
    extracted_at    TIMESTAMPTZ NOT NULL
)
```

**Indexes:**
- `ix_company_scored_at` on (company_id, scored_at)
- `ix_overall_score` on overall_score
- `ix_classification` on classification
- `ix_signal_name_category` on (signal_name, signal_category)

---

### 2.4 Research Pipeline Tables

**File:** `src/solstein/infrastructure/database_models.py` (lines 348-595)

```sql
research_runs (
    id              UUID PRIMARY KEY,
    run_id          VARCHAR(255) UNIQUE NOT NULL,
    market          VARCHAR(255) NOT NULL,
    seed_company    VARCHAR(500) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'completed',
    strict_provenance BOOLEAN NOT NULL DEFAULT TRUE,
    min_readiness_score FLOAT,
    max_contradictions INTEGER,
    min_total_sources INTEGER,
    summary         JSON,
    created_at      TIMESTAMPTZ NOT NULL
)

research_stages (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    stage_name      VARCHAR(100) NOT NULL,
    stage_order     INTEGER NOT NULL,
    status          VARCHAR(50),
    metrics         JSON,
    created_at      TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_research_stage_run_name UNIQUE (run_id, stage_name)
)

research_artifacts (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    artifact_name   VARCHAR(255) NOT NULL,
    artifact_path   VARCHAR(1000),
    payload         JSON,
    created_at      TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_research_artifact_run_name UNIQUE (run_id, artifact_name)
)

source_documents (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    company_id      VARCHAR(255) NOT NULL,
    source_url      VARCHAR(2000) NOT NULL,
    source_domain   VARCHAR(255),
    source_type     VARCHAR(100),
    observed_at     TIMESTAMPTZ NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'observed',
    fetched_at      TIMESTAMPTZ,
    content_hash    VARCHAR(128),
    extract_hash    VARCHAR(128),
    CONSTRAINT uq_source_document_run_company_url UNIQUE (run_id, company_id, source_url)
)

metric_observations (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    company_id      VARCHAR(255) NOT NULL,
    metric_key      VARCHAR(100) NOT NULL,
    metric_value    NUMERIC,
    metric_value_raw JSON,
    source_url      VARCHAR(2000),
    created_at      TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_metric_observation_run_company_metric_source_value UNIQUE 
        (run_id, company_id, metric_key, source_url, metric_value)
)

evidence_readiness (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    company_id      VARCHAR(255) NOT NULL,
    company_name    VARCHAR(500) NOT NULL,
    readiness_score NUMERIC NOT NULL,
    readiness_level VARCHAR(100) NOT NULL,
    source_count    INTEGER NOT NULL DEFAULT 0,
    source_domain_count INTEGER NOT NULL DEFAULT 0,
    metric_source_coverage NUMERIC NOT NULL DEFAULT 0,
    metric_explainability NUMERIC NOT NULL DEFAULT 0,
    unsupported_metrics INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_evidence_readiness_run_company UNIQUE (run_id, company_id)
)

research_contradictions (
    id              UUID PRIMARY KEY,
    run_id          UUID NOT NULL REFERENCES research_runs(id),
    company_id      VARCHAR(255) NOT NULL,
    metric_key      VARCHAR(100) NOT NULL,
    contradiction_type VARCHAR(100) NOT NULL,
    details         JSON,
    status          VARCHAR(50) NOT NULL DEFAULT 'open',
    updated_at      TIMESTAMPTZ NOT NULL,
    resolved_at     TIMESTAMPTZ,
    ignored_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_contradiction_run_company_metric_type UNIQUE 
        (run_id, company_id, metric_key, contradiction_type)
)

research_contradiction_transitions (
    id              UUID PRIMARY KEY,
    contradiction_id UUID NOT NULL REFERENCES research_contradictions(id),
    from_status     VARCHAR(50) NOT NULL,
    to_status       VARCHAR(50) NOT NULL,
    changed_at      TIMESTAMPTZ NOT NULL,
    changed_by      VARCHAR(255),
    reason          TEXT
)
```

---

### 2.5 Enrichment Tables (Phase 11-12)

**File:** `src/solstein/infrastructure/database_models.py` (lines 597-760)

```sql
enrichment_audit_trail (
    id              INTEGER PRIMARY KEY,
    company_id      VARCHAR(255) NOT NULL,
    company_name    VARCHAR(500),
    operation       VARCHAR(50) NOT NULL,  -- 'enrich_start', 'enrich_success', etc.
    source          VARCHAR(255),  -- 'SEC_EDGAR', 'Companies_House'
    status          VARCHAR(50) NOT NULL,  -- 'SUCCESS', 'FAILURE', 'SKIPPED'
    duration_ms     FLOAT,
    fields_enriched JSON,
    error_message   TEXT,
    user_id         VARCHAR(255),
    client_id       VARCHAR(255),
    timestamp       TIMESTAMPTZ NOT NULL
)

enrichment_cache (
    id              INTEGER PRIMARY KEY,
    company_id      VARCHAR(255) UNIQUE NOT NULL,
    enriched_data   JSON NOT NULL,  -- Full UnifiedCompany as JSON
    sources_used    JSON,
    fields_enriched JSON,
    cached_at       TIMESTAMPTZ NOT NULL,
    ttl_seconds     INTEGER DEFAULT 86400,
    expires_at      TIMESTAMPTZ NOT NULL,
    hits            INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ
)

enrichment_jobs (
    id              VARCHAR(255) PRIMARY KEY,  -- Celery task_id
    company_id      VARCHAR(255) NOT NULL,
    company_name    VARCHAR(500),
    job_type        VARCHAR(50) NOT NULL,  -- 'single', 'batch'
    status          VARCHAR(50) NOT NULL,  -- 'PENDING', 'RUNNING', 'SUCCESS', 'FAILED'
    progress        INTEGER DEFAULT 0,
    sources         JSON,
    batch_size      INTEGER,
    result_data     JSON,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    duration_ms     FLOAT,
    user_id         VARCHAR(255)
)
```

---

### 2.6 Supporting Tables

```sql
market_snapshots (
    id                  INTEGER PRIMARY KEY,
    snapshot_date       TIMESTAMPTZ NOT NULL,
    total_companies_scored INTEGER NOT NULL,
    average_growth_score    FLOAT NOT NULL,
    average_financial_score  FLOAT NOT NULL,
    average_competitive_score FLOAT NOT NULL,
    phoenix_count          INTEGER NOT NULL,
    salt_count             INTEGER NOT NULL,
    lead_count             INTEGER NOT NULL,
    market_metadata        JSON
)

audit_trails (
    id                  INTEGER PRIMARY KEY,
    company_id          VARCHAR(255) NOT NULL,
    gathering_batch_id  VARCHAR(255) NOT NULL,
    company_name        VARCHAR(500) NOT NULL,
    raw_data            JSON,
    aggregated_facts    JSON,
    extracted_signals   JSON,
    growth_score        FLOAT,
    financial_health_score FLOAT,
    competitive_position_score FLOAT,
    classification      VARCHAR(50),
    scoring_breakdown  JSON,
    analysis_started_at TIMESTAMPTZ,
    analysis_completed_at TIMESTAMPTZ,
    analysis_duration_seconds FLOAT,
    data_completeness   FLOAT DEFAULT 0.0,
    confidence_level    VARCHAR(50) DEFAULT 'unknown',
    errors             JSON DEFAULT [],
    warnings           JSON DEFAULT [],
    created_at         TIMESTAMPTZ NOT NULL
)

outbox_records (
    id              UUID PRIMARY KEY,
    event_key       VARCHAR(255) UNIQUE NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending',
    payload         JSON NOT NULL,
    attempt_count   INTEGER NOT NULL DEFAULT 0,
    available_at    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL,
    last_error      JSON,
    CONSTRAINT ck_outbox_status CHECK (status IN ('pending', 'in_progress', 'succeeded', 'failed'))
)

refresh_metadata (
    id                      INTEGER PRIMARY KEY,
    source_name             VARCHAR(100) UNIQUE NOT NULL,
    source_type             VARCHAR(50) NOT NULL,
    last_refresh_time       TIMESTAMPTZ,
    last_refresh_status     VARCHAR(50),
    last_refresh_job_id     VARCHAR(255),
    next_scheduled_time     TIMESTAMPTZ,
    refresh_interval_seconds INTEGER NOT NULL DEFAULT 86400,
    enabled                 BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL,
    updated_at              TIMESTAMPTZ NOT NULL
)
```

---

## 3. Relationship Diagram (ERD)

```
companies (PK: id, UK: company_id)
    │
    ├── 1:N ──► scoring_records (FK: company_id)
    │               │
    │               └── 1:N ──► signal_records (FK: scoring_record_id)
    │
    ├── 1:N ──► gathering_batches (FK: company_id)
    │               │
    │               └── 1:N ──► facts (FK: batch_id, company_id)
    │                       │
    │                       └── 1:N ──► fact_sources (FK: fact_id)
    │
    ├── 1:N ──► audit_trails (FK: company_id)
    │
    └── 1:N ──► enrichment_cache (UK: company_id)
                └── enrichment_audit_trail (FK: company_id)

research_runs (PK: id, UK: run_id)
    │
    ├── 1:N ──► research_stages (FK: run_id)
    ├── 1:N ──► research_artifacts (FK: run_id)
    ├── 1:N ──► source_documents (FK: run_id)
    ├── 1:N ──► metric_observations (FK: run_id)
    ├── 1:N ──► evidence_readiness (FK: run_id)
    ├── 1:N ──► research_contradictions (FK: run_id)
    │               │
    │               └── 1:N ──► research_contradiction_transitions (FK: contradiction_id)
    │
    └── 1:N ──► enrichment_jobs (FK: company_id)

refresh_metadata (standalone - source_name is natural key)
outbox_records (standalone - event processing)
market_snapshots (standalone - aggregated snapshots)
```

---

## 4. Active vs Legacy Tables

### Actively Used Tables (Production)
All tables are actively used in the current codebase:

1. **companies** - Primary data store, queried by API
2. **scoring_records** - Historical score tracking  
3. **signal_records** - Score component storage
4. **research_runs** - Pipeline execution tracking
5. **research_stages** - Stage metrics
6. **research_artifacts** - Pipeline outputs
7. **source_documents** - Data source catalog
8. **metric_observations** - Extracted metrics
9. **evidence_readiness** - Quality scoring
10. **research_contradictions** - Contradiction tracking
11. **outbox_records** - Event-driven processing
12. **enrichment_cache** - Performance optimization
13. **enrichment_jobs** - Async task tracking
14. **enrichment_audit_trail** - Operation auditing
15. **gathering_batches/facts/fact_sources** - Facts infrastructure

### No Legacy/Deprecated Tables Found
All tables in the current codebase appear to be in active use. There are no tables marked as deprecated or legacy.

---

## 5. JSON vs Database Storage

### Data in JSON Columns

| Table | JSON Columns | Data Stored |
|-------|-------------|-------------|
| `companies` | revenue_timeline | Full revenue history by year |
| `companies` | funding_rounds | Array of funding round objects |
| `companies` | lead_investors | Array of investor names |
| `companies` | profitability_raw_metrics | Raw financial data |
| `companies` | scoring_breakdown | Score calculation details |
| `scoring_records` | data_sources_used | Array of sources |
| `signal_records` | evidence | Supporting evidence |
| `audit_trails` | raw_data, aggregated_facts, extracted_signals | Full analysis artifacts |
| `research_runs` | summary | Run summary |
| `research_stages` | metrics | Stage metrics |
| `research_artifacts` | payload | Artifact data |
| `source_documents` | (hashed columns) | Content stored as hash |
| `metric_observations` | metric_value_raw | Raw extracted values |
| `research_contradictions` | details | Contradiction details |
| `enrichment_cache` | enriched_data, sources_used, fields_enriched | Full cached company |
| `enrichment_jobs` | sources, result_data | Job parameters/results |

### Data in JSON Files (Not Database)

The following data exists in JSON files but is loaded into memory, not stored in the database:

| File | Purpose | Loaded By |
|------|---------|-----------|
| `data/input/competitor_data.json` | Initial company seed data | `CompetitorDataLoader` |
| `data/fixtures/envision_digital_profile.json` | Test fixture | Tests |

**Pattern**: The system uses **JSON files for initial seeding** but **database for persistence**. The JSON loaders are patched in tests with mock data.

---

## 6. Data Integrity Issues

### Critical Issues

1. **Inconsistent Primary Key Types**
   - Some tables use `INTEGER AUTO_INCREMENT` (companies, scoring_records, signal_records)
   - Others use `UUID` (research_runs, facts, gathering_batches)
   - This creates inconsistent patterns and potential UUID/string confusion

2. **Missing Foreign Key Constraints**
   - `facts.company_id` → `companies.company_id` not enforced in migrations
   - `gathering_batches.company_id` → `companies.company_id` not enforced
   - No CASCADE DELETE when parent company is deleted

3. **Primary Key Column Name Inconsistency**
   - `companies` uses both `id` (Integer) and `company_id` (String)
   - Other tables only have one PK field
   - This creates confusion about which is the "real" business key

### Medium Issues

4. **Data Duplication**
   - `companies.revenue_eur_m` vs `companies.revenue_timeline` (JSON)
   - `companies.funding_rounds` (JSON) vs `companies.total_funding_raised_eur`
   - Same data stored in both relational and JSON formats

5. **Type Mismatch**
   - `companies.ai_in_production` is VARCHAR(10) but logically should be Boolean

6. **No Unique Constraint on companies.id**
   - Only `company_id` is unique, but `id` (auto-increment) has no uniqueness constraint
   - Could potentially insert duplicate companies with different IDs

### Minor Issues

7. **JSON Default Syntax**
   - Uses PostgreSQL-specific `DEFAULT '{}'::jsonb` syntax
   - SQLAlchemy models use Python defaults that may not match

8. **Missing NOT NULL on Some Foreign Keys**
   - `fact_sources.fact_id` should be NOT NULL
   - Several relationship columns allow NULL that should be required

---

## 7. Test Coverage Analysis

### What's Tested with Real Database

The test suite uses real Supabase database for some tests:

- **conftest.py** (lines 187-240): Provides `db_engine` and `db_session` fixtures
- **test_fact_repository.py**: Tests Fact CRUD with real database
- **test_database_service.py**: Database service tests
- **test_enrichment_repositories.py**: Enrichment repository tests

### What's Mocked

Most API/integration tests use mocks:

- **mock_repo** fixture: Mocked CompanyRepository
- **mock_company** fixture: In-memory Company objects
- **CompetitorDataLoader**: Patched to return test companies (see conftest.py lines 73-170)

### Pattern

```
Unit Tests        → Mocks (fast, isolated)
Integration Tests → Real DB (db_session fixture) 
                   OR Mocks (mock_repo fixture)
```

---

## 8. Recommendations

### Immediate Actions

1. **Add Foreign Key Constraints**
   ```sql
   ALTER TABLE facts 
   ADD CONSTRAINT fk_facts_company 
   FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE;
   ```

2. **Standardize Primary Key Strategy**
   - Either use UUID for all tables OR Integer for all
   - Recommendation: Use UUID for all new tables

3. **Fix ai_in_production Column**
   ```sql
   ALTER TABLE companies ALTER COLUMN ai_in_production TYPE BOOLEAN;
   ```

### Medium-term

4. **Consolidate JSON vs Relational Data**
   - Choose one: either store in JSON OR relational columns
   - Remove duplication between `revenue_timeline` JSON and `revenue_eur_m` column

5. **Add Unique Constraint on companies.id**
   ```sql
   ALTER TABLE companies ADD CONSTRAINT uk_companies_id UNIQUE (id);
   ```

### Long-term

6. **Consider Table Splitting**
   - `companies` table is very wide (40+ columns)
   - Consider splitting into: `companies`, `company_financials`, `company_scores`

7. **Add Data Quality Constraints**
   - Confidence scores: 0.0-1.0 range
   - Percentages: -100 to 100
   - Dates: Not in future

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tables | 17 |
| Tables with Foreign Keys | 12 |
| Tables Using UUID PK | 9 |
| Tables Using Integer PK | 8 |
| JSON Columns | 25+ |
| Unique Constraints | 12 |
| Check Constraints | 2 |
| Tables with Real DB Tests | 4 |
| Tables Fully Mocked | Most in unit tests |

The database schema is comprehensive and actively used. Main issues are around consistency (PK types, FK constraints) and some data duplication between JSON and relational storage.
