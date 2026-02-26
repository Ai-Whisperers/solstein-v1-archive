# 📁 Repository Structure

*A map of the vault.*

---

## Top-Level Layout

```
solstein/
├── src/solstein/        ← The platform (FastAPI, scoring, exporters, research)
├── tests/               ← Test suite (unit, integration, data quality)
├── docs/                ← All documentation (this folder)
├── data/                ← Input data (data/input/) + output (data/output/)
├── bin/                 ← Agent deployment and orchestration scripts
├── scripts/             ← Utility and setup scripts
├── docker/              ← Docker, Compose, Grafana, Prometheus configs
├── supabase/            ← Supabase database migrations
├── alembic/             ← Alembic database migrations
├── .github/workflows/   ← CI pipelines (ci.yml, ci-12stage.yml, mutation.yml, etc.)
├── pyproject.toml       ← Project metadata, dependencies, tool config
├── Makefile             ← Common tasks (install, test, lint, docker)
└── mkdocs.yml           ← Documentation site configuration
```

---

## Source Layout — `src/solstein/`

```
src/solstein/
├── cli.py                   ← Click CLI (extract, score, export-excel, analyze-market)
├── config.py                ← Application settings (Pydantic BaseSettings, .env support)
├── constants.py             ← Shared constants
├── exceptions.py            ← Custom exception hierarchy
├── worker.py                ← Celery app initialization
├── worker_tasks.py          ← Celery task definitions (14 refresh tasks)
├── celery_config.py         ← Celery configuration
├── adapters/
│   ├── protocols.py         ← EnrichmentSource + UnifiedDataSource protocols
│   ├── registry.py          ← Unified source registry
│   ├── instrumented.py      ← Instrumented adapter wrappers
│   ├── discovery/           ← Discovery adapters (competitor_json, static_catalog, web_search)
│   ├── enrichment/          ← Enrichment adapters (yahoo_finance, news, linkedin, patents, etc.)
│   └── signals/             ← Signal adapters
├── agents/
│   ├── base_agent.py        ← Base agent class
│   ├── coordinator_agent.py ← Agent orchestration
│   ├── github_agent.py      ← GitHub data collection
│   ├── companies_house_agent.py, web_search_agent.py, website_agent.py
│   └── resilience.py        ← Retry/circuit-breaker for agents
├── analytics/
│   ├── scoring.py           ← GrowthScorer, MarketAnalyzer, CompetitiveOverlapCalculator
│   ├── workflows.py         ← Temporal/batch workflow stubs
│   ├── confidence_integration.py ← Calibrated confidence provider
│   ├── scorers/             ← Individual scorers (growth_momentum, financial_health, competitive_position)
│   ├── signals/             ← Signal extraction (models, extractors)
│   ├── simulation/          ← Market simulation engine
│   ├── filters/             ← LLM and keyword filters
│   └── valuation/           ← Valuation models and analyzers
├── api/
│   ├── main.py              ← FastAPI app entry point (CORS, lifespan, router mounts)
│   ├── dependencies.py      ← Dependency injection (auth, repository)
│   ├── exceptions.py        ← API exception handlers
│   ├── middleware.py        ← Request/response middleware
│   ├── middleware/
│   │   ├── logging.py       ← Request/response logging middleware
│   │   └── security.py      ← Security headers middleware
│   ├── routers/
│   │   ├── companies.py     ← GET/POST/DELETE /companies
│   │   ├── scoring.py       ← POST /scoring/company/{id}/score, GET /scoring/batch, /stats
│   │   ├── market.py        ← GET /market/analysis, /market/overlap/{id}, /market/search
│   │   ├── export.py        ← GET /export/excel, /export/json, /export/search/llm
│   │   ├── drill_down.py    ← GET /drill-down/company/{id}/why, /sources, /facts, etc.
│   │   ├── health.py        ← GET /health, /health/status, /health/ready, /health/live
│   │   ├── jobs.py          ← GET /jobs/{workflow_id}
│   │   ├── simulation.py    ← POST /simulation/run
│   │   ├── enrichment.py    ← Enrichment REST API (8 endpoints)
│   │   └── async_jobs.py    ← Async job management
│   ├── routes/
│   │   └── refresh.py       ← POST/GET /refresh endpoints
│   ├── schemas/
│   │   └── enrichment.py    ← Enrichment Pydantic schemas
│   └── services/
│       ├── drill_down_service.py
│       └── enrichment_service.py ← Enrichment service layer
├── core/
│   ├── repositories.py      ← Abstract interfaces (CompanyRepository, CompanyFilter)
│   ├── scoring_config.py    ← Pydantic scoring configuration (thresholds, weights)
│   ├── supabase_client.py   ← Supabase client setup
│   ├── monitoring.py        ← Production monitoring
│   └── production_hardening.py
├── data/
│   ├── loaders.py           ← JSON ingestion (CompetitorDataLoader, BondYieldLoader)
│   ├── repositories.py      ← JsonFileRepository, SupabaseRepository
│   ├── company_research.py  ← CompanyResearch Pydantic model + CompanyResearcher
│   ├── fetchers.py          ← YahooFinanceFetcher, CurrencyRateFetcher, GlobalMarketLoader
│   ├── markets.py           ← Currency, MarketRegion, StockExchange, MarketIndex
│   ├── enrichment_orchestrator.py ← Enrichment pipeline orchestrator
│   ├── enrichment_config.py ← Enrichment source configuration
│   ├── enrichment_service.py ← Data enrichment service
│   ├── enrichment_validators.py ← Input validation & sanitization
│   ├── error_logging.py     ← Structured error logging
│   ├── security_hardening.py ← Rate limiter & security
│   ├── unified_loader.py    ← Unified data loader
│   └── connectors/          ← Data connectors (companies_house, sec_edgar, news_signal)
├── domain/
│   ├── models.py            ← Pure domain entities (Company, FinancialMetric, RawDataSource, enums)
│   ├── facts.py             ← Fact models
│   ├── simulation.py        ← Simulation models
│   └── validators.py        ← Domain validators
├── exporters/
│   ├── excel.py             ← ExcelExporter, TemplateExporter (openpyxl)
│   ├── audit_report.py      ← PipelineAuditReportGenerator
│   ├── llm.py               ← LLMReportEnhancer, SWOTAnalysis
│   └── markdown/            ← ReportGenerator, ClientReportGenerator
├── extractors/
│   └── markdown_extractor.py ← Markdown-to-profile extraction pipeline
├── infrastructure/
│   ├── database.py          ← Database connection/session
│   ├── database_models.py   ← SQLAlchemy ORM models
│   ├── database_service.py  ← Database service layer
│   ├── enrichment_repositories.py ← DB repositories
│   ├── conflict_resolution.py ← ConflictResolutionEngine
│   ├── confidence_adjustment.py ← Confidence calibration
│   ├── refresh.py           ← Refresh orchestrator
│   ├── unified_registry.py  ← Unified source registry
│   ├── retry_policy.py      ← Retry policies
│   └── connectors/          ← 12 refresh connectors (yahoo_finance, news, linkedin, etc.)
├── monitoring/
│   └── continuous_monitor.py
├── presentation/            ← Presentation layer
│   ├── adaptive_templates.py
│   ├── data_quality_indicators.py
│   └── narrative_consistency_checker.py
├── research/
│   ├── aggregate.py         ← Data aggregation + fact extraction
│   ├── pipeline.py          ← Research pipeline
│   ├── gather.py            ← Data gathering
│   ├── discovery.py         ← Company discovery
│   ├── signals.py           ← Signal processing
│   ├── evidence.py          ← Evidence tracking
│   └── sources.py           ← Source management
└── utils/
    └── logging.py           ← Logging utilities
```

---

## Agent Deployment — `bin/`

```
bin/
├── agents/
│   ├── runner.py              ← Cycle execution: test suite + quality metrics (mypy, bandit, radon)
│   ├── critiquer.py           ← Analyze issues found by runner
│   ├── planner.py             ← Create improvement plan from critique
│   ├── implementer.py         ← Apply planned fixes
│   ├── documenter.py          ← Record audit trail for each cycle
│   ├── hostinger-safe.py      ← Hostinger environment detection + Telegram rate limiting
│   └── rate-limiter.py        ← API call rate limiting + response caching
├── orchestrate_agents.py      ← 5-agent sequential orchestrator (6h cycles)
├── monitor-live.sh            ← Live monitoring dashboard (systemd/journalctl)
├── solstein-agents.service    ← systemd service unit
└── solstein-agents.timer      ← systemd timer (6h intervals)
```

**Cycle flow**: Runner → Critiquer → Planner → Implementer → Documenter (every 6 hours)


## Tests Layout — `tests/`

```
tests/
├── conftest.py              ← Shared fixtures (mock_repo, mock_company, client)
├── factories.py             ← Single source of truth for test object creation
├── test_fastapi.py          ← API integration tests
├── unit/                    ← 50+ unit test files
│   ├── test_models.py       ← Domain model property and edge case tests
│   ├── test_scoring.py      ← Scoring engine unit tests (parametrized, approx)
│   ├── test_cli.py          ← CLI tests
│   ├── test_exporters.py    ← Exporter tests
│   ├── test_resilience.py   ← Retry/resilience tests
│   ├── adapters/            ← Adapter tests (test_protocols.py)
│   ├── data/                ← Data connector tests
│   └── research/            ← Research pipeline tests (test_aggregate_extractors.py)
├── integration/
│   ├── conftest.py
│   ├── test_coordinator_to_api.py
│   ├── test_data_gathering_e2e.py
│   ├── test_full_pipeline.py
│   ├── test_golden_dataset_regression.py
│   ├── test_resilience_scenarios.py
│   ├── test_enrichment_api.py
│   ├── test_connector_enrichment.py
│   └── test_phase_11_12_integration.py
└── data_quality/
    └── test_ai_insights.py  ← Golden dataset regression tests
```

---

## Quick Commands

```bash
# Install
pip install -e ".[dev]"

# Run API (hot reload)
uvicorn solstein.api.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A solstein.worker worker --loglevel=info

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing
```

Or with Make:

```bash
make install     # Set up virtualenv + dependencies
make run         # Start API server
make test        # Run full suite
make lint        # ruff + mypy
make coverage    # Coverage report
```

---

## Data Flow

```
Input JSON / API Sources    CLI / API Request
(data/input/)        →     identify market
        ↓
    CompetitorDataLoader + Enrichment Adapters
        ↓
    Enrichment Pipeline Orchestrator (Enrichment Pipeline)
        ↓
    JsonFileRepository / SupabaseRepository
        ↓
    GrowthScorer / MarketAnalyzer / CompetitiveOverlapCalculator
        ↓
    API Response / ExcelExporter / ReportGenerator / Celery Task
        ↓
    Output (data/output/)
```

---

*Last Updated: February 26, 2026*
