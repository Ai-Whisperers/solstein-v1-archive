# Solstein Architecture Documentation

## System Overview

Solstein is an AI-powered competitive intelligence platform for PE/VC professionals. It analyzes market data, company financials, competitive positioning, and generates strategic insights using a multi-LLM provider architecture with automatic failover.

**Key characteristics:**
- Multi-tenant SaaS (per-tenant API keys, rate limiting, plan tiers)
- Async-first: FastAPI + asyncpg + async SQLAlchemy 2.0
- 13 LLM providers with proactive health checking and automatic failover
- Background task processing via Celery + Redis
- Hexagonal architecture with ports and adapters

---

## Architecture Principles

1. **Database-First** — All data stored in PostgreSQL with proper constraints and indexes
2. **Async-First** — All I/O operations use async/await; FastAPI + asyncpg throughout
3. **Repository Pattern** — Unified repository layer; direct session access discouraged in business logic
4. **Multi-Tenancy** — Every request carries tenant context; rate limits enforced per tenant
5. **Provider Resilience** — LLM provider failures rotate automatically; no single point of failure
6. **Observability** — Every enrichment, scoring, and research operation is audit-logged

---

## Architecture Layers

```
┌───────────────────────────────────────────────────────────────────┐
│                          API Layer                                │
│   FastAPI · 13 Routers · WebSocket · TenantMiddleware · JWT       │
└──────────────────────────────┬────────────────────────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
┌─────────────┐      ┌──────────────────┐     ┌──────────────────┐
│  Research   │      │   Scoring &      │     │    Enrichment    │
│  Pipeline   │      │   Analytics      │     │    Pipeline      │
│ (research/) │      │  (analytics/)    │     │  (adapters/)     │
└─────────────┘      └──────────────────┘     └──────────────────┘
       │                       │                        │
       └───────────────────────┼────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────────┐
│                        Domain Layer                               │
│          Business Entities · Value Objects · Enums               │
│               Validators · Repository Interfaces                  │
└──────────────────────────────┬────────────────────────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
┌─────────────┐      ┌──────────────────┐     ┌──────────────────┐
│ PostgreSQL  │      │      Redis       │     │  LLM Providers   │
│   14+       │      │  Cache + Celery  │     │  (13 providers)  │
│ (18 tables) │      │                  │     │                  │
└─────────────┘      └──────────────────┘     └──────────────────┘
```

---

## System Components

### 1. Database Layer

**PostgreSQL 14+** with async SQLAlchemy 2.0 and asyncpg driver.

**18 Tables** organized by functional domain:

#### Competitive Intelligence (Integer PKs)

| Table | Purpose |
|---|---|
| `companies` | Core company profiles — ~42 columns including financials, AI scores, funding |
| `scoring_records` | Point-in-time scoring snapshots per company |
| `signal_records` | Individual signals driving each scoring record |
| `market_snapshots` | Aggregate market state at a point in time |
| `audit_trails` | Full per-company analysis audit trail |
| `enrichment_cache` | TTL-based enrichment data cache (default: 24h TTL) |
| `enrichment_audit_trail` | Per-operation enrichment audit log |
| `enrichment_jobs` | Celery enrichment task tracking |

#### Research Pipeline (UUID PKs)

| Table | Purpose |
|---|---|
| `research_runs` | Top-level research run (market + seed_company) |
| `research_stages` | Per-stage execution tracking within a run |
| `research_artifacts` | Artifacts produced by a run |
| `source_documents` | Source URLs observed per company |
| `metric_observations` | Individual metric values from each source |
| `evidence_readiness` | Evidence quality scores per company |
| `research_contradictions` | Detected data conflicts between sources |
| `research_contradiction_transitions` | Contradiction status change history |

#### Infrastructure (Mixed PKs)

| Table | Purpose |
|---|---|
| `outbox_records` | Transactional outbox for reliable event delivery (UUID) |
| `tenants` | Multi-tenant API key registry (UUID) |

**Connection Pool:**
- `pool_size = 20`
- `max_overflow = 10`
- `timeout = 30s`

---

### 2. API Layer

**FastAPI** application at `solstein.api.main:app` with 13 routers.

**Middleware Stack** (applied in order):
1. CORS
2. `LoggingMiddleware` — request IDs, timing headers
3. Rate Limiting
4. Exception Handlers
5. `SecurityMiddleware`
6. `TenantMiddleware` — reads `X-API-Key` header, loads tenant, enforces rate limit

**Routers:**

| Router | Prefix | Description |
|---|---|---|
| `auth` | — | Login, logout, refresh, me |
| `companies` | — | Company list, detail, score, enrich |
| `scoring` | `/scoring` | Score a company, stats |
| `market` | `/market` | Market analysis, search, overlap |
| `export` | `/export` | Excel export |
| `simulation` | `/simulation` | Market simulation (POST /run) |
| `dashboard` | `/dashboard` | Summary, sectors, top, trends |
| `drill_down` | `/drill-down` | Signal explanation (transparency) |
| `enrichment` | — | Enrichment trigger, cache, audit |
| `health` | `/health` | Health, status, liveness, readiness |
| `jobs` | `/jobs` | Returns 501 (Temporal removed) |
| `async_jobs` | `/async` | Celery-backed async job management |
| `websocket` | — | WebSocket support |

**Authentication:**
- **Tenant auth**: `X-API-Key` header → `TenantMiddleware` → rate limiting
- **User auth**: JWT bearer tokens from `POST /auth/login`

---

### 3. Research Pipeline

The core research workflow runs in `src/solstein/research/`:

```
Discovery → Gather → Aggregate → Evidence → Reconcile → Score → Export
```

| Stage | Module | Description |
|---|---|---|
| Discovery | `research/discovery.py` | Find competitor companies |
| Gather | `research/gather.py` | Collect data from 11 connectors |
| Aggregate | `research/aggregate.py` | Normalize and merge facts from multiple sources |
| Evidence | `research/evidence.py` | Assess source quality and readiness scores |
| Reconcile | `research/reconcile.py` | Resolve data conflicts, track contradiction transitions |
| Signals | `research/signals.py` | Extract market signals from aggregated data |
| Pipeline | `research/pipeline.py` | Orchestration |

**Agent Coordinator** (`src/solstein/agents/`) orchestrates multiple research agents:
- `GitHubAgent` — GitHub repository signals
- `WebSearchAgent` — Web search via Exa/Google
- `WebsiteAgent` — Company website scraping
- `CompaniesHouseAgent` — UK Companies House filings
- `SeedMarkdownAgent` — Seed competitor markdown files

LangGraph powers multi-agent workflow orchestration.

---

### 4. Enrichment Pipeline

**Celery-based** async enrichment via `src/solstein/adapters/enrichment/`.

11 enrichment adapters, each with a unified interface:

| Adapter | Data Source |
|---|---|
| `FundingEnrichmentAdapter` | Funding/Crunchbase data |
| `LinkedInEnrichmentAdapter` | LinkedIn company data |
| `NewsEnrichmentAdapter` | News articles |
| `PatentsEnrichmentAdapter` | USPTO / Google Patents |
| `WebSearchEnrichmentAdapter` | Web search results |
| `WebsiteEnrichmentAdapter` | Company website |
| `YahooFinanceEnrichmentAdapter` | Financial data |
| `GlobalMarketEnrichmentAdapter` | Market data |
| `SECEdgarConnector` | SEC EDGAR filings |
| `NewsSignalConnector` | News-derived signals |
| `GitHubConnector` | GitHub activity |

**Flow:**
```
POST /companies/{id}/enrich
  → EnrichmentJobRecord created (Celery task_id as PK)
  → Celery worker picks up task
  → Runs applicable adapters
  → Results stored in companies table + enrichment_cache
  → Audit logged to enrichment_audit_trail
```

---

### 5. LLM Provider Layer

13 providers with proactive health checking and automatic failover.

**Priority order (failover chain):**

| # | Provider | Notes |
|---|---|---|
| 1 | Ollama (local) | Privacy-first, llama3.2 |
| 2 | Groq | Fast inference |
| 3 | Fireworks | Cost-effective |
| 4 | SiliconFlow | |
| 5 | Alibaba Cloud | |
| 6 | Mistral | European |
| 7 | DeepInfra | |
| 8 | Gemini | Google |
| 9 | NVIDIA NIM | |
| 10 | Cerebras | |
| 11 | Kimi (Moonshot) | |
| 12 | Anthropic | |
| 13 | OpenAI | |
| — | Template fallback | When all providers fail |

**Health States:** `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `RATE_LIMITED`, `EXHAUSTED`

**Error Classification:**
- 429 → `RATE_LIMITED` → rotate to next provider
- 401 → `AUTHENTICATION` → skip provider
- 402 → `QUOTA_EXHAUSTED` → skip provider

---

### 6. Infrastructure Layer

`src/solstein/infrastructure/` contains all external system adapters:

| Module | Purpose |
|---|---|
| `database.py` | Async engine, session factory, `init_db()` |
| `database_models.py` | All 18 SQLAlchemy ORM models |
| `database_service.py` | High-level database service |
| `cache.py` | Redis cache client |
| `cache_protocol.py` | Cache protocol/interface |
| `cache_warming.py` | Proactive cache warming on startup |
| `company_repository.py` | Company CRUD repository |
| `repositories.py` | Scoring, signal, market repositories |
| `enrichment_repositories.py` | Enrichment-specific repositories |
| `outbox_worker.py` | Transactional outbox processor |
| `retry_policy.py` | Configurable retry with backoff |
| `vector_store.py` | Vector store (for semantic search) |
| `connectors/` | 11 low-level data connectors |

---

## Repository Pattern

All data access goes through repositories. Direct session queries are discouraged in business logic.

```python
# ✅ Good — through repository
company = await company_repo.get_by_company_id(company_id)

# ⚠️ Only in repositories, not business logic
result = await session.execute(
    select(CompanyRecord).where(CompanyRecord.company_id == company_id)
)
```

**Key Repositories:**
- `CompanyRepository` — Company CRUD, search, tier queries
- `ScoringRepository` — Score storage and retrieval
- `SignalRepository` — Signal storage per scoring record
- `EnrichmentRepository` — Cache, audit, job tracking

---

## Service Layer

**API Services** (`src/solstein/api/services/`):
- `DrillDownService` — Signal explanation and transparency
- `EnrichmentService` — Enrichment orchestration and job management

**Application Services** (`src/solstein/application/`):
- Agent orchestration
- Analytics pipeline
- Export orchestration

All services receive `AsyncSession` via dependency injection:

```python
class DrillDownService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_repo = CompanyRepository(session)
```

---

## Data Flow

### Scoring Flow

```
POST /scoring/company/{id}/score
  → CompanyRepository.get_by_company_id()
  → Analytics scorers (growth, financial_health, competitive_position)
  → ScoringRecord saved to scoring_records table
  → SignalRecords saved to signal_records table
  → AuditTrailRecord saved to audit_trails table
  → companies table updated with latest scores
```

### Enrichment Flow (Async)

```
POST /companies/{id}/enrich
  → EnrichmentJobRecord created (status: PENDING)
  → Celery task dispatched
  → Worker: runs enrichment adapters
  → Worker: updates companies table fields
  → Worker: stores result in enrichment_cache
  → Worker: logs to enrichment_audit_trail
  → Job status updated to SUCCESS/FAILED
```

### Research Pipeline Flow

```
Research run initiated
  → Discovery: find companies via adapters
  → Gather: collect data from 11 connectors
  → Aggregate: normalize facts from multiple sources
  → Evidence: score source quality, detect contradictions
  → Reconcile: resolve conflicts, track transitions
  → Score & Classify: apply analytics pipeline
  → Export: generate reports (Excel, PDF, Markdown)
```

---

## Design Patterns

### Transactional Outbox

`outbox_records` table implements the transactional outbox pattern for reliable event delivery:

```python
async with session.begin():
    company = await company_repo.create(...)
    await session.add(OutboxRecord(event_type="company.created", payload=...))
    # Both committed atomically
# OutboxWorker processes outbox_records asynchronously
```

### Unit of Work

Transactions managed at service level:

```python
async with session.begin():
    scoring_record = await scoring_repo.create(...)
    for signal in signals:
        await signal_repo.create(scoring_record_id=scoring_record.id, ...)
    # All signals committed with scoring record or rolled back together
```

### Dependency Injection

FastAPI's dependency injection provides sessions to routers:

```python
# In router
async def score_company(
    company_id: str,
    session: AsyncSession = Depends(get_async_session),
    tenant: TenantRecord = Depends(get_current_tenant),
) -> ScoringResponse:
    service = ScoringService(session)
    return await service.score(company_id)
```

---

## Performance

### Database

1. **Composite Indexes** — `(industry, headquarters)` for common filter patterns
2. **Score Indexes** — `composite_score`, `ai_score`, `growth_rate_pct` for ranking queries
3. **Connection Pooling** — pool_size=20, max_overflow=10
4. **Async Operations** — all queries non-blocking via asyncpg

### Caching

1. **Redis Cache** — company data, enrichment results, API responses
2. **Enrichment Cache** — TTL-based (`enrichment_cache` table, default 86400s)
3. **Cache Warming** — proactive warming on API startup

### LLM

1. **Provider Health Checking** — preemptively detects rate limits before they fail
2. **Structured Client** — typed LLM calls with schema validation
3. **Tracing** — LLM call tracing for cost/latency observability

---

## Security

1. **Multi-Tenant Isolation** — X-API-Key → TenantRecord → per-tenant rate limiting
2. **API Key Hashing** — SHA-256 stored; raw key never persisted
3. **JWT Auth** — short-lived access tokens + refresh token rotation
4. **SQL Injection Prevention** — SQLAlchemy parameterized queries only
5. **Input Validation** — Pydantic models validate all inputs
6. **Audit Logging** — all enrichment and scoring operations logged

---

## Deployment Architecture

### Production Setup

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Clients   │────▶│   FastAPI   │────▶│ PostgreSQL  │
│  (X-API-Key)│     │   Server    │     │    14+      │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌─────────┐  ┌─────────┐  ┌──────────┐
       │  Redis  │  │ Celery  │  │   LLM    │
       │ (Cache) │  │ Workers │  │Providers │
       └─────────┘  └─────────┘  └──────────┘
```

### Scaling

1. **Read Replicas** — PostgreSQL replicas for query scaling
2. **Celery Workers** — horizontal scaling for enrichment throughput
3. **Redis Cluster** — distributed caching for multi-instance deployments
4. **LLM Failover** — 13 providers ensure LLM availability

---

## Module Map

```
src/solstein/
├── api/               # FastAPI: routers, middleware, schemas, websocket
├── adapters/          # Enrichment, discovery, aggregation adapters
├── agents/            # Research agents (GitHub, web, companies house)
├── analytics/         # Scoring, classification, TAM, equity analysis
├── application/       # Orchestration layer (agents, exporters, analytics)
├── config/            # Pydantic-settings configuration
├── core/              # Hexagonal architecture ports
├── data/              # Data access: fetchers, loaders, connectors
├── domain/            # Business entities and value objects (DDD)
├── exporters/         # Excel, CSV, PDF, Markdown export generators
├── extractors/        # LLM financial extractor, markdown extractor
├── infrastructure/    # DB, Redis, repositories, connectors, outbox
├── llm/               # 13-provider LLM client with health checking
├── migrations/        # Data migration scripts
├── monitoring/        # Continuous monitoring
├── presentation/      # Report generation and narrative templates
├── research/          # Core research pipeline
├── security/          # JWT handler
├── utils/             # Shared utilities (logging)
├── validation/        # Input validation (company, financial sanity)
├── cli.py             # CLI entry point (solstein = 'solstein.cli:main')
├── celery_config.py   # Celery configuration
├── worker.py          # Background task worker
└── worker_tasks.py    # Celery task definitions
```

---

**Last Updated**: 2026-03-01
**Version**: 3.0 (Multi-tenant, 13 LLM providers, Celery enrichment)
