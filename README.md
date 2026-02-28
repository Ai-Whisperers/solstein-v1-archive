<div align="center">

# 𝔖𝔬𝔩𝔰𝔱𝔢𝔦𝔫

### *The Sunstone for Capital Navigation*

> *In Viking navigation, the solarsteinn revealed the sun behind the clouds.*
> *Solstein reveals the competitive landscape through market fog.*
> *Built by the Guild of Architects — not engineers. Wizards.*

[![Python](https://img.shields.io/badge/Python-3.12-4b0082?style=for-the-badge&logo=python&logoColor=ffd700)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Live-4b0082?style=for-the-badge&logo=fastapi&logoColor=ffd700)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-Workers-4b0082?style=for-the-badge&logo=celery&logoColor=ffd700)](https://docs.celeryq.dev)
[![Tests](https://img.shields.io/badge/Tests-1190+%20Collected-4b0082?style=for-the-badge&logo=pytest&logoColor=ffd700)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-~28%25-ffd700?style=for-the-badge&logo=codecov&logoColor=4b0082)](tests/)
[![License](https://img.shields.io/badge/License-Proprietary-4b0082?style=for-the-badge&logo=scroll&logoColor=ffd700)](LICENSE)

> **📖 Documentation Site**: [https://ai-whisperers.github.io/solstein/](https://ai-whisperers.github.io/solstein/)

</div>

---

## 🎯 How It Works

Solstein combines **financial intelligence**, **technical signals**, and **market context** to deliver comprehensive company assessments:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Sources   │───→│  Scoring Engine │───→│  Attractiveness │
│                 │    │                 │    │     Board       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Financial     │    │ • Growth Score  │    │ • Ranked list   │
│ • GitHub        │    │ • Financial     │    │ • Classified    │
│ • News          │    │   Health        │    │ • Explainable   │
│ • Team          │    │ • Competitive   │    │ • Actionable    │
│ • Technology    │    │   Position      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**The Process:**

| Step | Action | Timeline |
|------|--------|----------|
| 1️⃣ **Discover** | Define market universe (100-500 companies) | Day 1 |
| 2️⃣ **Gather** | AI agents collect data from 5+ sources | Day 1-2 |
| 3️⃣ **Score** | Multi-dimensional scoring with full traceability | Day 2-3 |
| 4️⃣ **Present** | Interactive Attractiveness Board with explanations | Day 3 |

**vs. Traditional Consulting:**

| Aspect | McKinsey/Bain/BCG | Solstein |
|--------|-------------------|----------|
| **Timeline** | 90 days | 3 days |
| **Cost** | EUR 500K–1.5M | EUR 60K–150K/year |
| **Deliverable** | Static 100-page PDF | Interactive dashboard |
| **Updates** | One-time snapshot | Quarterly refreshes |
| **Explainability** | "Trust our analysis" | Full signal chain visible |

📊 **Live Proof**: [29 European energy software companies](docs/PITCH/case-study.md) analyzed in 3 days with complete classification.

---

## 📜 What Is Solstein?

Companies are born with wings. They start light, agile, and fast. But as they grow, something heavy begins to form — a manual process here, a temporary workaround there, a script that only one person understands and that person left six months ago.

Slowly. Inevitably. **The wings turn to lead.**

**Solstein is the Sunstone** — the instrument that sees through market fog and tells Private Equity exactly which companies are flying, which are drifting, and which are sinking under the Gravity of Legacy.

It replaces the old ritual — EUR 500K–1.5M to McKinsey, 90 days to wait, a static PDF on delivery — with AI-orchestrated market intelligence built by a **Guild of Wizards**, delivered in **days, not months**.

The core output is an **Attractiveness Board**: ranked, clickable, fully-explainable. Every score exposes its signal chain. No black boxes. No "trust the algorithm."

### 💎 Business Value Proposition

Solstein transforms the Private Equity due diligence process:
- **Velocity**: Market maps delivered in days, not months.
- **Explainability**: Every score is traceable to specific financial and technical signals.
- **Edge**: Identify hidden "Diamonds in the Lead" that traditional analysis misses.
- **Cost Efficiency**: 80% lower cost than traditional tier-1 consulting engagements.

---

## 🔥 The Classification System

Every company in a market is scored and classified:

| Classification | Growth Score | What It Means |
|---|---|---|
| 🔥 **Phoenix** | ≥ 7.0 | High-growth, AI-native or rapidly adopting. Act now. |
| 🧂 **Salt** | 4.0 – 7.0 | Stable players. Watch for directional signals. |
| ⚖️ **Lead** | ≤ 4.0 | Legacy weight. Hidden diamonds or dead weight. Assess the people. |

The score is calculated across three dimensions:
- **Growth Score** — Revenue trajectory, margin health
- **Financial Health Score** — Scale, funding cushion, efficiency  
- **Competitive Position Score** — AI maturity, SaaS adoption, tech stack depth

---

## 🏗️ Architecture

```
solstein/
├── src/solstein/
│   ├── api/              ← FastAPI application & routers
│   ├── infrastructure/   ← Stone Layer: PostgreSQL, SQLAlchemy, Services
│   ├── analytics/        ← Logic Fusion: Scoring, Market Analysis
│   ├── agents/           ← Specialized AIs (Coordinator, GitHub, News)
│   ├── domain/           ← Pure domain models
│   ├── utils/            ← Aura Layer: Logging, Traceability
│   └── worker.py         ← Celery worker & Temporal workflows
├── bin/agents/           ← Agent deployment scripts (planner, implementer, critiquer)
├── tests/
│   ├── unit/             ← Domain models & scoring logic
│   ├── integration/      ← API endpoints & worker tasks
│   └── data_quality/     ← Golden dataset regression tests
├── docs/                 ← Technical Grimoire
└── data/                 ← Market intelligence datasets
```

---

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone <repo> && cd solstein
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# 2. Start the API
uvicorn solstein.api.main:app --reload

# 3. Start workers (separate terminal)
celery -A solstein.worker worker --loglevel=info

# 4. Run the test suite
pytest tests/ --cov=src/solstein
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Platform health check |
| `GET` | `/companies` | List all profiled companies |
| `GET` | `/companies/{id}` | Retrieve single company profile |
| `POST` | `/scoring/company/{id}/score` | Score a specific company |
| `GET` | `/scoring/stats` | Market-wide scoring statistics |
| `GET` | `/market/analysis` | Full market landscape analysis |
| `GET` | `/market/search` | Search companies by query |
| `GET` | `/market/overlap/{id}` | Competitive overlap analysis |
| `POST` | `/export/` | Generate Excel intelligence report |

> Full API reference → [`docs/api/reference.md`](docs/api/reference.md)

---

## 💰 Commercial Model

| Tier | Price | Deliverable |
|------|-------|-------------|
| **Anchor Validation** | EUR 60K pilot | Single market, validated scoring vs. real deals |
| **PE Subscription** | EUR 75–150K/yr | Continuous intelligence, quarterly refreshes |
| **Portfolio-Wide** | EUR 2–3M + 300K/yr | Up to 10 portfolio companies, multi-vertical |
| **Enterprise License** | EUR 3–5M + 500K/yr | Unlimited markets, full architecture transfer |

> Full business model → [`docs/PITCH/business-model.md`](docs/PITCH/business-model.md)

---

## 📚 Documentation by Persona

| Scroll | Contents |
|--------|----------|
| 📜 [`docs/LORE/origin.md`](docs/LORE/origin.md) | The origin story — how Solstein was born |
| 📜 [`docs/LORE/the-play.md`](docs/LORE/the-play.md) | The three-entity strategic architecture |
| 📜 [`docs/PITCH/executive-brief.md`](docs/PITCH/executive-brief.md) | One-page investor brief |
| 📜 [`docs/PITCH/business-model.md`](docs/PITCH/business-model.md) | Full commercial model |
| 📜 [`docs/PITCH/case-study.md`](docs/PITCH/case-study.md) | Live case: 29 companies, European energy software |
| 📜 [`docs/guides/developer.md`](docs/guides/developer.md) | Developer setup & contribution guide |
| 📜 [`docs/guides/operator.md`](docs/guides/operator.md) | Deployment & operations guide |
| 📜 [`docs/api/reference.md`](docs/api/reference.md) | Full API reference |
| 📜 [`docs/architecture/decisions.md`](docs/architecture/decisions.md) | Architecture decision records |

### 👨‍💼 For Investors & Business Stakeholders
| Document | Purpose |
|----------|---------|
| 📊 [Executive Brief](docs/PITCH/executive-brief.md) | One-page investment thesis |
| 💰 [Business Model](docs/PITCH/business-model.md) | Pricing & commercial strategy |
| 📈 [Case Study](docs/PITCH/case-study.md) | Live 29-company analysis proof |
| 🏛️ [The Strategic Play](docs/LORE/the-play.md) | Three-entity value architecture |

### 👨‍💻 For Developers & Engineers
| Document | Purpose |
|----------|---------|
| ⚙️ [Developer Guide](docs/guides/developer.md) | Setup, testing, architecture |
| 🔌 [API Reference](docs/api/reference.md) | Complete endpoint documentation |
| 🏗️ [Architecture Decisions](docs/architecture/decisions.md) | Technical design rationale |
| 🧪 [Testing Guide](docs/guides/developer.md#testing) | 4-layer testing pyramid |

### 👨‍✈️ For Operators & DevOps
| Document | Purpose |
|----------|---------|
| 🚀 [Operator Guide](docs/guides/operator.md) | Deployment, Docker, monitoring |
| 🗄️ [Database Guide](docs/guides/database.md) | PostgreSQL setup & migrations |
| ⚡ [Quick Reference](docs/QUICK-REFERENCE.md) | Commands & environment variables |
Historical/internal planning docs that used to live in the repo root are archived in `docs/archive/root-docs/`.

---

## 🧪 Testing Philosophy

Solstein follows a **4-layer testing pyramid**:

1. **Unit** — Domain models and scoring math, `pytest.approx` precision
2. **Integration** — All API endpoints with deterministic mock repositories
3. **Worker** — Celery tasks verified synchronously without Redis dependency
4. **Data Quality** — Golden Dataset regression to protect classification boundaries

```bash
pytest tests/unit/          # Fast, pure logic
pytest tests/integration/   # API contract tests
pytest tests/data_quality/  # Golden dataset regressions
pytest tests/ --cov         # Full suite with coverage
```

---

## 🏛️ Professionalization

Solstein underwent a structured **5-wave professionalization initiative** in February 2026, transforming it from a prototype into a production-ready platform.

| Wave | Focus | Key Deliverables |
|------|-------|-----------------|
| Wave 1 | Foundation | Data migration script, fixed 4 broken test files, 4 new DB migrations |
| Wave 2 | Repository Unification | Unified async SQLAlchemy repos, deprecated JsonFileRepository |
| Wave 3 | Production Cleanup | Removed all mock clients, zero JSON in production paths |
| Wave 4 | Constraints & Optimization | FK constraints, CHECK constraints, 11 performance indexes |
### Security & Performance Hardening (March 2026)

Following the initial professionalization, a **comprehensive security and performance hardening initiative** was completed:

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| **Phase 1** | Critical Security | JWT authentication (17 tests), CORS hardening (16 tests), CI/CD security fixes, 75 total security tests |
| **Phase 2** | Performance | N+1 query fixes, 13 database indexes, Redis caching layer, comprehensive input validation (33 tests) |

**Security Improvements:**
- ✅ Fixed CORS wildcard vulnerability with specific origin validation
- ✅ Implemented JWT authentication with HS256 tokens and refresh support
- ✅ Added production secret key validation
- ✅ Removed CI/CD security bypasses (`|| true` flags)
- ✅ Created 75 security tests covering headers, input sanitization, auth, and CORS

**Performance Improvements:**
- ✅ Fixed N+1 queries with `get_all_filtered()` database-level filtering
- ✅ Added 13 database indexes (industry, headquarters, composite, score fields)
- ✅ Implemented Redis caching with in-memory fallback for company data
- ✅ Created Pydantic validation schemas with 33 comprehensive validation tests

**Files Created:**
- `src/solstein/security/jwt_handler.py` - JWT token handling
- `src/solstein/security/cache.py` - Redis caching layer
- `src/solstein/api/schemas/validation.py` - Input validation schemas
- `tests/unit/test_*.py` - 158+ new tests across security, JWT, validation


**16+ ORM models** across two files:
- `src/solstein/infrastructure/database_models.py` — 17 models (companies, scoring, signals, research, enrichment, audit)
- `src/solstein/domain/facts.py` — 6 models (gathering batches, facts, sources, refresh, conflicts, calibration)

**11 Alembic migrations** covering the complete schema evolution from initial tables through FK constraints and index optimization.

### Test Coverage

| Category | Location | Count |
|----------|----------|-------|
| Unit | `tests/unit/` | 80+ test files |
| Integration | `tests/integration/` | 15+ test files |
| Data Quality | `tests/data_quality/` | Golden dataset regression |
| Performance | `tests/performance/` | Load tests |
| **Total** | `tests/` | **1,434+ collected** |

### Performance Baselines

| Operation | Target | Status |
|-----------|--------|--------|
| Company lookup by ID | <10ms | ✅ |
| Facts query by company | <50ms | ✅ |
| Full pipeline (1 company) | <2s | ✅ |

> Full professionalization details → [`PROFESSIONALIZATION.md`](PROFESSIONALIZATION.md)  
> Database schema reference → [`DATABASE_SCHEMA.md`](DATABASE_SCHEMA.md)  
> Testing guide → [`TESTING.md`](TESTING.md)

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). This is a proprietary platform — internal development only.

---

<div align="center">

*Built by* **AI Whisperers** *— finding the diamonds nobody knew were there.*

[![Contact](https://img.shields.io/badge/Contact-AI%20Whisperers-4b0082?style=for-the-badge&logoColor=ffd700)](mailto:contact@ai-whisperers.com)

</div>
