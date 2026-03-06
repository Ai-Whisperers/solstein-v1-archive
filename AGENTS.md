# Solstein - AI-Powered Competitive Intelligence Platform

> **AGENTS.md v3.0** | Claude Code v1.0+ Standard  
> Last Updated: 2026-03-01  
> Source of truth: verified against actual codebase

## Quick Reference

```yaml
project: solstein
language: python
framework: fastapi
architecture: domain-driven + hexagonal
ai_ready: true
mcp_servers: [filesystem, sequential-thinking, memory]
python_min: "3.10"
```

## Project Identity

**What is this?**  
AI-powered competitive intelligence platform for PE/VC professionals. Analyzes market data, company financials, competitive positioning, and generates strategic insights using 13 LLM providers with automatic failover.

**Why does it exist?**  
Private equity and venture capital firms need rapid, data-driven competitive analysis. Traditional research is slow and expensive. Solstein automates this with AI.

**Who maintains it?**  
Core team with AI-assisted development via Claude Code.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.10+ |
| **Framework** | FastAPI | Latest |
| **Package Manager** | uv / pip | - |
| **Database** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 2.0+ (async) |
| **Driver** | asyncpg | Latest |
| **Task Queue** | Celery + Redis | Latest |
| **LLM Orchestration** | LangGraph | 0.0.20+ |
| **Data Processing** | Pandas | 2.x |
| **Excel Export** | OpenPyXL | 3.x |
| **Supabase** | supabase-py | 2.3+ |
| **Testing** | pytest | 8.x |
| **Linting** | ruff + black | Latest |
| **Type Check** | mypy | Latest (partial coverage) |
| **CLI** | Click | 8.x |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│    FastAPI · 13 Routers · WebSocket · TenantMiddleware       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Research   │    │  Analytics   │    │   Export     │
│   Pipeline   │    │   Engine     │    │   Engine     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Domain Layer (Business Logic)                   │
│     Models · Value Objects · Repository Interfaces          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PostgreSQL   │    │    Redis     │    │  LLM Layer   │
│  14+ (async) │    │ Cache+Celery │    │ 13 providers │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Directory Structure

```
solstein/
├── src/solstein/
│   ├── adapters/            # Data source adapters
│   │   ├── aggregation/     # Multi-source data aggregation
│   │   ├── discovery/       # Company discovery strategies
│   │   ├── enrichment/      # Per-source enrichment adapters (11 adapters)
│   │   └── signals/         # Signal extraction adapters
│   ├── agents/              # Research agents (coordinator, GitHub, web, etc.)
│   ├── analytics/           # Analysis tools
│   │   ├── filters/         # Data filters
│   │   ├── scorers/         # Scoring: growth, financial_health, competitive_position
│   │   ├── signals/         # Signal extractors and models
│   │   ├── simulation/      # Market simulation
│   │   └── valuation/       # Valuation models
│   ├── api/                 # FastAPI application
│   │   ├── middleware/      # Request middleware (logging, rate_limit, security, tenant)
│   │   ├── routers/         # 13 route handlers (auth, companies, scoring, market…)
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── services/        # API-layer services (drill_down, enrichment)
│   │   ├── websocket/       # WebSocket support
│   │   └── dependencies.py, main.py, exceptions.py
│   ├── application/         # Application orchestration layer
│   ├── config/              # Pydantic-settings configuration (directory)
│   ├── core/                # Hexagonal architecture ports
│   ├── data/                # Data access layer (fetchers, loaders, connectors)
│   ├── domain/              # Business entities (DDD)
│   │   ├── models.py        # Company, FinancialMetric, MarketAnalysis, etc.
│   │   ├── facts.py         # Fact-related domain objects
│   │   ├── value_objects.py # Value objects
│   │   └── repository_interfaces.py
│   ├── exceptions.py        # Top-level exception hierarchy
│   ├── exporters/           # Export format generators
│   │   ├── markdown/        # Markdown export (directory with 4 files)
│   │   ├── excel.py, excel_improved.py, csv.py, pdf.py, llm.py, audit_report.py
│   ├── extractors/          # LLM financial extractor, markdown extractor
│   ├── infrastructure/      # External infrastructure adapters
│   │   ├── connectors/      # 11 data connectors (sec_edgar, linkedin, github…)
│   │   ├── database.py      # Async engine and session factory
│   │   ├── database_models.py  # All 18 SQLAlchemy ORM models
│   │   ├── cache.py         # Redis cache client
│   │   ├── company_repository.py
│   │   └── repositories.py, enrichment_repositories.py, outbox_worker.py…
│   ├── llm/                 # 13-provider LLM client with health checking
│   │   ├── health_checker.py, enhanced_client.py, structured_client.py, tracing.py
│   ├── migrations/          # Data migration scripts
│   ├── monitoring/          # Continuous monitoring
│   ├── presentation/        # Report templates and narrative generation
│   ├── research/            # Core research pipeline (gather, aggregate, reconcile…)
│   ├── security/            # JWT handler
│   ├── utils/               # Shared utilities (logging)
│   ├── validation/          # Input validation (company, financial sanity)
│   ├── cli.py               # CLI entry point
│   ├── celery_config.py     # Celery task queue configuration
│   ├── worker.py            # Background task worker
│   └── worker_tasks.py      # Celery task definitions
├── tests/
│   ├── unit/                # Unit tests (adapters, agents, analytics, domain, research)
│   ├── integration/         # Integration tests (real DB)
│   ├── data_quality/        # Data validation tests
│   ├── performance/         # Benchmarks and load tests
│   ├── property/            # Property-based tests (Hypothesis)
│   ├── test_agents/         # AI agent behavior tests
│   ├── factories/           # Test data factories (factory-boy)
│   ├── fixtures/            # Shared pytest fixtures
│   ├── mocks/               # Mock objects
│   └── snapshots/           # Snapshot test data (syrupy)
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## Development Commands

### Setup
```bash
# Install dependencies (preferred)
uv sync

# Or with pip (editable install)
pip install -e .

# Set PYTHONPATH (required for all commands)
export PYTHONPATH=src

# Initialize database
python -c "import asyncio; from solstein.infrastructure.database import init_db; asyncio.run(init_db())"
```

### Development
```bash
# Set PYTHONPATH first
export PYTHONPATH=src

# Run API server
uvicorn solstein.api.main:app --reload --host 0.0.0.0 --port 8000

# Run CLI
solstein --help

# Start Celery worker (required for enrichment tasks)
celery -A solstein.celery_config worker --loglevel=info
```

### Quality
```bash
# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test layer
pytest -m unit
pytest -m integration
pytest -m data_quality
pytest -m agents

# Type check (partial coverage)
mypy .

# Format and lint
black . && ruff check --fix .

# Full check
make check-all
```

### Claude Code Integration
```bash
# Check MCP servers
make mcp-check

# Run smoke tests
./scripts/Claude-mcp-smoke-test.sh

# Doctor check
./scripts/Claude-mcp-doctor.sh
```

## Code Standards

### Formatting
- **Line Length**: 120 characters (Black)
- **Import Order**: isort (stdlib → third-party → local)
- **Type Hints**: Required for functions under mypy coverage
- **Docstrings**: Google style

### Naming
| Type | Convention | Example |
|------|-----------|---------|
| Modules | snake_case | `research_analyzer.py` |
| Classes | PascalCase | `CompetitiveAnalyzer` |
| Functions | snake_case | `analyze_competitor()` |
| Constants | UPPER_SNAKE | `MAX_RETRY_ATTEMPTS` |

### Anti-Patterns (⛔)
```python
# ❌ Bare except
except:
    pass

# ❌ Mutable defaults
def func(items=[]):
    ...

# ❌ Print statements
print("debug")

# ❌ Type suppression
value = some_func()  # type: ignore
```

### Best Practices (✅)
```python
# ✅ Structured error handling
from loguru import logger

try:
    result = await operation()
except SpecificError as e:
    logger.error("Operation failed", error=str(e))
    raise BusinessError("User-friendly message") from e

# ✅ Type hints
def analyze_company(company_id: str) -> AnalysisResult:
    ...

# ✅ Logging
logger.info("Processing company", company_id=company_id)
```

## Database

### Connection
```yaml
type: postgresql
driver: asyncpg
orm: sqlalchemy 2.0
pool_size: 20
max_overflow: 10
timeout: 30s
```

### Key ORM Models (18 tables total)

**Competitive Intelligence (Integer PKs):**
- `CompanyRecord` — Core company profiles (~42 columns incl. financials, AI scores)
- `ScoringRecord` — Point-in-time scoring snapshots per company
- `SignalRecord` — Individual signals driving each scoring record
- `MarketSnapshot` — Aggregate market state snapshots
- `AuditTrailRecord` — Full per-company analysis audit trail
- `EnrichmentCacheRecord` — TTL-based enrichment cache (default 24h)
- `EnrichmentAuditRecord` — Per-operation enrichment audit log
- `EnrichmentJobRecord` — Celery enrichment task tracking

**Research Pipeline (UUID PKs):**
- `ResearchRunRecord` — Top-level research run metadata
- `ResearchStageRecord` — Per-stage execution tracking
- `ResearchArtifactRecord` — Artifacts produced by a run
- `SourceDocumentRecord` — Source URLs observed per company
- `MetricObservationRecord` — Individual metric values from sources
- `EvidenceReadinessRecord` — Evidence quality scores
- `ContradictionRecord` — Detected data conflicts
- `ContradictionTransitionRecord` — Contradiction status history

**Infrastructure:**
- `OutboxRecord` — Transactional outbox for event reliability (UUID)
- `TenantRecord` — Multi-tenant API key registry (UUID)

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for the complete schema reference.

## Testing Strategy

| Type | Location | Purpose |
|------|----------|---------|
| Unit | `tests/unit/` | Isolated component tests |
| Integration | `tests/integration/` | Cross-component tests (real DB) |
| Data Quality | `tests/data_quality/` | Data validation tests |
| Performance | `tests/performance/` | Benchmarks and load tests |
| Property | `tests/property/` | Property-based tests (Hypothesis) |
| Agent | `tests/test_agents/` | AI agent behavior tests |

### Test Commands
```bash
# All tests (auto-runs coverage per pyproject.toml)
pytest

# By layer
pytest -m unit
pytest -m integration
pytest -m data_quality
pytest -m agents
pytest -m slow
pytest -m e2e

# Parallel execution
pytest -n auto
```

## Claude Code Configuration

### MCP Servers
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Subagents

| Agent | Purpose | Budget | Tools |
|-------|---------|--------|-------|
| `@build` | Implementation | 500 | write, edit, test |
| `@plan` | Architecture | 300 | read, analyze |
| `@review` | Code quality | 200 | read, analyze |
| `@test` | Test generation | 200 | write, test |
| `@docs` | Documentation | 150 | write, read |

## LLM Providers

### Supported Providers (13 total)
| Priority | Provider | Notes |
|----------|----------|-------|
| 1 | Ollama (local) | Privacy-first, llama3.2, no API key |
| 2 | Groq | Fast inference |
| 3 | Fireworks | Cost-effective |
| 4 | SiliconFlow | Chinese cloud |
| 5 | Alibaba Cloud | |
| 6 | Mistral | European LLM |
| 7 | DeepInfra | Cost-effective inference |
| 8 | Gemini | Google |
| 9 | NVIDIA NIM | Enterprise inference |
| 10 | Cerebras | Fast chips |
| 11 | Kimi (Moonshot) | |
| 12 | Anthropic | Premium reasoning |
| 13 | OpenAI | General purpose |

### Provider Fallback Chain
```
Ollama → Groq → Fireworks → SiliconFlow → Alibaba → Mistral → DeepInfra
  → Gemini → NVIDIA → Cerebras → Kimi → Anthropic → OpenAI → Template Fallback
```

### Health Checking
All LLM providers have proactive health checking:
- Rate limit detection (429)
- Quota exhaustion detection (402)
- Authentication failure detection (401)
- Automatic provider rotation on failure

See: `src/solstein/llm/health_checker.py`

## Security

### Secrets Management
- `.env` files are git-ignored
- Use `pydantic-settings` for config
- Never log API keys
- Multi-tenant: API keys hashed with SHA-256 before storage

### Security Checks
```bash
# Secret scanning
make scan-secrets

# Dependency vulnerabilities
pip-audit

# SBOM generation
make generate-sbom
```

## Git Workflow

### Branch Naming
```
feature/scoring-algorithm-update
fix/api-response-validation
docs/readme-update
refactor/database-models
test/scoring-unit-tests
```

### Commit Messages
```
feat: Add competitive threat level calculation
fix: Handle null revenue values in scoring
docs: Update API endpoint documentation
refactor: Extract scoring logic to service layer
test: Add unit tests for Phoenix classification
```

### Pre-Commit
```bash
# Format and lint
black . && ruff check --fix .

# Type check
mypy .

# Run tests
pytest tests/unit -q
```

## Troubleshooting

### Common Issues

**Database connection fails**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify credentials in .env (use double underscore for nested pydantic-settings)
echo $DATABASE__URL
```

**LLM providers unavailable**
```bash
# Check health
PYTHONPATH=src python -c "
from solstein.llm import get_health_checker
import asyncio
asyncio.run(get_health_checker().check_all_providers())
"

# Verify API keys in .env
```

**Import errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use editable install
pip install -e .
```

**Celery worker not starting**
```bash
# Verify Redis is running
redis-cli ping

# Start worker with explicit app
PYTHONPATH=src celery -A solstein.celery_config worker --loglevel=debug
```

## Context Rules

### For Build Agent
- Always write tests for new features
- Follow existing patterns in codebase
- Use type hints everywhere (especially for files under mypy coverage)
- Handle errors explicitly, never silent catches

### For Plan Agent
- Read existing code before proposing changes
- Consider backward compatibility
- Document trade-offs
- Estimate complexity

### For Review Agent
- Check type safety
- Verify error handling
- Validate test coverage
- Ensure docstrings present

## Performance Guidelines

### Database
- Use async queries for all I/O
- Batch inserts where possible
- Index frequently queried fields
- Use connection pool (pool_size=20, max_overflow=10)

### API
- Paginate large result sets
- Cache expensive computations (Redis)
- Use background tasks for long operations (Celery)

### LLM
- Use cheaper models for simple tasks
- Cache LLM responses when appropriate
- Implement provider fallback for reliability (13-provider chain)

## External Dependencies

### Required
- Python 3.10+
- PostgreSQL 14+
- Redis (cache + Celery task queue)

### Optional
- Ollama (for local LLM inference)

## Code Quality Guidelines for Agents

**CRITICAL: All code must pass automated quality gates.**

### Function Size Limits
- **Maximum:** 100 lines per function
- **Target:** <50 lines per function
- **Action:** If your function exceeds 50 lines, break it down immediately

### Class Size Limits
- **Maximum:** 300 lines per class
- **Maximum:** 15 methods per class
- **Target:** <200 lines per class
- **Action:** Extract classes if exceeding limits

### File Size Limits
- **Maximum:** 500 lines per file
- **Target:** <400 lines per file
- **Action:** Split into modules if exceeding limits

### Parameter Limits
- **Maximum:** 5 parameters per function
- **Action:** Use parameter objects or builders if exceeding

### Nesting Limits
- **Maximum:** 4 levels of indentation
- **Action:** Extract early returns, use guard clauses

### Error Handling
- **NEVER use bare except clauses**
- **ALWAYS catch specific exceptions**
- **NEVER silently catch errors**

```python
# ❌ FORBIDDEN:
try:
    process_data()
except:
    pass

# ✅ REQUIRED:
try:
    process_data()
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise BusinessError("Processing failed") from e
```

### Import Rules
- **NO lazy imports** (imports inside functions)
- **Place all imports at top of file**
- **Use absolute imports** (not relative)

```python
# ❌ FORBIDDEN:
def some_function():
    from . import utils  # Lazy import!
    utils.do_something()

# ✅ REQUIRED:
from solstein import utils  # At top of file

def some_function():
    utils.do_something()
```

### Automated Enforcement
CI/CD will **REJECT** your PR if:
- Any function >100 lines
- Any class >300 lines
- Any file >500 lines
- Any bare except clauses
- Lazy imports detected

### Quality Check Commands

```bash
# Check your code before committing
python scripts/ci/code_smell_detector.py src/your/file.py
python scripts/ci/check_function_sizes.py src/your/file.py
python scripts/ci/check_class_sizes.py src/your/file.py
python scripts/ci/check_file_sizes.py
```

### Code Smell References
- See [EPIC-019](../docs/epics/EPIC-019-AUTOMATED-CODE-QUALITY-GUARDRAILS.md) for full guidelines
- See [COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md](../COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md) for current issues
- All new code must not increase smell count

---

## Version History


## Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.0 | 2026-03-01 | Accurate documentation: 21 modules, 18 DB tables, 13 LLM providers, Celery |
| v2.0 | 2026-02-28 | Claude Code v1.0+ standard, LLM health checking |
| v1.8 | 2026-02-01 | Initial multi-provider support |

---

*This AGENTS.md follows the Claude Code v1.0+ standard for project context.*
