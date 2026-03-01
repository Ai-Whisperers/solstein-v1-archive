# Solstein — Architecture Overview

> AI-powered competitive intelligence platform for PE/VC professionals.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│              (FastAPI + Async Endpoints)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Research   │    │  Analytics   │    │   Export     │
│   Engine     │    │   Engine     │    │   Engine     │
└──────────────┘    └──────────────┘    └──────────────┘
                              │
        ┌─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Domain Layer (Business Logic)                   │
│     Models • Services • Repositories • Scoring              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PostgreSQL   │    │    Redis     │    │ File System  │
│   (Data)     │    │   (Cache)    │    │  (Exports)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Architecture Principles

1. **Database-First** — All data stored in PostgreSQL with proper constraints and indexes
2. **Async-First** — All I/O operations use `async/await` pattern via `asyncpg`
3. **Repository Pattern** — Unified repository layer for data access; no direct DB calls in business logic
4. **Type Safety** — Full type hints throughout; `mypy --strict` enforced
5. **Test Coverage** — 4-layer testing pyramid (unit → integration → worker → data quality)
6. **LLM Resilience** — Provider fallback chain with health checking; never a single point of failure

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.11+ |
| **Framework** | FastAPI | Latest |
| **Package Manager** | uv / pip | — |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 2.0+ (async) |
| **Data Processing** | Pandas | 2.x |
| **Excel Export** | OpenPyXL | 3.x |
| **Testing** | pytest | 8.x |
| **Linting** | ruff + black + mypy | Latest |
| **Frontend** | Next.js | 18+ |

---

## Directory Structure

```
solstein/
├── src/solstein/
│   ├── api/                 # FastAPI application
│   │   ├── routers/         # Route handlers (companies, scoring, market, export, …)
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── middleware.py    # Logging & security middleware
│   │   ├── exceptions.py    # Global exception handlers
│   │   └── main.py          # App factory & lifespan
│   ├── domain/              # Pure domain models
│   │   ├── models/          # Business entities (Company, Signal, …)
│   │   └── scoring/         # Scoring algorithms (Phoenix/Salt/Lead)
│   ├── infrastructure/      # External adapters
│   │   ├── database/        # SQLAlchemy async engine & session
│   │   ├── cache/           # Redis client
│   │   └── company_repository.py
│   ├── application/         # Application services (orchestration)
│   │   └── services/
│   ├── exporters/           # Export formats
│   │   ├── llm.py           # LLM-powered narrative reports
│   │   ├── excel.py         # Excel generation (OpenPyXL)
│   │   └── markdown.py
│   ├── analytics/           # Analysis tools & filters
│   ├── llm/                 # LLM client with health checking
│   │   ├── health_checker.py
│   │   └── enhanced_client.py
│   ├── security/            # Auth & caching
│   │   ├── jwt_handler.py   # JWT token handling (HS256)
│   │   └── cache.py         # Redis caching layer
│   └── config.py            # Application settings (pydantic-settings)
├── tests/
│   ├── unit/                # Domain models & scoring logic
│   ├── integration/         # API endpoints & worker tasks
│   ├── data_quality/        # Golden dataset regression tests
│   └── performance/         # Load tests
├── docs/                    # Documentation
├── scripts/                 # Utility scripts (setup_db.py, …)
├── dashboard/               # Next.js frontend
└── data/                    # Market intelligence datasets
```

---

## Database Layer

**PostgreSQL 15+** with the following characteristics:

- **21 Tables** organized by domain
- **40+ Indexes** for query optimization
- **20+ Foreign Keys** for referential integrity
- **50+ Constraints** for data quality
- **ACID Compliance** for transaction safety

### Table Categories

**Core Entities:**
- `companies` — Company profiles
- `research_runs` — Research execution tracking
- `facts` — Extracted factual data
- `signals` — Detected market signals
- `contradictions` — Fact contradictions
- `source_document_snapshots` — Source documentation

**Scoring & Analysis:**
- `scoring_records` — Company scoring data
- `signal_records` — Signal generation records

**Enrichment:**
- `company_enrichment_queue` — Pending enrichments
- `enrichment_results` — Enrichment outcomes
- `enrichment_cache` — Cached enrichment data
- `enrichment_audit` — Enrichment audit trail

**Monitoring:**
- `market_snapshots` — Market data snapshots
- `audit_trails` — Audit logging
- `outbox_records` — Event outbox

### ORM Models

**16+ ORM models** across two files:
- `src/solstein/infrastructure/database_models.py` — 17 models (companies, scoring, signals, research, enrichment, audit)
- `src/solstein/domain/facts.py` — 6 models (gathering batches, facts, sources, refresh, conflicts, calibration)

**11 Alembic migrations** covering the complete schema evolution.

---

## LLM Provider Architecture

Solstein uses a **provider fallback chain** with proactive health checking:

```
Ollama (local) → Fireworks → OpenAI → Groq → Template Fallback
```

### Supported Providers

| Provider | Model | Use Case |
|----------|-------|----------|
| Ollama | llama3.2:latest | Local, sensitive data |
| OpenAI | gpt-4o-mini | General purpose |
| Groq | llama-3.3-70b-versatile | Fast inference |
| Fireworks | mixtral-8x22b-instruct | Cost-effective |

### Health Checking

All LLM providers have proactive health checking:
- Rate limit detection (HTTP 429)
- Quota exhaustion detection (HTTP 402)
- Authentication failure detection (HTTP 401)
- Automatic provider rotation on failure

See: `src/solstein/llm/health_checker.py`

---

## Security Architecture

- **JWT Authentication** — HS256 tokens with configurable expiry (default 30 min)
- **CORS** — Specific origin allowlist (no wildcard)
- **Input Validation** — Pydantic schemas on all endpoints
- **Secret Key Validation** — Startup fails in production if using default key
- **Security Middleware** — Request-level security headers

---

## Scoring System

Every company is scored across three dimensions and classified:

| Classification | Score | Meaning |
|---|---|---|
| 🔥 **Phoenix** | ≥ 7.0 | High-growth, AI-native |
| 🧂 **Salt** | 4.0–7.0 | Stable, signal-rich |
| ⚖️ **Lead** | ≤ 4.0 | Legacy weight, transformation opportunity |

**Score dimensions:**
- **Growth Score** — Revenue trajectory, margin health
- **Financial Health Score** — Scale, funding cushion, efficiency
- **Competitive Position Score** — AI maturity, SaaS adoption, tech stack depth

---

## Performance Baselines

| Operation | Target | Status |
|-----------|--------|--------|
| Company lookup by ID | <10ms | ✅ |
| Facts query by company | <50ms | ✅ |
| Full pipeline (1 company) | <2s | ✅ |

**Performance optimizations applied:**
- N+1 query elimination via `get_all_filtered()` database-level filtering
- 13 database indexes (industry, headquarters, composite, score fields)
- Redis caching with in-memory fallback for company data

---

## Related Documentation

- [`docs/architecture/decisions.md`](architecture/decisions.md) — Architecture decision records
- [`docs/architecture/modules.md`](architecture/modules.md) — Module dependency map
- [`docs/guides/developer.md`](guides/developer.md) — Developer setup guide
- [`docs/api/reference.md`](api/reference.md) — Full API reference
