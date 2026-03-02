# 📖 Solstein Glossary

**Key terms, definitions, and concepts used across Solstein documentation and code.**

---

## Business & Market Terms

### **Attractiveness Board**
The core output of Solstein — a ranked, clickable, fully-explainable list of companies classified by growth potential. Every score exposes its signal chain with no black boxes.

### **Classification** / **Classification System**
The three-tier system that categorizes companies:
- 🔥 **Phoenix** (≥ 7.0) — High-growth companies, AI-native or rapidly adopting
- 🧂 **Salt** (4.0–7.0) — Stable players, signal-rich
- ⚖️ **Lead** (≤ 4.0) — Legacy-heavy but transformation opportunities

### **Competitive Position Score**
One of three scoring dimensions. Measures how well-positioned a company is in its market based on:
- AI maturity
- SaaS adoption level
- Technology stack depth
- Market positioning

**Range:** 0–10 (higher = better positioned)

### **Market Intelligence**
The collective analysis of companies within a defined market segment (e.g., "European Energy Software," "US SaaS Infrastructure").

### **PE / VC**
- **PE** = Private Equity
- **VC** = Venture Capital
- Primary customers for Solstein's competitive intelligence

### **Portfolio Company**
A company owned/invested in by a PE firm. Solstein analyzes entire portfolios to identify overlaps and competitive threats.

### **Sunstone**
The metaphor at Solstein's heart. In Viking navigation, the solarsteinn revealed the sun behind clouds. Solstein reveals the competitive landscape through market fog.

---

## Scoring & Analytics Terms

### **Financial Health Score**
One of three scoring dimensions. Measures company stability and financial cushion:
- Revenue scale and growth trajectory
- Profitability and margins
- Funding/capital position
- Operational efficiency

**Range:** 0–10 (higher = healthier)

### **Growth Score**
One of three scoring dimensions. Measures revenue trajectory and momentum:
- Year-over-year revenue growth rate
- Revenue acceleration/deceleration
- Market expansion signals

**Range:** 0–10 (higher = faster growth)

### **GrowthScorer**
The main scoring engine (`src/solstein/analytics/scoring.py`). Calculates all three scores from company financial data and applies classification logic.

### **Market Analysis**
Aggregate view of all companies in a market, including:
- Score distributions
- Classification breakdowns
- Competitive overlaps
- Market trends

### **Scoring Dimension**
One of the three independent scoring axes:
1. Growth Score
2. Financial Health Score
3. Competitive Position Score

Each dimension is 0–10. Combined they inform classification.

### **Scoring Threshold**
Boundary value that determines classification:
- Phoenix threshold: growth_score ≥ 7.0
- Lead threshold: growth_score ≤ 4.0
- Salt: everything in between

---

## Technical Architecture Terms

### **API Router**
FastAPI module handling a specific endpoint domain. Solstein has routers for:
- `/companies` — Company CRUD
- `/scoring` — Score calculation and stats
- `/market` — Market analysis and search
- `/export` — Report generation

**Location:** `src/solstein/api/routers/`

### **Celery**
Python task queue library used for background jobs:
- Batch scoring (multiple companies)
- Excel report generation
- Long-running analysis tasks

Requires Redis as the message broker.

### **Composite Score**
(Future feature) A single 0–10 score calculated from the three dimension scores using weighted formula.

### **Domain Model**
Pure business entity, independent of frameworks. In Solstein:
- `Company` — A single company profile
- `FinancialMetric` — Time-series financial data point

**Location:** `src/solstein/domain/models.py`

### **Dependency Injection**
Design pattern used throughout FastAPI code. FastAPI's `Depends()` automatically provides:
- Repository implementations (swappable for testing)
- Current user/authentication
- Configuration settings

**Location:** `src/solstein/api/dependencies.py`

### **Entity**
A distinct business concept with identity. In Solstein:
- `Company` — has `id`, `name`, `scores`
- `FinancialMetric` — time-series data point

Unlike value objects (like `Score`), entities persist and have unique IDs.

### **Export / Exporter**
Process and code that generates reports in other formats:
- **ExcelExporter** — Generates dashboard-style Excel reports
- (Future) PDFExporter, JSONExporter

**Location:** `src/solstein/exporters/`

### **FastAPI**
Python async web framework powering Solstein's API. Key features:
- Automatic OpenAPI documentation
- Dependency injection system
- Pydantic integration for validation
- Native async/await

### **Health Check**
Endpoint `/health` that verifies API availability:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-02-20T..."
}
```

> Note: Only checks API process, not database/Redis connectivity.

### **Lifespan**
FastAPI application lifecycle hooks:
- `@app.on_event("startup")` — runs once when API starts
- `@app.on_event("shutdown")` — runs once when API stops

Used for initializing connections, warming up caches, etc.

### **ORM / SQLAlchemy**
Object-Relational Mapper for database queries. Solstein uses SQLAlchemy 2.0 for:
- Type-safe database access
- Connection pooling
- Query building

### **Pydantic**
Python library for data validation and configuration:
- Request/response schema validation
- Type hints at runtime
- Environment variable parsing

### **Redis**
In-memory key-value store used for:
- Celery task broker
- Response caching (future)
- Session storage (future)

**Port:** 6379 (default)

### **Repository Pattern**
Abstraction for data access. All database queries go through `CompanyRepository`:
- `JsonFileRepository` — reads JSON files
- `SupabaseRepository` — reads PostgreSQL
- (Future) `PostgresRepository`, `MongoRepository`

**Location:** `src/solstein/core/repositories.py`

### **Schema** / **Pydantic Schema**
Request/response shape definition. In Solstein:
- `CompanySchema` — API response for single company
- `CreateCompanyRequest` — API request body

**Location:** `src/solstein/api/schemas.py`

### **Supabase**
Hosted PostgreSQL database with auth and real-time APIs. Solstein uses it for:
- Production data store
- Cloud deployments
- User authentication (future)

### **Temporal**
(Future) Workflow orchestration platform for complex multi-step processes:
- Batch scoring with retries
- Data pipelines
- Report generation workflows

### **Value Object**
Immutable object with no identity, defined by its values. In Solstein:
- `Score` (a float 0–10)
- `Classification` (enum: Phoenix/Salt/Lead)

Unlike entities, value objects are not persisted separately.

---

## Testing Terms

### **Fixture**
Reusable test data or setup. Defined in `tests/conftest.py`:
- `mock_company` — deterministic test company
- `mock_repo` — mocked repository
- `client` — FastAPI test client

### **Golden Dataset**
Reference dataset protecting classification boundaries. Stored in test data, used to verify scoring doesn't drift over time.

**Location:** `tests/data_quality/`

### **Mock / Mocking**
Replacing a real component with a fake for testing. Example:
```python
# Replace real repository with mock
@patch('solstein.data.repositories.SupabaseRepository')
def test_endpoint(mock_repo):
    mock_repo.find_all.return_value = [mock_company]
    # ...
```

### **Parametrized Test**
Test that runs multiple times with different inputs:
```python
@pytest.mark.parametrize("score,expected", [
    (8.5, "Phoenix"),
    (5.0, "Salt"),
    (3.2, "Lead"),
])
def test_classification(score, expected):
    # ...
```

### **Regression Test**
Test that verifies behavior doesn't regress after code changes. In Solstein:
- Golden dataset tests
- API contract tests
- Scoring precision tests (using `pytest.approx`)

### **Test Pyramid**
6-layer testing strategy:
1. **Unit** — Pure logic, no I/O
2. **Integration** — API contracts with mocked repos
3. **Worker** — Celery tasks
4. **Data Quality** — Golden dataset regressions

---

## Deployment & Operations Terms

### **Blue-Green Deployment**
(Future) Strategy for zero-downtime upgrades:
- Blue = current production
- Green = new production
- Switch traffic when ready

### **CI/CD**
- **CI** = Continuous Integration (automated tests on every commit)
- **CD** = Continuous Deployment (automated releases)

Solstein uses GitHub Actions for both.

### **Container**
Isolated environment (Docker) bundling code + dependencies + runtime.

### **Environment**
Deployment context:
- **Development** — Local machine or dev server
- **Staging** — Pre-production, production-like config
- **Production** — Live, real data

### **Health Endpoint**
See **Health Check** above.

### **Horizontal Scaling**
Running multiple API server instances behind a load balancer. Each instance is stateless.

### **Load Balancer**
Distributes incoming requests across multiple server instances for scaling.

### **Logging Level**
Verbosity of application logs:
- `DEBUG` — Detailed diagnostic info
- `INFO` — General operational info
- `WARNING` — Warning conditions
- `ERROR` — Error conditions
- `CRITICAL` — Critical failures

### **Monitoring**
(Future) Observability stack:
- **Prometheus** — Metrics collection
- **Grafana** — Metrics visualization
- **Alerting** — Rules that trigger notifications

### **Observability**
(Future) Ability to understand system behavior through:
- Logs
- Metrics
- Traces
- Health checks

### **Vertical Scaling**
Increasing resources (CPU, RAM) of a single server.

---

## Process & Governance Terms

### **ADR / Architecture Decision Record**
Document explaining a technical decision:
- Problem statement
- Decision rationale
- Consequences and trade-offs

**Location:** `docs/architecture/decisions.md`

### **Branching Strategy**
Git branching convention:
- `main` — stable, deployable
- `feature/FD-XXX` — new features
- `fix/FD-XXX` — bug fixes
- `docs/FD-XXX` — documentation only

### **Code Review**
Peer review process before merging to `main`. Checks:
- Code quality
- Test coverage
- Documentation updates
- Breaking changes

### **Conventional Commit**
Commit message format:
```
<type>(<scope>): <subject>

feat(scoring): add competitive position dimension
fix(api): resolve CORS header bug
docs(readme): update quick start
test(golden-dataset): add regression for Phoenix threshold
```

### **CHANGELOG**
Record of version history and notable changes. Updated per-release.

**Location:** `[CHANGELOG.md](../CHANGELOG.md)`

### **Pull Request / PR**
GitHub feature for code review and merge. Includes:
- Diff of changes
- CI/CD test results
- Review comments
- Merge status

### **Release**
Tagged version of the codebase (e.g., `v0.2.0`). Includes:
- Git tag
- CHANGELOG entry
- Deployment to production

### **Semantic Versioning**
Version numbering scheme: `MAJOR.MINOR.PATCH`
- **MAJOR** — breaking changes
- **MINOR** — new features (backward-compatible)
- **PATCH** — bug fixes

Example: `0.1.0` (first pre-release), `1.0.0` (first stable)

---

## Data Terms

### **Feature**
In machine learning, a measured property used for analysis. In Solstein:
- Revenue growth rate
- Profit margin
- AI maturity score
- Employee count

### **Financial Metric**
Time-series financial data for a company:
- Revenue (annual)
- Growth rate (year-over-year %)
- Profit margin
- Employee count

### **Financials**
Aggregate financial data for a company, usually from a single year.

### **Seed Data**
Initial/test data loaded into the system. Solstein seed data:
- 29 companies from European energy market
- Financial data for analysis
- Includes known classifications (for validation)

---

## Common Acronyms

| Acronym | Meaning |
|---------|---------|
| **ADR** | Architecture Decision Record |
| **API** | Application Programming Interface |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **CRUD** | Create, Read, Update, Delete |
| **DTO** | Data Transfer Object |
| **JWT** | JSON Web Token |
| **ORM** | Object-Relational Mapper |
| **PE** | Private Equity |
| **PR** | Pull Request |
| **RPS** | Requests Per Second |
| **SaaS** | Software as a Service |
| **SQL** | Structured Query Language |
| **VC** | Venture Capital |

---

## Related Documentation

- **Business Context:** [Executive Brief](PITCH/executive-brief.md), [The Origin](LORE/origin.md)
- **Architecture:** [ADRs](architecture/decisions.md), [Repository Structure](STRUCTURE.md)
- **Development:** [Developer Guide](guides/developer.md), [Code Conventions](guides/code-conventions.md)
- **Quick Lookup:** [Quick Reference](QUICK-REFERENCE.md)

---

*Last Updated: February 20, 2026*
*Suggest additions or corrections via PR*

