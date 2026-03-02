<div align="center">

# 𝔖𝔬𝔩𝔰𝔱𝔢𝔦𝔫

### *The Sunstone for Capital Navigation*

> *In Viking navigation, the solarsteinn revealed the sun behind the clouds.*
> *Solstein reveals the competitive landscape through market fog.*
> *Built by the Guild of Architects — not engineers. Wizards.*

[![Python](https://img.shields.io/badge/Python-3.10+-4b0082?style=for-the-badge&logo=python&logoColor=ffd700)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Live-4b0082?style=for-the-badge&logo=fastapi&logoColor=ffd700)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-1434+%20Collected-4b0082?style=for-the-badge&logo=pytest&logoColor=ffd700)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-~28%25-ffd700?style=for-the-badge&logo=codecov&logoColor=4b0082)](tests/)
[![License](https://img.shields.io/badge/License-Proprietary-4b0082?style=for-the-badge&logo=scroll&logoColor=ffd700)](LICENSE)

</div>

---

## 🎯 How It Works

Solstein combines **financial intelligence**, **technical signals**, and **market context** to deliver comprehensive company assessments:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Sources   │───→│  Scoring Engine │───→│  Attractiveness │
│ (AI-Orchestrated)│    │ (Multi-Factor)  │    │     Board       │
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

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.10+ |
| **Framework** | FastAPI | Latest |
| **Package Manager** | uv / pip | — |
| **Database** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 2.0+ (async) |
| **Data Processing** | Pandas | 2.x |
| **Excel Export** | OpenPyXL | 3.x |
| **Testing** | pytest | 8.x |
| **Linting** | ruff + black + mypy | Latest |
| **Task Queue** | Celery + Redis | Latest |

### Directory Structure

```
solstein/
├── src/solstein/
│   ├── adapters/            # Data source adapters (11 adapters)
│   ├── agents/              # Research agents (coordinator, GitHub, web…)
│   ├── analytics/           # Analysis tools, scorers, signals
│   ├── api/                 # FastAPI endpoints & 13 routers
│   ├── application/         # Application orchestration layer
│   ├── config/              # Pydantic-settings configuration (directory)
│   ├── core/                # Hexagonal architecture ports
│   ├── data/                # Data access layer (fetchers, connectors)
│   ├── domain/              # Domain models & value objects (DDD)
│   ├── exporters/           # LLM, Excel, CSV, PDF, Markdown exports
│   ├── extractors/          # LLM financial & markdown extractors
│   ├── infrastructure/      # Database, cache, repositories (18 tables)
│   ├── llm/                 # 13-provider LLM client with health checking
│   ├── migrations/          # Data migration scripts
│   ├── monitoring/          # Continuous monitoring
│   ├── presentation/        # Report templates & narrative generation
│   ├── research/            # Core research pipeline
│   ├── security/            # JWT handler
│   ├── utils/               # Shared utilities (logging)
│   ├── validation/          # Input validation
│   ├── celery_config.py     # Celery task queue configuration
│   ├── cli.py               # CLI entry point
│   ├── worker.py            # Background task worker
│   └── worker_tasks.py      # Celery task definitions
├── tests/                   # 6-layer test strategy (1,434+ tests)
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

---

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone <repo> && cd solstein
uv sync  # or: pip install -e .

# 2. Configure environment
cp .env.example .env
# Edit .env — set GITHUB_TOKEN and DATABASE__URL at minimum

# 3. Setup database
export PYTHONPATH=src && python -c "import asyncio; from solstein.infrastructure.database import init_db; asyncio.run(init_db())"

# 4. Start the API
PYTHONPATH=src python -m uvicorn solstein.api.main:app --reload

# 5. Run the test suite
pytest tests/
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | ✅ Yes | GitHub API token for data gathering |
| `DATABASE__URL` | ✅ Yes | PostgreSQL connection string |
| `SECURITY__SECRET_KEY` | ✅ Prod | JWT secret key (change in production) |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `GROQ_API_KEY` | Optional | Groq API key |
| `FIREWORKS_API_KEY` | Optional | Fireworks API key |
| `COMPANIES_HOUSE_API_KEY` | Optional | UK Companies House data |
| `GOOGLE_API_KEY` | Optional | Web search data gathering |

### LLM Provider Fallback

Solstein features a robust LLM provider fallback chain to ensure high availability:

```
Ollama (local) → Groq → Fireworks → SiliconFlow → Alibaba Cloud → Mistral → DeepInfra
```
  → Gemini → NVIDIA NIM → Cerebras → Kimi → Anthropic → OpenAI → Template Fallback

Set `LLM_PROVIDER=auto` (default) to enable automatic fallback, or pin a specific provider:

```bash
LLM_PROVIDER=ollama      # Local Ollama (llama3.2:latest, privacy-first)
LLM_PROVIDER=groq        # Groq (llama-3.3-70b-versatile, fast)
LLM_PROVIDER=fireworks   # Fireworks (mixtral-8x22b-instruct, cost-effective)
LLM_PROVIDER=siliconflow # SiliconFlow (Chinese cloud)
LLM_PROVIDER=alibaba     # Alibaba Cloud
LLM_PROVIDER=mistral     # Mistral (European LLM)
LLM_PROVIDER=deepinfra   # DeepInfra (cost-effective inference)
LLM_PROVIDER=gemini      # Google Gemini
LLM_PROVIDER=nvidia      # NVIDIA NIM (enterprise inference)
LLM_PROVIDER=cerebras    # Cerebras (fast chips)
LLM_PROVIDER=kimi        # Kimi / Moonshot
LLM_PROVIDER=anthropic   # Anthropic Claude (premium reasoning)
LLM_PROVIDER=openai      # OpenAI (gpt-4o-mini)
LLM_PROVIDER=none        # Disable LLM, use template fallback
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Platform health check |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/healthz` | K8s liveness probe alias |
| `POST` | `/auth/login` | JWT authentication |
| `GET` | `/companies` | List all profiled companies |
| `GET` | `/companies/{id}` | Retrieve single company profile |
| `POST` | `/scoring/company/{id}/score` | Score a specific company |
| `GET` | `/scoring/stats` | Market-wide scoring statistics |
| `GET` | `/market/analysis` | Full market landscape analysis |
| `GET` | `/market/search` | Search companies by query |
| `GET` | `/market/overlap/{id}` | Competitive overlap analysis |
| `GET` | `/export` | Generate intelligence report (excel/csv/pdf/markdown) |
| `GET` | `/jobs/{workflow_id}` | Job status — **501 Not Implemented** (disabled) |
| `POST` | `/simulation/run` | Run market simulation scenario |

> Full API reference → [`docs/api/reference.md`](docs/api/reference.md) | Interactive docs → `/docs`

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

## 📚 Documentation

| Document | Contents |
|----------|----------|
| 📜 [`docs/architecture.md`](docs/architecture.md) | Architecture overview & diagrams |
| 📜 [`docs/development.md`](docs/development.md) | Development commands & workflows |
| 📜 [`docs/api.md`](docs/api.md) | API endpoint documentation |
| 📜 [`docs/guides/developer.md`](docs/guides/developer.md) | Developer setup & contribution guide |
| 📜 [`docs/guides/operator.md`](docs/guides/operator.md) | Deployment & operations guide |
| 📜 [`docs/api/reference.md`](docs/api/reference.md) | Full API reference |
| 📜 [`docs/architecture/decisions.md`](docs/architecture/decisions.md) | Architecture decision records |
| 📜 [`docs/PITCH/executive-brief.md`](docs/PITCH/executive-brief.md) | One-page investor brief |
| 📜 [`docs/PITCH/case-study.md`](docs/PITCH/case-study.md) | Live case: 29 companies, European energy software |
| 📜 [`docs/LORE/origin.md`](docs/LORE/origin.md) | The origin story |

---

## 🧪 Testing

Solstein follows a **6-layer testing strategy**:

1. **Unit** — Isolated component tests; domain models and scoring math
2. **Integration** — All API endpoints with deterministic mock repositories
3. **Data Quality** — Golden Dataset regression to protect classification boundaries
4. **Performance** — Benchmarks and load tests for critical paths
5. **Property** — Hypothesis-based property testing
6. **Agents** — AI agent behavior tests

```bash
pytest tests/unit/          # Fast, pure logic
pytest tests/integration/   # API contract tests
pytest tests/data_quality/  # Golden dataset regressions
pytest tests/performance/   # Benchmarks
pytest tests/property/      # Property-based tests
pytest -m agents            # AI agent behavior tests
pytest                      # Full suite (auto-runs coverage per pyproject.toml)
```

| Category | Location | Purpose |
|----------|----------|---------|
| Unit | `tests/unit/` | Isolated component tests |
| Integration | `tests/integration/` | Cross-component tests |
| Data Quality | `tests/data_quality/` | Classification boundary regressions |
| Performance | `tests/performance/` | Benchmarks and load tests |
| Property | `tests/property/` | Hypothesis-based property tests |
| Agents | `tests/test_agents/` | AI agent behavior tests |
| **Total** | `tests/` | **1,434+ collected** |

---

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). This is a proprietary platform — internal development only.

---

<div align="center">

*Built by* **AI Whisperers** *— finding the diamonds nobody knew were there.*

[![Contact](https://img.shields.io/badge/Contact-AI%20Whisperers-4b0082?style=for-the-badge&logoColor=ffd700)](mailto:contact@ai-whisperers.com)

</div>
