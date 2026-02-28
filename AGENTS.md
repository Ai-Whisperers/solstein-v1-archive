# Solstein - AI-Powered Competitive Intelligence Platform

> **AGENTS.md v2.0** | OpenCode v1.0+ Standard  
> Last Updated: 2026-02-28  
> Auto-generated: Partial (manual enhancements applied)

## Quick Reference

```yaml
project: solstein
language: python
framework: fastapi
architecture: domain-driven
ai_ready: true
mcp_servers: [filesystem, sequential-thinking, memory]
```

## Project Identity

**What is this?**  
AI-powered competitive intelligence platform for PE/VC professionals. Analyzes market data, company financials, competitive positioning, and generates strategic insights.

**Why does it exist?**  
Private equity and venture capital firms need rapid, data-driven competitive analysis. Traditional research is slow and expensive. Solstein automates this with AI.

**Who maintains it?**  
Core team with AI-assisted development via OpenCode.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.11+ |
| **Framework** | FastAPI | Latest |
| **Package Manager** | uv / pip | - |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Data Processing** | Pandas | 2.x |
| **Excel Export** | OpenPyXL | 3.x |
| **Testing** | pytest | 8.x |
| **Linting** | ruff + black + mypy | Latest |
| **CLI** | Click | 8.x |

## Architecture

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
        │                     │                     │
        └─────────────────────┼─────────────────────┘
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

## Directory Structure

```
solstein/
├── src/solstein/
│   ├── api/                 # FastAPI endpoints
│   │   ├── routes/         # API route handlers
│   │   ├── schemas/        # Pydantic models
│   │   └── dependencies/   # FastAPI dependencies
│   ├── domain/             # Domain models
│   │   ├── models/        # Business entities
│   │   └── scoring/       # Scoring algorithms
│   ├── infrastructure/     # External adapters
│   │   ├── database/      # SQLAlchemy models
│   │   ├── cache/         # Redis client
│   │   └── company_repository.py
│   ├── application/        # Application services
│   │   └── services/
│   ├── exporters/          # Export formats
│   │   ├── llm.py         # LLM-powered reports
│   │   ├── excel.py       # Excel generation
│   │   └── markdown.py
│   ├── analytics/          # Analysis tools
│   │   └── filters/
│   ├── llm/               # LLM client with health checking
│   │   ├── health_checker.py
│   │   └── enhanced_client.py
│   └── config.py          # Application settings
├── tests/                  # Test suites
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── dashboard/             # Next.js frontend
```

## Development Commands

### Setup
```bash
# Install dependencies
uv sync
# or
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py
```

### Development
```bash
# Run API server
python -m uvicorn solstein.api.main:app --reload

# Run CLI
python run_research.py

# Run dashboard
cd dashboard && npm run dev
```

### Quality
```bash
# Run tests
pytest -v
pytest --cov=. --cov-report=html

# Type check
mypy . --strict

# Format and lint
black . && ruff check --fix .

# Full check
make check-all
```

### OpenCode Integration
```bash
# Check MCP servers
make mcp-check

# Run smoke tests
./scripts/opencode-mcp-smoke-test.sh

# Doctor check
./scripts/opencode-mcp-doctor.sh
```

## Code Standards

### Formatting
- **Line Length**: 120 characters (Black)
- **Import Order**: isort (stdlib → third-party → local)
- **Type Hints**: Required for all functions
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
```

### Key Models
- `Company` - Core entity with financials
- `FinancialData` - Revenue, growth, employees
- `Signal` - Data source observations
- `Analysis` - Generated insights

## Testing Strategy

| Type | Location | Coverage Target |
|------|----------|-----------------|
| Unit | `tests/unit/` | 80% |
| Integration | `tests/integration/` | 60% |
| E2E | `tests/e2e/` | Critical paths |

### Test Commands
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test
pytest tests/unit/test_scoring.py -v

# Parallel execution
pytest -n auto
```

## OpenCode Configuration

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

### Usage Patterns

```markdown
# Plan Phase (Read-Only)
@plan Analyze the scoring algorithm and propose improvements

# Build Phase (Implementation)
@build Implement the proposed scoring changes with tests

# Review Phase (Quality Check)
@review Check the implementation against our standards
```

## LLM Providers

### Supported Providers
| Provider | Model | Use Case |
|----------|-------|----------|
| Ollama | llama3.2 | Local, sensitive data |
| OpenAI | gpt-4o-mini | General purpose |
| Groq | llama-3.3-70b | Fast inference |
| Fireworks | qwen2-72b | Cost-effective |

### Provider Fallback Chain
```
Ollama (local) → Fireworks → OpenAI → Groq → Template Fallback
```

### Health Checking
All LLM providers now have proactive health checking:
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

# Verify credentials in .env
```

**LLM providers unavailable**
```bash
# Check health
python -c "from solstein.llm import get_health_checker; import asyncio; asyncio.run(get_health_checker().check_all_providers())"

# Verify API keys in .env
```

**Import errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use editable install
pip install -e .
```

## Context Rules

### For Build Agent
- Always write tests for new features
- Follow existing patterns in codebase
- Use type hints everywhere
- Handle errors explicitly

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
- Use async queries for I/O
- Batch inserts where possible
- Index frequently queried fields

### API
- Paginate large result sets
- Cache expensive computations
- Use background tasks for long operations

### LLM
- Use cheaper models for simple tasks
- Cache LLM responses when appropriate
- Implement provider fallback for reliability

## External Dependencies

### Required
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for dashboard)

### Optional
- Redis (for caching)
- Ollama (for local LLM)

## Resources

### Documentation
- API Docs: `/docs` (when running)
- Architecture: `docs/architecture/`
- Data Sources: `docs/data-sources/`

### Monitoring
- Health endpoint: `/health`
- Metrics: `/metrics`
- OpenAPI: `/openapi.json`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.0 | 2026-02-28 | OpenCode v1.0+ standard, LLM health checking |
| v1.9 | 2026-02-15 | Enhanced provider failover |
| v1.8 | 2026-02-01 | Initial multi-provider support |

---

*This AGENTS.md follows the OpenCode v1.0+ standard for project context.*  
*For OpenCode documentation: https://docs.opencode.ai*
