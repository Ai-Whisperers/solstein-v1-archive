# Solstein — Development Guide

> Setup, workflows, and conventions for contributors.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | Required |
| PostgreSQL | 15+ | Required |
| Node.js | 18+ | Required for dashboard |
| uv | Latest | Recommended package manager |
| Redis | 7+ | Optional (in-memory fallback available) |
| Ollama | Latest | Optional (local LLM) |

---

## Setup

### 1. Install Dependencies

```bash
# Recommended: uv (fast)
uv sync

# Alternative: pip
pip install -r requirements.txt

# Development extras
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values. Minimum required:

```bash
# Required
GITHUB_TOKEN=ghp_your_token_here
DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein

# Security (change in production!)
SECURITY__SECRET_KEY=your-strong-secret-key-here

# Optional LLM providers
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
FIREWORKS_API_KEY=fw_...
```

### 3. Setup Database

```bash
python scripts/setup_db.py
```

### 4. Start the API

```bash
# PYTHONPATH=src is required — the package lives under src/
PYTHONPATH=src python -m uvicorn solstein.api.main:app --reload
```

API available at: **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 5. Start the Dashboard (optional)

```bash
cd dashboard && npm install && npm run dev
```

Dashboard available at: **http://localhost:3000**

---

## Development Commands

### Running the API

```bash
# Development (with auto-reload)
PYTHONPATH=src python -m uvicorn solstein.api.main:app --reload

# Production-like
PYTHONPATH=src python -m uvicorn solstein.api.main:app --host 0.0.0.0 --port 8000

# Direct entry point
PYTHONPATH=src python src/solstein/api/main.py
```

### Testing

```bash
# All tests
PYTHONPATH=src pytest tests/

# With coverage
PYTHONPATH=src pytest tests/ --cov=src/solstein --cov-report=html

# Specific layers
PYTHONPATH=src pytest tests/unit/          # Fast, pure logic
PYTHONPATH=src pytest tests/integration/   # API contract tests
PYTHONPATH=src pytest tests/data_quality/  # Golden dataset regressions

# Specific file
PYTHONPATH=src pytest tests/unit/test_scoring.py -v

# Parallel execution
PYTHONPATH=src pytest tests/ -n auto
```

### Code Quality

```bash
# Format
black .

# Lint (with auto-fix)
ruff check --fix .

# Type check
mypy . --strict

# All at once
black . && ruff check --fix . && mypy . --strict
```

### Database

```bash
# Run migrations
PYTHONPATH=src alembic upgrade head

# Create new migration
PYTHONPATH=src alembic revision --autogenerate -m "description"

# Rollback one step
PYTHONPATH=src alembic downgrade -1

# Check current revision
PYTHONPATH=src alembic current
```

### CLI Research Tool

```bash
# Run research pipeline
PYTHONPATH=src python run_research.py

# With specific company
PYTHONPATH=src python run_research.py --company "Acme Corp"
```

---

## Code Standards

### Formatting

- **Line Length**: 120 characters (Black)
- **Import Order**: isort (stdlib → third-party → local)
- **Type Hints**: Required for all functions
- **Docstrings**: Google style

### Naming Conventions

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

# ❌ Silent error swallowing
try:
    result = await operation()
except Exception:
    return None  # NEVER do this

# ❌ Mutable defaults
def func(items=[]):
    ...

# ❌ Print statements (use loguru)
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

# ✅ Type hints everywhere
def analyze_company(company_id: str) -> AnalysisResult:
    ...

# ✅ Structured logging
logger.info("Processing company", company_id=company_id, stage="scoring")
```

---

## Testing Strategy

Solstein follows a **4-layer testing pyramid**:

### Layer 1: Unit Tests (`tests/unit/`)
- Domain models and scoring math
- Use `pytest.approx` for floating-point comparisons
- No database, no network, no LLM calls
- Fast: should complete in seconds

### Layer 2: Integration Tests (`tests/integration/`)
- All API endpoints with deterministic mock repositories
- Tests the full request/response cycle
- Uses `httpx.AsyncClient` with FastAPI test client

### Layer 3: Worker Tests
- Background tasks verified synchronously
- No Redis dependency required

### Layer 4: Data Quality Tests (`tests/data_quality/`)
- Golden Dataset regression to protect classification boundaries
- Ensures scoring changes don't silently break Phoenix/Salt/Lead thresholds

### Test File Conventions

```python
# tests/unit/test_scoring.py
import pytest
from solstein.domain.scoring import calculate_growth_score

def test_phoenix_threshold():
    score = calculate_growth_score(revenue_growth=0.45, margin=0.25)
    assert score >= 7.0

def test_lead_threshold():
    score = calculate_growth_score(revenue_growth=-0.05, margin=0.02)
    assert score <= 4.0
```

---

## LLM Provider Configuration

### Auto Mode (default)

```bash
LLM_PROVIDER=auto  # Tries providers in fallback order
```

Fallback chain: **Ollama → Fireworks → OpenAI → Groq → Template**

### Pinning a Provider

```bash
LLM_PROVIDER=ollama     # Local Ollama
LLM_PROVIDER=openai     # OpenAI gpt-4o-mini
LLM_PROVIDER=groq       # Groq llama-3.3-70b-versatile
LLM_PROVIDER=fireworks  # Fireworks mixtral-8x22b-instruct
LLM_PROVIDER=none       # Disable LLM entirely
```

### Local Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the default model
ollama pull llama3.2:latest

# Verify
ollama list
```

---

## Git Workflow

### Branch Naming

```
feature/scoring-algorithm-update
fix/api-response-validation
docs/readme-update
refactor/database-models
test/scoring-unit-tests
```

### Commit Messages (Conventional Commits)

```
feat: Add competitive threat level calculation
fix: Handle null revenue values in scoring
docs: Update API endpoint documentation
refactor: Extract scoring logic to service layer
test: Add unit tests for Phoenix classification
```

### Pre-Commit Checklist

```bash
# 1. Format
black . && ruff check --fix .

# 2. Type check
mypy . --strict

# 3. Tests
PYTHONPATH=src pytest tests/unit -q

# 4. Commit
git add -A && git commit -m "feat: your message"
```

---

## Troubleshooting

### Import Errors

```bash
# Always set PYTHONPATH when running scripts
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use editable install
pip install -e .
```

### Database Connection Fails

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify credentials in .env
cat .env | grep DATABASE
```

### LLM Providers Unavailable

```bash
# Check health of all providers
PYTHONPATH=src python -c "
from solstein.llm import get_health_checker
import asyncio
asyncio.run(get_health_checker().check_all_providers())
"

# Verify API keys
cat .env | grep -E "(OPENAI|GROQ|FIREWORKS)_API_KEY"
```

### Tests Failing with Import Errors

```bash
# Ensure PYTHONPATH is set
PYTHONPATH=src pytest tests/ -v

# Or install in editable mode
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Related Documentation

- [`docs/architecture.md`](architecture.md) — System architecture overview
- [`docs/api.md`](api.md) — API endpoint reference
- [`docs/guides/operator.md`](guides/operator.md) — Deployment & operations
- [`docs/guides/database.md`](guides/database.md) — Database setup & migrations
