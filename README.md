<div align="center">

# 𝔖𝔬𝔩𝔰𝔱𝔢𝔦𝔫

### *The Sunstone for Capital Navigation*

> *In Viking navigation, the solarsteinn revealed the sun behind the clouds.*
> *Solstein reveals the competitive landscape through market fog.*
> *Built by the Guild of Architects — not engineers. Wizards.*

[![Python](https://img.shields.io/badge/Python-3.12-4b0082?style=for-the-badge&logo=python&logoColor=ffd700)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Live-4b0082?style=for-the-badge&logo=fastapi&logoColor=ffd700)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-Workers-4b0082?style=for-the-badge&logo=celery&logoColor=ffd700)](https://docs.celeryq.dev)
[![Tests](https://img.shields.io/badge/Tests-90%20Passing-4b0082?style=for-the-badge&logo=pytest&logoColor=ffd700)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-57%25-ffd700?style=for-the-badge&logo=codecov&logoColor=4b0082)](tests/)
[![License](https://img.shields.io/badge/License-Proprietary-4b0082?style=for-the-badge&logo=scroll&logoColor=ffd700)](LICENSE)

> **📖 Documentation Site**: [https://ai-whisperers.github.io/solstein/](https://ai-whisperers.github.io/solstein/)

</div>

---

## 📜 What Is Solstein?

Companies are born with wings. They start light, agile, and fast. But as they grow, something heavy begins to form — a manual process here, a temporary workaround there, a script that only one person understands and that person left six months ago.

Slowly. Inevitably. **The wings turn to lead.**

**Solstein is the Sunstone** — the instrument that sees through market fog and tells Private Equity exactly which companies are flying, which are drifting, and which are sinking under the Gravity of Legacy.

It replaces the old ritual — EUR 500K–1.5M to McKinsey, 90 days to wait, a static PDF on delivery — with AI-orchestrated market intelligence built by a **Guild of Wizards**, delivered in **days, not months**.

The core output is an **Attractiveness Board**: ranked, clickable, fully-explainable. Every score exposes its signal chain. No black boxes. No "trust the algorithm."

> *It does not replace the analyst. It gives the analyst a sunstone.*

---

## 🔥 The Classification System

Every company in a market is scored and classified:

| Classification | Growth Score | What It Means |
|---|---|---|
| 🚀 **Rocket** | ≥ 7.0 | High-growth, AI-native or rapidly adopting. Act now. |
| ⚖️ **Neutral** | 4.0 – 7.0 | Stable players. Watch for directional signals. |
| 🦕 **Dinosaur** | ≤ 4.0 | Legacy weight. Hidden diamonds or dead weight. Assess the people. |

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
│   ├── analytics/        ← GrowthScorer, MarketAnalyzer
│   ├── core/             ← Scoring config, repository interfaces
│   ├── data/             ← JSON loaders, data repositories
│   ├── domain/           ← Pure domain models (Company, FinancialMetric)
│   ├── exporters/        ← Excel report generation
│   └── tasks.py          ← Celery background workers
├── tests/
│   ├── unit/             ← Domain models & scoring logic
│   ├── integration/      ← API endpoints & worker tasks
│   └── data_quality/     ← Golden dataset regression tests
├── docs/
│   ├── LORE/             ← The origin story & strategic narrative
│   ├── PITCH/            ← Investor & client-facing materials
│   ├── guides/           ← Developer & operator guides
│   ├── api/              ← API reference
│   └── architecture/     ← Architecture decision records
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

## 📚 Documentation

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

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). This is a proprietary platform — internal development only.

---

<div align="center">

*Built by* **AI Whisperers** *— finding the diamonds nobody knew were there.*

[![Contact](https://img.shields.io/badge/Contact-AI%20Whisperers-4b0082?style=for-the-badge&logoColor=ffd700)](mailto:contact@ai-whisperers.com)

</div>
