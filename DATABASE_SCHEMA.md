# Solstein — Database Schema Reference

> Complete reference for all ORM models, relationships, constraints, and indexes.

---

## Overview

Solstein uses **PostgreSQL** (Supabase managed) with **SQLAlchemy 2.0 async** ORM.

| Attribute | Value |
|-----------|-------|
| Database | PostgreSQL 15+ |
| ORM | SQLAlchemy 2.0 (async) |
| Driver | asyncpg |
| Migrations | Alembic |
| Total Tables | 23 |
| Total ORM Models | 23 (across 2 files) |
| Migration Files | 12 |

---

## Table of Contents

1. [Core Tables](#core-tables)
2. [Facts & Data Collection Tables](#facts--data-collection-tables)
3. [Scoring & Analysis Tables](#scoring--analysis-tables)
4. [Research Pipeline Tables](#research-pipeline-tables)
5. [Enrichment Tables](#enrichment-tables)
6. [Audit & Reliability Tables](#audit--reliability-tables)
7. [Entity Relationship Diagram](#entity-relationship-diagram)
8. [Foreign Key Constraints](#foreign-key-constraints)
9. [Indexes & Performance](#indexes--performance)
10. [CHECK Constraints](#check-constraints)
11. [Migration History](#migration-history)

---

## Core Tables

### `companies`

The central table. All other tables reference this via `company_id`.

**ORM Model**: `CompanyRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE companies (
    company_id   VARCHAR PRIMARY KEY,
    name         VARCHAR NOT NULL,
    industry     VARCHAR,
    country      VARCHAR,
    website      VARCHAR,
    description  TEXT,
    metadata     JSONB,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);
```

**Key Fields**:
- `company_id` — Business identifier (e.g., `"eneve-001"`, `"sap-001"`)
- `metadata` — JSONB blob for flexible additional data (revenue timelines, funding rounds)
- `industry` — Market segment (e.g., `"energy_software"`, `"fintech"`)

**Example**:
```python
from solstein.infrastructure.database_models import CompanyRecord

company = CompanyRecord(
    company_id="eneve-001",
    name="Eneve Energy",
    industry="energy_software",
    country="DE",
)
session.add(company)
await session.commit()
```

---

## Facts & Data Collection Tables

### `gathering_batches`

Tracks data gathering sessions for companies. Each batch represents one run of the data collection pipeline.

**ORM Model**: `GatheringBatch` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE gathering_batches (
    batch_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    status       VARCHAR NOT NULL DEFAULT 'in_progress'
                 CHECK (status IN ('in_progress', 'completed', 'failed')),
    created_at   TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

**Indexes**:
- `idx_batches_company_id` on `(company_id)`
- `idx_batches_status` on `(status)`

---

### `facts`

Stores extracted facts about companies with confidence scores. The core data unit of the intelligence pipeline.

**ORM Model**: `Fact` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE facts (
    fact_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    batch_id   UUID NOT NULL REFERENCES gathering_batches(batch_id) ON DELETE CASCADE,
    fact_type  VARCHAR NOT NULL,
    value      NUMERIC,
    value_str  VARCHAR,
    confidence NUMERIC CHECK (confidence BETWEEN 0 AND 1),
    source     VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Fact Types** (common values):
| Type | Description | Value Field |
|------|-------------|-------------|
| `revenue` | Annual revenue in EUR | `value` (numeric) |
| `employees` | Headcount | `value` (numeric) |
| `growth_rate` | YoY revenue growth % | `value` (numeric) |
| `funding_total` | Total funding raised | `value` (numeric) |
| `github_stars` | GitHub repository stars | `value` (numeric) |
| `ai_maturity` | AI adoption score 0–10 | `value` (numeric) |
| `description` | Company description | `value_str` (text) |
| `tech_stack` | Technology stack | `value_str` (JSON array) |

**Indexes**:
- `idx_facts_company_id` on `(company_id)`
- `idx_facts_company_type` on `(company_id, fact_type)` — compound for filtered queries

**Example**:
```python
from solstein.domain.facts import Fact

fact = Fact(
    company_id="eneve-001",
    batch_id=batch.batch_id,
    fact_type="revenue",
    value=5_000_000.0,
    confidence=0.92,
    source="sec_edgar",
)
session.add(fact)
await session.commit()
```

---

### `fact_sources`

Source attribution for each fact. Links facts to their original data sources.

**ORM Model**: `FactSource` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE fact_sources (
    source_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact_id      UUID NOT NULL REFERENCES facts(fact_id) ON DELETE CASCADE,
    source_type  VARCHAR,
    url          VARCHAR,
    title        VARCHAR,
    retrieved_at TIMESTAMP DEFAULT NOW()
);
```

**Source Types**:
- `sec_edgar` — SEC EDGAR financial filings
- `companies_house` — UK Companies House
- `github` — GitHub repository data
- `news` — News articles
- `yahoo_finance` — Yahoo Finance market data
- `web_search` — General web search results

---

### `refresh_metadata`

Tracks data freshness for each company/source combination.

**ORM Model**: `RefreshMetadata` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE refresh_metadata (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    source_type  VARCHAR NOT NULL,
    last_refresh TIMESTAMP,
    next_refresh TIMESTAMP,
    refresh_count INTEGER DEFAULT 0,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

### `data_source_conflicts`

Records conflicts when two data sources disagree on the same fact.

**ORM Model**: `DataSourceConflict` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE data_source_conflicts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    fact_type    VARCHAR NOT NULL,
    source_a     VARCHAR NOT NULL,
    source_b     VARCHAR NOT NULL,
    value_a      NUMERIC,
    value_b      NUMERIC,
    delta_pct    NUMERIC,
    resolved     BOOLEAN DEFAULT FALSE,
    resolution   VARCHAR,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

### `confidence_calibration`

Stores calibration data for confidence score adjustments per source type.

**ORM Model**: `ConfidenceCalibration` in `src/solstein/domain/facts.py`

```sql
CREATE TABLE confidence_calibration (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type  VARCHAR NOT NULL,
    fact_type    VARCHAR NOT NULL,
    base_confidence NUMERIC CHECK (base_confidence BETWEEN 0 AND 1),
    calibration_factor NUMERIC,
    sample_size  INTEGER,
    updated_at   TIMESTAMP DEFAULT NOW()
);
```

---

## Scoring & Analysis Tables

### `scoring_records`

Stores AI-generated company scores. Each row is one scoring run for one company.

**ORM Model**: `ScoringRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE scoring_records (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id                  VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    company_name                VARCHAR,
    growth_score                NUMERIC CHECK (growth_score BETWEEN 0 AND 10),
    financial_health_score      NUMERIC CHECK (financial_health_score BETWEEN 0 AND 10),
    competitive_position_score  NUMERIC CHECK (competitive_position_score BETWEEN 0 AND 10),
    overall_score               NUMERIC CHECK (overall_score BETWEEN 0 AND 10),
    classification              VARCHAR CHECK (classification IN ('Phoenix', 'Salt', 'Lead')),
    scoring_timestamp           TIMESTAMP DEFAULT NOW(),
    scorer_version              VARCHAR,
    signal_breakdown            JSONB
);
```

**Classification Thresholds**:
| Classification | Overall Score | Meaning |
|---|---|---|
| 🔥 Phoenix | ≥ 7.0 | High-growth, AI-native |
| 🧂 Salt | 4.0 – 7.0 | Stable, watch for signals |
| ⚖️ Lead | ≤ 4.0 | Legacy weight |

**Indexes**:
- `idx_scoring_company_id` on `(company_id)`
- `idx_scoring_timestamp` on `(scoring_timestamp DESC)`

---

### `signal_records`

Individual signals that contribute to a company's score.

**ORM Model**: `SignalRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE signal_records (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    scoring_id   UUID REFERENCES scoring_records(id) ON DELETE CASCADE,
    signal_type  VARCHAR NOT NULL,
    signal_value NUMERIC,
    confidence   NUMERIC CHECK (confidence BETWEEN 0 AND 1),
    created_at   TIMESTAMP DEFAULT NOW()
);
```

**Signal Types**:
- `revenue_growth` — YoY revenue growth rate
- `github_velocity` — Commit frequency trend
- `ai_adoption` — AI/ML technology adoption score
- `funding_momentum` — Recent funding activity
- `team_growth` — Headcount growth rate

---

### `market_snapshots`

Stores market segment analysis snapshots.

**ORM Model**: `MarketSnapshot` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE market_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_segment  VARCHAR NOT NULL,
    snapshot_data   JSONB NOT NULL,
    company_count   INTEGER,
    avg_score       NUMERIC,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## Research Pipeline Tables

### `research_runs`

Tracks complete research pipeline executions.

**ORM Model**: `ResearchRunRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE research_runs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    run_type     VARCHAR NOT NULL,
    status       VARCHAR NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    started_at   TIMESTAMP,
    completed_at TIMESTAMP,
    error_msg    TEXT,
    metadata     JSONB,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
- `idx_research_runs_company_id` on `(company_id)`

---

### `research_stages`

Individual stages within a research run (e.g., GitHub fetch, news fetch, scoring).

**ORM Model**: `ResearchStageRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE research_stages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id       UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    stage_name   VARCHAR NOT NULL,
    status       VARCHAR NOT NULL DEFAULT 'pending',
    started_at   TIMESTAMP,
    completed_at TIMESTAMP,
    output       JSONB,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

### `research_artifacts`

Output artifacts produced by research stages (reports, data files, etc.).

**ORM Model**: `ResearchArtifactRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE research_artifacts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    artifact_type VARCHAR NOT NULL,
    content       JSONB,
    file_path     VARCHAR,
    created_at    TIMESTAMP DEFAULT NOW()
);
```

---

### `source_documents`

Raw source documents retrieved during research (HTML pages, PDFs, API responses).

**ORM Model**: `SourceDocumentRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE source_documents (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    source_type  VARCHAR NOT NULL,
    url          VARCHAR,
    content      TEXT,
    retrieved_at TIMESTAMP DEFAULT NOW()
);
```

---

### `metric_observations`

Time-series metric observations for companies.

**ORM Model**: `MetricObservationRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE metric_observations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    metric_name  VARCHAR NOT NULL,
    metric_value NUMERIC,
    observed_at  TIMESTAMP NOT NULL,
    source       VARCHAR,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
- `idx_metric_observations_company_id` on `(company_id)`

---

### `evidence_readiness`

Tracks evidence quality and readiness for scoring decisions.

**ORM Model**: `EvidenceReadinessRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE evidence_readiness (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    dimension       VARCHAR NOT NULL,
    readiness_score NUMERIC CHECK (readiness_score BETWEEN 0 AND 1),
    fact_count      INTEGER DEFAULT 0,
    source_count    INTEGER DEFAULT 0,
    assessed_at     TIMESTAMP DEFAULT NOW()
);
```

---

### `research_contradictions`

Records contradictions detected between data sources.

**ORM Model**: `ContradictionRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE research_contradictions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    fact_type    VARCHAR NOT NULL,
    source_a     VARCHAR NOT NULL,
    source_b     VARCHAR NOT NULL,
    value_a      JSONB,
    value_b      JSONB,
    severity     VARCHAR CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status       VARCHAR DEFAULT 'open',
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

### `research_contradiction_transitions`

Audit trail for contradiction resolution state changes.

**ORM Model**: `ContradictionTransitionRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE research_contradiction_transitions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contradiction_id  UUID NOT NULL REFERENCES research_contradictions(id) ON DELETE CASCADE,
    from_status       VARCHAR,
    to_status         VARCHAR NOT NULL,
    reason            TEXT,
    transitioned_at   TIMESTAMP DEFAULT NOW()
);
```

---

## Enrichment Tables

### `enrichment_audit_trail`

Audit trail for all enrichment operations.

**ORM Model**: `EnrichmentAuditRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE enrichment_audit_trail (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id     VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    operation_type VARCHAR NOT NULL,
    status         VARCHAR NOT NULL,
    details        JSONB,
    duration_ms    INTEGER,
    created_at     TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
- `idx_enrichment_company_id` on `(company_id)`

---

### `enrichment_cache`

Caches enrichment data to avoid redundant API calls.

**ORM Model**: `EnrichmentCacheRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE enrichment_cache (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    cache_key    VARCHAR NOT NULL,
    cache_data   JSONB NOT NULL,
    expires_at   TIMESTAMP NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW(),
    UNIQUE (company_id, cache_key)
);
```

---

### `enrichment_jobs`

Job queue for enrichment operations.

**ORM Model**: `EnrichmentJobRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE enrichment_jobs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id   VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    job_type     VARCHAR NOT NULL,
    status       VARCHAR NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    priority     INTEGER DEFAULT 5,
    payload      JSONB,
    result       JSONB,
    error_msg    TEXT,
    scheduled_at TIMESTAMP,
    started_at   TIMESTAMP,
    completed_at TIMESTAMP,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

---

## Audit & Reliability Tables

### `audit_trails`

General audit trail for company analysis operations.

**ORM Model**: `AuditTrailRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE audit_trails (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          VARCHAR NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    company_name        VARCHAR,
    scoring_timestamp   TIMESTAMP,
    scorer_version      VARCHAR,
    data_sources_used   JSONB,
    created_at          TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
- `idx_audit_company_id` on `(company_id)`

---

### `outbox_records`

Transactional outbox for reliable event publishing (prevents lost events on crash).

**ORM Model**: `OutboxRecord` in `src/solstein/infrastructure/database_models.py`

```sql
CREATE TABLE outbox_records (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type   VARCHAR NOT NULL,
    payload      JSONB NOT NULL,
    status       VARCHAR NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'processing', 'published', 'failed')),
    attempts     INTEGER DEFAULT 0,
    last_error   TEXT,
    created_at   TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP
);
```

**Indexes**:
- `idx_outbox_status` on `(status)` — for outbox processor polling

---

## Entity Relationship Diagram

```
companies (PK: company_id)
    │
    ├── gathering_batches (FK: company_id)
    │       │
    │       └── facts (FK: company_id, batch_id)
    │               │
    │               └── fact_sources (FK: fact_id, CASCADE)
    │
    ├── scoring_records (FK: company_id)
    │       │
    │       └── signal_records (FK: company_id, scoring_id)
    │
    ├── research_runs (FK: company_id)
    │       ├── research_stages (FK: run_id, CASCADE)
    │       └── research_artifacts (FK: run_id, CASCADE)
    │
    ├── research_contradictions (FK: company_id)
    │       └── research_contradiction_transitions (FK: contradiction_id, CASCADE)
    │
    ├── enrichment_audit_trail (FK: company_id)
    ├── enrichment_cache (FK: company_id, UNIQUE: company_id+cache_key)
    ├── enrichment_jobs (FK: company_id)
    │
    ├── audit_trails (FK: company_id)
    ├── source_documents (FK: company_id)
    ├── metric_observations (FK: company_id)
    ├── evidence_readiness (FK: company_id)
    ├── refresh_metadata (FK: company_id)
    └── data_source_conflicts (FK: company_id)

market_snapshots (independent — no FK to companies)
outbox_records (independent — event bus)
confidence_calibration (independent — calibration data)
```

---

## Foreign Key Constraints

All foreign keys are defined with explicit constraint names for easy identification in error messages.

| Constraint Name | Child Table | Child Column | Parent Table | Parent Column | On Delete |
|-----------------|-------------|--------------|--------------|---------------|-----------|
| `fk_batches_companies` | `gathering_batches` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_facts_companies` | `facts` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_facts_batches` | `facts` | `batch_id` | `gathering_batches` | `batch_id` | CASCADE |
| `fk_fact_sources_facts` | `fact_sources` | `fact_id` | `facts` | `fact_id` | CASCADE |
| `fk_scoring_companies` | `scoring_records` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_signals_companies` | `signal_records` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_signals_scoring` | `signal_records` | `scoring_id` | `scoring_records` | `id` | CASCADE |
| `fk_research_runs_companies` | `research_runs` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_research_stages_runs` | `research_stages` | `run_id` | `research_runs` | `id` | CASCADE |
| `fk_research_artifacts_runs` | `research_artifacts` | `run_id` | `research_runs` | `id` | CASCADE |
| `fk_contradictions_companies` | `research_contradictions` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_contradiction_transitions` | `research_contradiction_transitions` | `contradiction_id` | `research_contradictions` | `id` | CASCADE |
| `fk_enrichment_audit_companies` | `enrichment_audit_trail` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_enrichment_cache_companies` | `enrichment_cache` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_enrichment_jobs_companies` | `enrichment_jobs` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_audit_trails_companies` | `audit_trails` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_source_docs_companies` | `source_documents` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_metric_obs_companies` | `metric_observations` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_evidence_companies` | `evidence_readiness` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_refresh_metadata_companies` | `refresh_metadata` | `company_id` | `companies` | `company_id` | CASCADE |
| `fk_conflicts_companies` | `data_source_conflicts` | `company_id` | `companies` | `company_id` | CASCADE |

---

## Indexes & Performance

All indexes were added in migration `011_optimize_database_indexes.py`.

| Index Name | Table | Columns | Purpose |
|------------|-------|---------|---------|
| `idx_facts_company_id` | `facts` | `(company_id)` | Fact lookups by company |
| `idx_facts_company_type` | `facts` | `(company_id, fact_type)` | Filtered fact queries |
| `idx_batches_company_id` | `gathering_batches` | `(company_id)` | Batch lookups |
| `idx_batches_status` | `gathering_batches` | `(status)` | Status filtering |
| `idx_scoring_company_id` | `scoring_records` | `(company_id)` | Scoring lookups |
| `idx_scoring_timestamp` | `scoring_records` | `(scoring_timestamp DESC)` | Time-series queries |
| `idx_audit_company_id` | `audit_trails` | `(company_id)` | Audit trail queries |
| `idx_enrichment_company_id` | `enrichment_audit_trail` | `(company_id)` | Enrichment lookups |
| `idx_research_runs_company_id` | `research_runs` | `(company_id)` | Research run queries |
| `idx_metric_observations_company_id` | `metric_observations` | `(company_id)` | Metric queries |
| `idx_outbox_status` | `outbox_records` | `(status)` | Outbox processor polling |

### Query Performance Targets

| Query Pattern | Index Used | Target |
|---------------|-----------|--------|
| `SELECT * FROM companies WHERE company_id = ?` | PK | <5ms |
| `SELECT * FROM facts WHERE company_id = ?` | `idx_facts_company_id` | <20ms |
| `SELECT * FROM facts WHERE company_id = ? AND fact_type = ?` | `idx_facts_company_type` | <10ms |
| `SELECT * FROM scoring_records WHERE company_id = ? ORDER BY scoring_timestamp DESC LIMIT 1` | `idx_scoring_company_id` + `idx_scoring_timestamp` | <15ms |
| `SELECT * FROM outbox_records WHERE status = 'pending'` | `idx_outbox_status` | <10ms |

---

## CHECK Constraints

Added in migration `010_add_database_constraints.py`.

| Table | Column | Constraint |
|-------|--------|------------|
| `facts` | `confidence` | `BETWEEN 0 AND 1` |
| `signal_records` | `confidence` | `BETWEEN 0 AND 1` |
| `scoring_records` | `growth_score` | `BETWEEN 0 AND 10` |
| `scoring_records` | `financial_health_score` | `BETWEEN 0 AND 10` |
| `scoring_records` | `competitive_position_score` | `BETWEEN 0 AND 10` |
| `scoring_records` | `overall_score` | `BETWEEN 0 AND 10` |
| `scoring_records` | `classification` | `IN ('Phoenix', 'Salt', 'Lead')` |
| `gathering_batches` | `status` | `IN ('in_progress', 'completed', 'failed')` |
| `research_runs` | `status` | `IN ('pending', 'in_progress', 'completed', 'failed')` |
| `enrichment_jobs` | `status` | `IN ('pending', 'in_progress', 'completed', 'failed')` |
| `outbox_records` | `status` | `IN ('pending', 'processing', 'published', 'failed')` |
| `evidence_readiness` | `readiness_score` | `BETWEEN 0 AND 1` |
| `confidence_calibration` | `base_confidence` | `BETWEEN 0 AND 1` |
| `research_contradictions` | `severity` | `IN ('low', 'medium', 'high', 'critical')` |

---

## Migration History

| File | Revision | Description |
|------|----------|-------------|
| `001_initial_schema.py` | 001 | Initial schema setup |
| `002_add_companies_table.py` | 002 | Core companies table |
| `003_add_facts_tables.py` | 003 | gathering_batches, facts, fact_sources |
| `004_add_enrichment_audit_cache_tables.py` | 004 | enrichment_audit_trail, enrichment_cache |
| `005_add_research_tables.py` | 005 | research_runs, research_stages, research_artifacts |
| `006_add_enrichment_job_table.py` | 006 | enrichment_jobs |
| `007_add_evidence_readiness_table.py` | 007 | evidence_readiness |
| `008_add_metric_outbox_contradiction_tables.py` | 008 | metric_observations, outbox_records, research_contradictions, research_contradiction_transitions |
| `009_add_foreign_key_constraints.py` | 009 | FK constraints on enrichment tables |
| `010_add_database_constraints.py` | 010 | CHECK constraints, standardized PKs |
| `011_optimize_database_indexes.py` | 011 | 11 performance indexes |
| `E2a_add_refresh_conflict_confidence_tables.py` | E2a | refresh_metadata, data_source_conflicts, confidence_calibration |

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Check current revision
alembic current

# Show migration history
alembic history

# Rollback one step
alembic downgrade -1
```

---

## Common Query Patterns

### Get all facts for a company

```python
from sqlalchemy import select
from solstein.domain.facts import Fact

result = await session.execute(
    select(Fact).where(Fact.company_id == "eneve-001")
)
facts = result.scalars().all()
```

### Get facts by type with confidence filter

```python
result = await session.execute(
    select(Fact).where(
        Fact.company_id == "eneve-001",
        Fact.fact_type == "revenue",
        Fact.confidence >= 0.8,
    ).order_by(Fact.created_at.desc())
)
revenue_facts = result.scalars().all()
```

### Get latest scoring for a company

```python
from solstein.infrastructure.database_models import ScoringRecord

result = await session.execute(
    select(ScoringRecord)
    .where(ScoringRecord.company_id == "eneve-001")
    .order_by(ScoringRecord.scoring_timestamp.desc())
    .limit(1)
)
latest_score = result.scalar_one_or_none()
```

### Get pending enrichment jobs

```python
from solstein.infrastructure.database_models import EnrichmentJobRecord

result = await session.execute(
    select(EnrichmentJobRecord)
    .where(EnrichmentJobRecord.status == "pending")
    .order_by(EnrichmentJobRecord.priority.desc(), EnrichmentJobRecord.created_at.asc())
    .limit(10)
)
jobs = result.scalars().all()
```

### Get market snapshot with company count

```python
from sqlalchemy import func
from solstein.infrastructure.database_models import MarketSnapshot

result = await session.execute(
    select(MarketSnapshot)
    .where(MarketSnapshot.market_segment == "energy_software")
    .order_by(MarketSnapshot.created_at.desc())
    .limit(1)
)
snapshot = result.scalar_one_or_none()
```

---

## Related Documentation

- [DATABASE.md](DATABASE.md) — Connection configuration, pool settings, backup/restore
- [TESTING.md](TESTING.md) — How to write database tests
- [PROFESSIONALIZATION.md](PROFESSIONALIZATION.md) — Schema evolution history
- [SETUP.md](SETUP.md) — Project setup including database configuration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common database issues

---

*Schema documented: February 2026*  
*Built by AI Whisperers — finding the diamonds nobody knew were there.*
