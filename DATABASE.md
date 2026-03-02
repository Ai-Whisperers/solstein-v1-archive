# Solstein — Database Documentation

This document covers the database layer: connection setup, ORM overview, working with models, and practical query patterns. For the complete schema reference (all 18 tables with every column, index, and constraint), see [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).

---

## Overview

| Property | Value |
|---|---|
| **Engine** | PostgreSQL 14+ |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Driver** | asyncpg |
| **Tables** | 18 |
| **Connection pool** | pool_size=20, max_overflow=10, timeout=30s |
| **Migrations** | Manual (see `src/solstein/migrations/`) |

---

## Connection Setup

### Environment Variable

Solstein uses `pydantic-settings` with nested model configuration. The database URL uses **double underscores** as the separator:

```env
# .env
DATABASE__URL=postgresql+asyncpg://user:password@localhost:5432/solstein

# Optional tuning
DATABASE__POOL_SIZE=20
DATABASE__MAX_OVERFLOW=10
DATABASE__ECHO=false
```

> **Important:** Use `DATABASE__URL` (double underscore), not `DATABASE_URL` (single underscore). The double underscore is the pydantic-settings v2 nested model separator.

### Async Session Usage

```python
from solstein.infrastructure.database import get_async_session

async with get_async_session() as session:
    result = await session.execute(select(CompanyRecord).limit(10))
    companies = result.scalars().all()
```

---

## Schema Overview

Solstein has **18 tables** organized into three functional groups:

### Group 1: Competitive Intelligence (Integer PKs)

| Table | Model Class | Purpose |
|---|---|---|
| `companies` | `CompanyRecord` | Core company profiles + scoring (~42 columns) |
| `scoring_records` | `ScoringRecord` | Point-in-time scoring snapshots |
| `signal_records` | `SignalRecord` | Individual signals driving scores |
| `market_snapshots` | `MarketSnapshot` | Aggregate market state snapshots |
| `audit_trails` | `AuditTrailRecord` | Full analysis audit trail per company |
| `enrichment_cache` | `EnrichmentCacheRecord` | Cached enrichment data (TTL-based) |
| `enrichment_audit_trail` | `EnrichmentAuditRecord` | Enrichment operation audit log |
| `enrichment_jobs` | `EnrichmentJobRecord` | Celery enrichment task tracking |

### Group 2: Research Pipeline (UUID PKs)

| Table | Model Class | Purpose |
|---|---|---|
| `research_runs` | `ResearchRunRecord` | Top-level research run metadata |
| `research_stages` | `ResearchStageRecord` | Per-stage execution within a run |
| `research_artifacts` | `ResearchArtifactRecord` | Artifacts produced by a run |
| `source_documents` | `SourceDocumentRecord` | Source URLs observed per company |
| `metric_observations` | `MetricObservationRecord` | Individual metric values from sources |
| `evidence_readiness` | `EvidenceReadinessRecord` | Evidence quality scores per company |
| `research_contradictions` | `ContradictionRecord` | Detected data conflicts |
| `research_contradiction_transitions` | `ContradictionTransitionRecord` | Contradiction status change history |

### Group 3: Infrastructure (Mixed PKs)

| Table | Model Class | Purpose |
|---|---|---|
| `outbox_records` | `OutboxRecord` | Transactional outbox for event reliability (UUID) |
| `tenants` | `TenantRecord` | Multi-tenant API key management (UUID) |

---

## Key Design Decisions

### Two PK Strategies

- **Integer PKs** — competitive intelligence tables (companies, scoring_records, signal_records, market_snapshots, audit_trails, enrichment_*)
- **UUID PKs** — research pipeline tables (research_runs, source_documents, etc.) and infrastructure tables (tenants, outbox_records)

This reflects the system's history: the scoring system predates the research pipeline.

### company_id vs id

In the `companies` table:
- `id` — Integer auto-increment PK (database-internal)
- `company_id` — String (unique) — the application-level identifier (slug or external ID)

Always query companies by `company_id` in application code, not by `id`.

### JSON Columns

Many columns store structured data as JSON (PostgreSQL JSON type):
- `companies.revenue_timeline` — historical revenue data points
- `companies.funding_rounds` — funding history
- `companies.scoring_breakdown` — per-dimension score details
- `research_runs.summary` — full research run summary
- `enrichment_cache.enriched_data` — complete enrichment payload

### Outbox Pattern

`outbox_records` implements the transactional outbox pattern for reliable event delivery. Events are written to the outbox in the same transaction as business data, then processed by `OutboxWorker` asynchronously.

---

## ORM Models

All models are in `src/solstein/infrastructure/database_models.py`.

```python
from solstein.infrastructure.database_models import (
    CompanyRecord,
    ScoringRecord,
    SignalRecord,
    MarketSnapshot,
    AuditTrailRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    ResearchArtifactRecord,
    SourceDocumentRecord,
    MetricObservationRecord,
    EvidenceReadinessRecord,
    ContradictionRecord,
    ContradictionTransitionRecord,
    OutboxRecord,
    EnrichmentAuditRecord,
    EnrichmentCacheRecord,
    EnrichmentJobRecord,
    TenantRecord,
)
```

---

## Common Queries

### Get a company by company_id

```python
from sqlalchemy import select
from solstein.infrastructure.database_models import CompanyRecord

async def get_company(session: AsyncSession, company_id: str) -> CompanyRecord | None:
    result = await session.execute(
        select(CompanyRecord).where(CompanyRecord.company_id == company_id)
    )
    return result.scalar_one_or_none()
```

### List companies by tier with scoring

```python
from sqlalchemy import select, desc
from solstein.infrastructure.database_models import CompanyRecord

async def get_top_companies(session: AsyncSession, tier: str, limit: int = 20):
    result = await session.execute(
        select(CompanyRecord)
        .where(CompanyRecord.tier == tier)
        .order_by(desc(CompanyRecord.composite_score))
        .limit(limit)
    )
    return result.scalars().all()
```

### Get latest scoring record with signals

```python
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from solstein.infrastructure.database_models import ScoringRecord

async def get_latest_score(session: AsyncSession, company_id: str) -> ScoringRecord | None:
    result = await session.execute(
        select(ScoringRecord)
        .where(ScoringRecord.company_id == company_id)
        .options(selectinload(ScoringRecord.signals))
        .order_by(desc(ScoringRecord.scored_at))
        .limit(1)
    )
    return result.scalar_one_or_none()
```

### Get research run with all related data

```python
from sqlalchemy.orm import selectinload
from solstein.infrastructure.database_models import ResearchRunRecord

async def get_run_full(session: AsyncSession, run_id: str) -> ResearchRunRecord | None:
    result = await session.execute(
        select(ResearchRunRecord)
        .where(ResearchRunRecord.run_id == run_id)
        .options(
            selectinload(ResearchRunRecord.stages),
            selectinload(ResearchRunRecord.artifacts),
            selectinload(ResearchRunRecord.sources),
        )
    )
    return result.scalar_one_or_none()
```

### Check enrichment cache

```python
from solstein.infrastructure.database_models import EnrichmentCacheRecord
from datetime import datetime

async def get_cached_enrichment(session: AsyncSession, company_id: str):
    result = await session.execute(
        select(EnrichmentCacheRecord)
        .where(
            EnrichmentCacheRecord.company_id == company_id,
            EnrichmentCacheRecord.expires_at > datetime.utcnow(),
        )
    )
    record = result.scalar_one_or_none()
    if record:
        record.hits += 1
        record.last_accessed_at = datetime.utcnow()
        await session.commit()
    return record
```

---

## Repository Pattern

Application code accesses the database through repositories, not directly:

```
src/solstein/infrastructure/
├── company_repository.py      # CompanyRepository
├── repositories.py            # ScoringRepository, SignalRepository, etc.
├── enrichment_repositories.py # EnrichmentRepository
└── research_dual_write.py     # ResearchRunRepository (dual-write support)
```

Use repositories from the application layer instead of raw SQLAlchemy sessions.

---

## Database Initialization

```bash
# Set PYTHONPATH first
export PYTHONPATH=src

# Create all tables (development)
python -c "
import asyncio
from solstein.infrastructure.database import init_db
asyncio.run(init_db())
"

# Or load seed data
python -m solstein.data.seed_db
```

---

## Indexes

The `companies` table has performance-optimized indexes for common query patterns:

| Index | Columns | Use Case |
|---|---|---|
| `idx_companies_name` | name | Name-based lookup |
| `idx_companies_industry` | industry | Industry filter |
| `idx_companies_headquarters` | headquarters | Geographic filter |
| `idx_companies_tier` | tier | Tier filter |
| `idx_companies_classification` | classification | Classification filter |
| `idx_companies_ai_score` | ai_score | AI score range queries |
| `idx_companies_composite_score` | composite_score | Top-N queries |
| `idx_companies_revenue` | revenue_eur_m | Revenue range queries |
| `idx_companies_growth` | growth_rate_pct | Growth range queries |
| `idx_companies_updated` | last_updated | Freshness queries |
| `idx_companies_industry_hq` | (industry, headquarters) | Combined filter |

---

## Multi-Tenancy

The `tenants` table controls API access:

```python
# Tenant record structure
class TenantRecord:
    id: UUID                  # PK
    name: str                 # Unique tenant name
    api_key_hash: str         # SHA-256 hash of API key (64 chars, unique)
    is_active: bool           # Enable/disable tenant
    plan: str                 # 'free' | 'standard' | 'enterprise'
    rate_limit_per_min: int   # Default: 60 req/min
```

All API requests include `X-API-Key` header. The `TenantMiddleware` hashes the key and looks up the tenant. Rate limiting is enforced per-tenant.

---

## See Also

- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** — Complete table-by-table schema reference with all columns, types, and constraints
- **`src/solstein/infrastructure/database_models.py`** — SQLAlchemy model definitions (single source of truth)
- **`src/solstein/infrastructure/database.py`** — Async engine and session factory
- **`src/solstein/infrastructure/repositories.py`** — Repository implementations
