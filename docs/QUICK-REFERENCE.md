# ⚡ Solstein Quick Reference

**One-page cheat sheet for common tasks and locations.**

---

## 🚀 Getting Started

| Task | Command | Reference |
|------|---------|-----------|
| **Clone repo** | `git clone <url> && cd solstein` | [Setup](guides/developer.md) |
| **Install deps** | `pip install -e ".[dev]"` | [Setup](guides/developer.md) |
| **Run API** | `uvicorn solstein.api.main:app --reload` | [Setup](guides/developer.md) |
| **Run workers** | `celery -A solstein.worker worker --loglevel=info` | [Setup](guides/developer.md) |
| **Run tests** | `pytest tests/` | [Testing](guides/developer.md) |
| **Run with Docker** | `docker compose up` | [Docker](guides/operator.md) |

---

## 📂 File Locations

| What | Location |
|-----|----------|
| **Source code** | `src/solstein/` |
| **Tests** | `tests/` |
| **Documentation** | `docs/` |
| **Data input** | `data/input/` |
| **Data output** | `data/output/` |
| **Docker files** | `docker/` |
| **Configuration** | `src/solstein/config.py` or `.env` |
| **Environment vars** | `.env` (root) |
| **Database schema** | `supabase/migrations/` |
| **Alembic migrations** | `alembic/` |
| **Agent scripts** | `bin/agents/` |
| **Enrichment API** | `src/solstein/api/routers/enrichment.py` |"],op:

---

## ⚙️ Key Configuration

### Environment Variables

```env
# Database
SOLSTEIN_DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
SOLSTEIN_DATABASE__POOL_SIZE=20

# Redis (Celery)
SOLSTEIN_REDIS__URL=redis://localhost:6379/0

# API
SOLSTEIN_API__HOST=127.0.0.1
SOLSTEIN_API__PORT=8000
SOLSTEIN_API__DEBUG=false

# Supabase (optional)
SOLSTEIN_SUPABASE__URL=https://your-project.supabase.co
SOLSTEIN_SUPABASE__KEY=your-anon-key
```

**Location:** `.env` file in project root

**Reference:** [Database Setup](guides/database.md) | [Operator Guide](guides/operator.md)

---

## 🧪 Testing

| Level | Command | Where |
|-------|---------|-------|
| **Unit tests** | `pytest tests/unit/` | `tests/unit/` |
| **Integration tests** | `pytest tests/integration/` | `tests/test_fastapi.py` |
| **Data quality** | `pytest tests/data_quality/` | `tests/data_quality/` |
| **All tests** | `pytest tests/` | — |
| **With coverage** | `pytest tests/ --cov=src/solstein` | — |
| **Specific test** | `pytest tests/unit/test_models.py::test_function_name` | — |

**Fixtures:** See `tests/conftest.py`  
**Test data factories:** See `tests/factories.py`

---

## 📊 API Endpoints (Quick Reference)

**Base URL:** `http://localhost:8000`  
**Full docs:** `http://localhost:8000/docs` (Swagger UI)

| Method | Endpoint | What It Does |
|--------|----------|-------------|
| `GET` | `/health` | API health check |
| `GET` | `/health/status` | Full health status |
| `GET` | `/companies` | List all companies |
| `GET` | `/companies/{id}` | Get single company |
| `POST` | `/companies` | Create new company |
| `POST` | `/scoring/company/{id}/score` | Score a company |
| `GET` | `/scoring/batch` | Batch scoring |
| `GET` | `/scoring/stats` | Scoring statistics |
| `GET` | `/market/analysis` | Full market analysis |
| `GET` | `/market/search?q=...` | Search companies |
| `GET` | `/market/overlap/{id}` | Competitive overlap |
| `GET` | `/export/excel` | Generate Excel report |
| `GET` | `/export/json` | Export as JSON |
| `GET` | `/drill-down/company/{id}/why/{signal}` | Signal drill-down |
| `GET` | `/drill-down/company/{id}/facts` | Extracted facts |
| `POST` | `/simulation/run` | Run market simulation |
| `GET` | `/jobs/{workflow_id}` | Check job status |
| `POST` | `/refresh/{source_name}` | Trigger data refresh |
| `GET` | `/refresh/sources` | List refresh sources |
| `POST` | `/companies/{id}/enrich` | Enrich a single company |
| `POST` | `/companies/enrich/batch` | Batch enrichment |
| `GET` | `/companies/{id}/enrichment/audit` | Audit trail |
| `GET` | `/companies/{id}/enrichment/cache` | Cache status |
| `POST` | `/enrichment/cache/clear` | Clear enrichment cache |
| `POST` | `/jobs/submit` | Submit async job |
| `GET` | `/jobs/{job_id}/status` | Job status |"],op:

**Full reference:** [API Reference](api/reference.md)

---

## 🏗️ Project Structure (30-Second Version)

```
src/solstein/
├── api/              ← FastAPI routes & schemas
├── adapters/         ← Data source adapters & protocols
├── agents/           ← AI data collection agents
├── analytics/        ← Scoring & market analysis logic
├── domain/           ← Pure business models
├── data/             ← Repository & data loading
├── core/             ← Interfaces & configuration
├── exporters/        ← Excel, Markdown, LLM reports
├── infrastructure/   ← DB, refresh connectors, conflict resolution
├── research/         ← Data aggregation & pipeline
└── worker_tasks.py   ← Celery background jobs
```

**Full structure:** [Repository Structure](STRUCTURE.md)

---

## 🐛 Common Issues & Solutions

| Problem | Check | Solution |
|---------|-------|----------|
| **"Connection refused"** | Port 8000/6379/5432 | `brew services start postgresql@15 redis` |
| **"Database not found"** | `data/input/` folder | Run seed script: `python -m solstein.data.seed_db` |
| **"Tests failing"** | `.env` file | Copy `pytest.ini`, verify `PYTHONPATH=src:.:` |
| **"Module not found"** | Virtual env | `source venv/bin/activate && pip install -e ".[dev]"` |
| **"Celery tasks not running"** | Redis running? | `redis-cli ping` should return `PONG` |

**Full troubleshooting:** [Troubleshooting Guide](guides/troubleshooting.md)

---

## 📝 Key Classes & Functions

| Class | Location | Purpose |
|-------|----------|---------|
| `Company` | `src/solstein/domain/models.py` | Core domain model |
| `GrowthScorer` | `src/solstein/analytics/scoring.py` | Scoring engine |
| `CompanyRepository` | `src/solstein/core/repositories.py` | Data access interface |
| `SupabaseRepository` | `src/solstein/data/repositories.py` | Supabase implementation |
| `ExcelExporter` | `src/solstein/exporters/excel.py` | Report generation |
| `CompanyResearch` | `src/solstein/data/company_research.py` | Company intel Pydantic model |
| `ConflictResolutionEngine` | `src/solstein/infrastructure/conflict_resolution.py` | Multi-source conflict resolver |
| `RawDataSource` | `src/solstein/domain/models.py` | Raw data container model |
| `CompetitorDataLoader` | `src/solstein/data/loaders.py` | JSON data ingestion |
| `UnifiedDataLoader` | `src/solstein/data/unified_loader.py` | Multi-source data unification |
| `EnrichmentOrchestrator` | `src/solstein/data/enrichment_orchestrator.py` | Enrichment pipeline |"],op:

---

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/FD-123-my-feature
```

### 2. Make Changes

- Edit code in `src/solstein/`
- Add tests in `tests/`
- Update docs if needed

### 3. Verify Quality

```bash
# Format
make format      # or: ruff format src/ tests/

# Lint
make lint        # or: ruff check src/ tests/

# Type check
mypy src/

# Test
pytest tests/ --cov=src/solstein
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature (FD-123)"
```

**Commit format:** [Conventional Commits](guides/code-conventions.md)

### 5. Create PR

```bash
git push origin feature/FD-123-my-feature
# Create PR on GitHub
```

**Checklist:** [Review Checklist](guides/documentation-review.md)

---

## 📚 Documentation Map

| Need | Read |
|------|------|
| **Getting started** | [Quick Start](README.md) + [Developer Guide](guides/developer.md) |
| **Business context** | [Executive Brief](PITCH/executive-brief.md) |
| **Architecture** | [ADRs](architecture/decisions.md) + [STRUCTURE](STRUCTURE.md) |
| **Database setup** | [Database Guide](guides/database.md) |
| **Deployment** | [Operator Guide](guides/operator.md) |
| **Contributing** | [Developer Guide](guides/developer.md) |
| **API usage** | [API Reference](api/reference.md) |
| **Background story** | [The Lore](LORE/origin.md) |

---

## 🎯 Code Standards

| Tool | Command | Config |
|------|---------|--------|
| **Format** | `ruff format src/ tests/` | `pyproject.toml` |
| **Lint** | `ruff check src/ tests/` | `pyproject.toml` |
| **Type check** | `mypy src/` | `pyproject.toml` |
| **Tests** | `pytest tests/` | `pyproject.toml` |

**Key rules:**
- ✅ Type hints on all functions
- ✅ No silent failures (`except: pass`)
- ✅ Tests for new features
- ✅ Docstrings on public functions
- ❌ No hardcoded paths (use `settings.data_dir`)

---

## 🚨 Before Pushing to main

- [ ] `pytest tests/ --cov=src/solstein` passes
- [ ] `ruff check src/ tests/` has no errors
- [ ] `mypy src/` has no errors
- [ ] CHANGELOG.md updated
- [ ] Documentation updated (if needed)
- [ ] No debug code left behind

---

## 🔗 External Links

- **GitHub:** [Ai-Whisperers/solstein](https://github.com/Ai-Whisperers/solstein)
- **Docs Site:** [ai-whisperers.github.io/solstein](https://ai-whisperers.github.io/solstein)
- **FastAPI Docs:** `http://localhost:8000/docs`
- **Supabase:** [supabase.com/dashboard](https://supabase.com/dashboard)

---

## ❓ Can't Find It?

Try searching:
- 📖 **What does X mean?** → [Glossary](GLOSSARY.md)
- 🔍 **Where is file X?** → Check [STRUCTURE.md](STRUCTURE.md)
- 📝 **How do I...?** → Search guides, or check [Code Conventions](guides/code-conventions.md)
- 🚀 **How to deploy?** → [Operator Guide](guides/operator.md)

---

*Last Updated: February 26, 2026*
*Keep this page bookmarked!*

