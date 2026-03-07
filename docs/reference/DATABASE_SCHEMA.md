# Solstein Database Schema Reference

> **Version**: 2026-03-01  
> **Source of truth**: `src/solstein/infrastructure/database_models.py`  
> **Engine**: PostgreSQL 14+ via SQLAlchemy 2.0 (async) + asyncpg  
> **Tables**: 18 total across 3 functional groups

---

## Table of Contents

1. [Connection & Configuration](#connection--configuration)
2. [Competitive Intelligence Tables (Integer PKs)](#competitive-intelligence-tables)
3. [Research Pipeline Tables (UUID PKs)](#research-pipeline-tables)
4. [Infrastructure Tables (UUID PKs)](#infrastructure-tables)
5. [Indexes Summary](#indexes-summary)
6. [Relationships Diagram](#relationships-diagram)
7. [ORM Import Reference](#orm-import-reference)

---

## Connection & Configuration

```env
# .env (double underscore = pydantic-settings nested model)
DATABASE__URL=postgresql+asyncpg://user:password@localhost:5432/solstein
DATABASE__POOL_SIZE=20       # default
DATABASE__MAX_OVERFLOW=10    # default
DATABASE__POOL_TIMEOUT=30    # seconds, default
```

```python
# src/solstein/infrastructure/database.py
from solstein.infrastructure.database import get_async_session, init_db

# Initialize all tables
import asyncio
asyncio.run(init_db())
```

---

## Competitive Intelligence Tables

Eight tables with **Integer** primary keys. These form the core analytics domain.

---

### 1. `companies` — `CompanyRecord`

Core company profiles with AI scores, financial metrics, and competitive classification.

```sql
CREATE TABLE companies (
    id                          SERIAL PRIMARY KEY,
    company_id                  TEXT UNIQUE NOT NULL,           -- e.g. "acme-corp"
    name                        TEXT NOT NULL,
    industry                    TEXT DEFAULT 'Energy Software',
    hq                          TEXT,
    website                     TEXT,
    description                 TEXT,

    -- Classification
    tier                        TEXT,                           -- TIER_1..TIER_4
    threat_level                TEXT,                           -- LOW/MEDIUM/HIGH/CRITICAL
    classification              TEXT,                           -- Phoenix/Salt/Lead

    -- AI Maturity
    ai_maturity                 TEXT,                           -- NONE/LOW/MODERATE/STRONG/VERY_STRONG
    saas_maturity               TEXT,
    ai_score                    FLOAT,
    ai_signal_level             TEXT,
    ai_key_capabilities         TEXT[],                         -- ARRAY
    ai_in_production            BOOLEAN,

    -- Revenue Metrics
    revenue_eur_m               FLOAT,
    revenue_confidence          TEXT,                           -- ConfidenceLevel enum
    growth_rate_pct             FLOAT,
    growth_confidence           TEXT,
    profit_margin_pct           FLOAT,
    ebitda_margin_pct           FLOAT,
    recurring_revenue_pct       FLOAT,
    revenue_per_employee_eur_k  FLOAT,
    revenue_timeline            JSONB,                          -- {year: revenue_m}
    revenue_cagr_3yr            FLOAT,
    revenue_cagr_5yr            FLOAT,

    -- Funding
    funding_rounds              JSONB,                          -- [{round, amount, date}]
    total_funding_raised_eur    FLOAT,
    latest_valuation_eur        FLOAT,
    lead_investors              TEXT[],
    funding_war_chest           FLOAT,

    -- Workforce
    employee_count              INTEGER,
    employee_cagr_3yr           FLOAT,
    open_positions              INTEGER,

    -- Financial Details
    profitability_raw_metrics   JSONB,

    -- Data Provenance
    data_availability           TEXT,
    data_source                 TEXT,

    -- Composite Scores
    growth_score                FLOAT,
    financial_health_score      FLOAT,
    competitive_position_score  FLOAT,
    composite_score             FLOAT,
    scoring_breakdown           JSONB,

    -- Timestamps
    last_updated                TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at                  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Indexes:**
```sql
CREATE INDEX ix_companies_name               ON companies (name);
CREATE INDEX ix_companies_industry           ON companies (industry);
CREATE INDEX ix_companies_hq                 ON companies (hq);
CREATE INDEX ix_companies_tier               ON companies (tier);
CREATE INDEX ix_companies_classification     ON companies (classification);
CREATE INDEX ix_companies_ai_score           ON companies (ai_score);
CREATE INDEX ix_companies_composite_score    ON companies (composite_score);
CREATE INDEX ix_companies_revenue_eur_m      ON companies (revenue_eur_m);
CREATE INDEX ix_companies_growth_rate_pct    ON companies (growth_rate_pct);
CREATE INDEX ix_companies_last_updated       ON companies (last_updated);
CREATE INDEX ix_companies_industry_hq        ON companies (industry, hq);
```

**Domain Enums (stored as TEXT):**

| Column | Valid Values |
|--------|-------------|
| `tier` | `TIER_1`, `TIER_2`, `TIER_3`, `TIER_4` |
| `threat_level` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `ai_maturity` | `NONE`, `LOW`, `MODERATE`, `STRONG`, `VERY_STRONG` |
| `revenue_confidence` | `CONFIRMED`, `ESTIMATED`, `UNKNOWN`, `SYNTHETIC` |

---

### 2. `scoring_records` — `ScoringRecord`

Point-in-time scoring snapshots for each company.

```sql
CREATE TABLE scoring_records (
    id                          SERIAL PRIMARY KEY,
    company_id                  INTEGER,                        -- logical ref (not FK)
    company_name                TEXT,
    growth_score                FLOAT,
    financial_health_score      FLOAT,
    competitive_position_score  FLOAT,
    overall_score               FLOAT,
    classification              TEXT,                           -- Phoenix/Salt/Lead
    scored_at                   TIMESTAMP WITH TIME ZONE DEFAULT now(),
    data_sources_used           JSONB                           -- list of source names
);

CREATE INDEX ix_scoring_records_company_id ON scoring_records (company_id);
```

**Relationships:**
- `signals` → one-to-many → `SignalRecord` (FK: `signal_records.scoring_record_id`)

---

### 3. `signal_records` — `SignalRecord`

Individual signals that drive each scoring record.

```sql
CREATE TABLE signal_records (
    id                  SERIAL PRIMARY KEY,
    scoring_record_id   INTEGER NOT NULL REFERENCES scoring_records(id) ON DELETE CASCADE,
    signal_name         TEXT,
    signal_category     TEXT,
    signal_value        FLOAT,
    signal_text         TEXT CHECK (length(signal_text) <= 2000),
    source_agent        TEXT,
    evidence            JSONB,                                  -- supporting evidence
    confidence          FLOAT,
    extracted_at        TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

---

### 4. `market_snapshots` — `MarketSnapshot`

Aggregate market state at a point in time.

```sql
CREATE TABLE market_snapshots (
    id                          SERIAL PRIMARY KEY,
    snapshot_date               TIMESTAMP WITH TIME ZONE DEFAULT now(),
    total_companies_scored      INTEGER,
    average_growth_score        FLOAT,
    average_financial_score     FLOAT,
    average_competitive_score   FLOAT,
    phoenix_count               INTEGER,                        -- high-threat classifications
    salt_count                  INTEGER,                        -- declining companies
    lead_count                  INTEGER,                        -- lead/prospect companies
    market_metadata             JSONB
);
```

---

### 5. `audit_trails` — `AuditTrailRecord`

Full per-company analysis audit trail capturing raw data through to final scores.

```sql
CREATE TABLE audit_trails (
    id                          SERIAL PRIMARY KEY,
    company_id                  INTEGER,
    gathering_batch_id          TEXT,
    company_name                TEXT,

    -- Data at each pipeline stage
    raw_data                    JSONB,
    aggregated_facts            JSONB,
    extracted_signals           JSONB,

    -- Scores
    growth_score                FLOAT,
    financial_health_score      FLOAT,
    competitive_position_score  FLOAT,
    classification              TEXT,
    scoring_breakdown           JSONB,

    -- Execution Metadata
    analysis_started_at         TIMESTAMP WITH TIME ZONE,
    analysis_completed_at       TIMESTAMP WITH TIME ZONE,
    analysis_duration_seconds   FLOAT,
    data_completeness           FLOAT,
    confidence_level            TEXT DEFAULT 'unknown',         -- ConfidenceLevel
    errors                      JSONB,                          -- list of error strings
    warnings                    JSONB,                          -- list of warning strings
    created_at                  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

---

### 6. `enrichment_cache` — `EnrichmentCacheRecord`

TTL-based enrichment result cache keyed by company.

```sql
CREATE TABLE enrichment_cache (
    id              SERIAL PRIMARY KEY,
    company_id      TEXT UNIQUE NOT NULL,                       -- cache key
    enriched_data   JSONB,                                      -- merged enrichment payload
    sources_used    JSONB,                                      -- list of adapter names
    fields_enriched JSONB,                                      -- list of field names updated
    cached_at       TIMESTAMP WITH TIME ZONE DEFAULT now(),
    ttl_seconds     INTEGER DEFAULT 86400,                      -- 24 hours default
    expires_at      TIMESTAMP WITH TIME ZONE,
    hits            INTEGER DEFAULT 0,                          -- access counter
    last_accessed_at TIMESTAMP WITH TIME ZONE
);
```

---

### 7. `enrichment_audit_trail` — `EnrichmentAuditRecord`

Per-operation enrichment audit log.

```sql
CREATE TABLE enrichment_audit_trail (
    id              SERIAL PRIMARY KEY,
    company_id      TEXT,
    company_name    TEXT,
    operation       TEXT,   -- 'enrich_start'|'enrich_success'|'enrich_failure'|'cache_hit'|'cache_miss'
    source          TEXT,   -- e.g. 'SEC_EDGAR', 'LINKEDIN', 'GITHUB'
    status          TEXT,   -- 'SUCCESS'|'FAILURE'|'SKIPPED'
    duration_ms     INTEGER,
    fields_enriched JSONB,
    error_message   TEXT,
    user_id         TEXT,
    client_id       TEXT,
    timestamp       TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX ix_enrichment_audit_company_ts  ON enrichment_audit_trail (company_id, timestamp);
CREATE INDEX ix_enrichment_audit_operation_ts ON enrichment_audit_trail (operation, timestamp);
```

**Valid `operation` values:** `enrich_start`, `enrich_success`, `enrich_failure`, `cache_hit`, `cache_miss`  
**Valid `status` values:** `SUCCESS`, `FAILURE`, `SKIPPED`  
**Valid `source` values** (from `DataSourceType`): `GITHUB`, `COMPANY_FILINGS`, `NEWS`, `CRUNCHBASE`, `LINKEDIN`, `PATENTS`, `WEBSITE`, `PRESS_RELEASE`, `YAHOO_FINANCE`, `EXA_SEARCH`, `GOOGLE_SEARCH`, `USPTO`, `GOOGLE_PATENTS`, `NEWSAPI`, `COMPETITOR_JSON`, `STATIC_CATALOG`

---

### 8. `enrichment_jobs` — `EnrichmentJobRecord`

Celery enrichment task tracking. **Note: `id` is a String (Celery task_id), not auto-increment.**

```sql
CREATE TABLE enrichment_jobs (
    id              TEXT PRIMARY KEY,                           -- Celery task_id (UUID string)
    company_id      TEXT,
    company_name    TEXT,
    job_type        TEXT,                                       -- 'single'|'batch'
    status          TEXT,                                       -- 'PENDING'|'RUNNING'|'SUCCESS'|'FAILED'
    progress        INTEGER DEFAULT 0,                          -- 0-100
    sources         JSONB,                                      -- list of source names to use
    batch_size      INTEGER,
    result_data     JSONB,
    error_message   TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT now(),
    started_at      TIMESTAMP WITH TIME ZONE,
    completed_at    TIMESTAMP WITH TIME ZONE,
    duration_ms     INTEGER,
    user_id         TEXT
);
```

**Note:** The `id` column stores the Celery task UUID (e.g. `"a1b2c3d4-..."`), not a database-generated integer.

---

## Research Pipeline Tables

Eight tables with **UUID** primary keys. These track the full research lifecycle.

---

### 9. `research_runs` — `ResearchRunRecord`

Top-level research run metadata. Parent of all other research tables.

```sql
CREATE TABLE research_runs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                  TEXT UNIQUE NOT NULL,               -- human-readable identifier
    market                  TEXT,
    seed_company            TEXT,
    status                  TEXT DEFAULT 'completed',
    strict_provenance       BOOLEAN,
    min_readiness_score     FLOAT,
    max_contradictions      INTEGER,
    min_total_sources       INTEGER,
    summary                 JSONB,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Relationships (all cascade delete):**
- `stages` → `research_stages.run_id`
- `artifacts` → `research_artifacts.run_id`
- `sources` → `source_documents.run_id`

---

### 10. `research_stages` — `ResearchStageRecord`

Per-stage execution tracking within a run.

```sql
CREATE TABLE research_stages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id      UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    stage_name  TEXT,
    stage_order INTEGER,
    status      TEXT,
    metrics     JSONB,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_research_stages_run_stage UNIQUE (run_id, stage_name)
);
```

---

### 11. `research_artifacts` — `ResearchArtifactRecord`

Artifacts (files, exports, reports) produced by a research run.

```sql
CREATE TABLE research_artifacts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    artifact_name   TEXT,
    artifact_path   TEXT,
    payload         JSONB,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_research_artifacts_run_name UNIQUE (run_id, artifact_name)
);
```

---

### 12. `source_documents` — `SourceDocumentRecord`

Source URLs observed per company during a research run.

```sql
CREATE TABLE source_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id      TEXT,
    source_url      TEXT,
    source_domain   TEXT,
    source_type     TEXT,                                       -- DataSourceType enum
    observed_at     TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status          TEXT DEFAULT 'observed',
    fetched_at      TIMESTAMP WITH TIME ZONE,
    content_hash    TEXT,
    extract_hash    TEXT,

    CONSTRAINT uq_source_documents_run_company_url UNIQUE (run_id, company_id, source_url)
);
```

---

### 13. `metric_observations` — `MetricObservationRecord`

Individual metric values extracted from sources.

```sql
CREATE TABLE metric_observations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id          TEXT,
    metric_key          TEXT,
    metric_value        TEXT,
    metric_value_raw    JSONB,                                  -- original parsed value
    source_url          TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_metric_obs_run_company_metric_url_val
        UNIQUE (run_id, company_id, metric_key, source_url, metric_value)
);
```

---

### 14. `evidence_readiness` — `EvidenceReadinessRecord`

Evidence quality scores per company per run.

```sql
CREATE TABLE evidence_readiness (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id                  UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id              TEXT,
    company_name            TEXT,
    readiness_score         FLOAT,
    readiness_level         TEXT,                               -- e.g. 'high', 'medium', 'low'
    source_count            INTEGER,
    source_domain_count     INTEGER,
    metric_source_coverage  FLOAT,
    metric_explainability   FLOAT,
    unsupported_metrics     JSONB,                              -- metrics with no evidence
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_evidence_readiness_run_company UNIQUE (run_id, company_id)
);
```

---

### 15. `research_contradictions` — `ContradictionRecord`

Detected data conflicts between sources.

```sql
CREATE TABLE research_contradictions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
    company_id          TEXT,
    metric_key          TEXT,
    contradiction_type  TEXT,
    details             JSONB,
    status              TEXT DEFAULT 'open',                    -- 'open'|'resolved'|'ignored'
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT now(),
    resolved_at         TIMESTAMP WITH TIME ZONE,
    ignored_at          TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT uq_contradiction_run_company_metric_type
        UNIQUE (run_id, company_id, metric_key, contradiction_type)
);
```

**Relationships:**
- `transitions` → one-to-many → `ContradictionTransitionRecord`

---

### 16. `research_contradiction_transitions` — `ContradictionTransitionRecord`

Status change history for contradictions.

```sql
CREATE TABLE research_contradiction_transitions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contradiction_id    UUID NOT NULL REFERENCES research_contradictions(id) ON DELETE CASCADE,
    from_status         TEXT,
    to_status           TEXT,
    changed_at          TIMESTAMP WITH TIME ZONE DEFAULT now(),
    changed_by          TEXT,
    reason              TEXT
);
```

---

## Infrastructure Tables

Two tables with **UUID** primary keys for platform reliability and multi-tenancy.

---

### 17. `outbox_records` — `OutboxRecord`

Transactional outbox for reliable event publishing (at-least-once delivery).

```sql
CREATE TABLE outbox_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_key       TEXT UNIQUE NOT NULL,                       -- idempotency key
    event_type      TEXT,
    status          TEXT DEFAULT 'pending',                     -- 'pending'|'processing'|'done'|'failed'
    payload         JSONB,
    attempt_count   INTEGER DEFAULT 0,
    available_at    TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_error      JSONB
);

CREATE INDEX ix_outbox_status_available ON outbox_records (status, available_at);
```

---

### 18. `tenants` — `TenantRecord`

Multi-tenant API key registry.

```sql
CREATE TABLE tenants (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT UNIQUE NOT NULL,
    api_key_hash        TEXT UNIQUE NOT NULL,                   -- SHA-256 hex (64 chars)
    is_active           BOOLEAN DEFAULT TRUE,
    plan                TEXT DEFAULT 'free',                    -- 'free'|'standard'|'enterprise'
    rate_limit_per_min  INTEGER DEFAULT 60,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Security:** API keys are hashed with SHA-256 before storage. The raw key is only returned at creation time and never stored.

**Rate limits by plan:**

| Plan | Default Rate Limit |
|------|--------------------|
| `free` | 60 req/min |
| `standard` | 60 req/min (configurable) |
| `enterprise` | 60 req/min (configurable) |

---

## Indexes Summary

| Table | Index | Columns |
|-------|-------|---------|
| `companies` | `ix_companies_name` | `name` |
| `companies` | `ix_companies_industry` | `industry` |
| `companies` | `ix_companies_hq` | `hq` |
| `companies` | `ix_companies_tier` | `tier` |
| `companies` | `ix_companies_classification` | `classification` |
| `companies` | `ix_companies_ai_score` | `ai_score` |
| `companies` | `ix_companies_composite_score` | `composite_score` |
| `companies` | `ix_companies_revenue_eur_m` | `revenue_eur_m` |
| `companies` | `ix_companies_growth_rate_pct` | `growth_rate_pct` |
| `companies` | `ix_companies_last_updated` | `last_updated` |
| `companies` | `ix_companies_industry_hq` | `(industry, hq)` |
| `scoring_records` | `ix_scoring_records_company_id` | `company_id` |
| `enrichment_audit_trail` | `ix_enrichment_audit_company_ts` | `(company_id, timestamp)` |
| `enrichment_audit_trail` | `ix_enrichment_audit_operation_ts` | `(operation, timestamp)` |
| `outbox_records` | `ix_outbox_status_available` | `(status, available_at)` |
| All UUID tables | Automatic PK index | `id` (UUID) |
| `tenants` | Unique constraint | `name`, `api_key_hash` |
| `research_runs` | Unique constraint | `run_id` |

---

## Relationships Diagram

```
companies (Integer PK)
    └── (logical reference by company_id TEXT) ──► scoring_records
                                                        └── signal_records

scoring_records (Integer PK)
    └── signal_records (FK: scoring_record_id)

research_runs (UUID PK)
    ├── research_stages         (FK: run_id, UNIQUE: run_id+stage_name)
    ├── research_artifacts      (FK: run_id, UNIQUE: run_id+artifact_name)
    ├── source_documents        (FK: run_id, UNIQUE: run_id+company_id+source_url)
    ├── metric_observations     (FK: run_id)
    ├── evidence_readiness      (FK: run_id, UNIQUE: run_id+company_id)
    └── research_contradictions (FK: run_id, UNIQUE: run_id+company_id+metric_key+type)
            └── research_contradiction_transitions (FK: contradiction_id)

tenants (UUID PK) ── rate_limit_per_min enforced by API middleware
outbox_records (UUID PK) ── processed by src/solstein/infrastructure/outbox_worker.py
enrichment_jobs (Text PK = Celery task_id) ── processed by Celery worker
```

---

## ORM Import Reference

```python
# All 18 models from one import
from solstein.infrastructure.database_models import (
    # Competitive Intelligence (Integer PKs)
    CompanyRecord,
    ScoringRecord,
    SignalRecord,
    MarketSnapshot,
    AuditTrailRecord,
    EnrichmentCacheRecord,
    EnrichmentAuditRecord,
    EnrichmentJobRecord,

    # Research Pipeline (UUID PKs)
    ResearchRunRecord,
    ResearchStageRecord,
    ResearchArtifactRecord,
    SourceDocumentRecord,
    MetricObservationRecord,
    EvidenceReadinessRecord,
    ContradictionRecord,
    ContradictionTransitionRecord,

    # Infrastructure (UUID PKs)
    OutboxRecord,
    TenantRecord,

    # SQLAlchemy base
    Base,
)

# Session usage
from solstein.infrastructure.database import get_async_session

async def example():
    async with get_async_session() as session:
        result = await session.execute(
            select(CompanyRecord).where(CompanyRecord.tier == "TIER_1")
        )
        companies = result.scalars().all()
```

---

## Quick Reference: Table Count by Group

| Group | Tables | PK Type |
|-------|--------|---------|
| Competitive Intelligence | 8 | Integer (SERIAL) |
| Research Pipeline | 8 | UUID |
| Infrastructure | 2 | UUID |
| **Total** | **18** | — |

---

*Schema source: `src/solstein/infrastructure/database_models.py`*  
*Last verified: 2026-03-01*
