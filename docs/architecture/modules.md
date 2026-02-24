# 🏛️ Solstein Module Architecture Reference

**Deep dive into each module: responsibilities, key classes, extension points, and data flow.**

---

## Module Overview

```
solstein/
├── api/                  ← HTTP request handling (FastAPI)
├── analytics/            ← Business logic (scoring, analysis)
├── core/                 ← Interfaces & configuration
├── data/                 ← Data access layer (repository pattern)
├── domain/               ← Pure business entities
├── exporters/            ← Output formats (Excel, PDF, etc.)
├── extractors/           ← Data extraction (Markdown, etc.)
├── config.py             ← Application settings
├── tasks.py              ← Celery background jobs
├── worker.py             ← Celery app initialization
└── cli.py                ← Command-line interface
```

Each module is **independently testable** and follows **clean architecture principles**: low coupling, high cohesion, framework-agnostic domain logic.

---

## 1. `domain/` — Pure Business Entities

**Responsibility:** Define core business concepts with NO framework dependencies.

**Location:** `src/solstein/domain/models.py`

### Key Classes

#### `Company` (Dataclass)
Represents a single company profile with all associated data.

```python
@dataclass
class Company:
    # Identity
    id: str                              # Unique company ID
    name: str                            # Human-readable name
    
    # Classification & Positioning
    tier: CompanyTier                    # Tier 1-4 by size
    industry: str                        # Industry category
    threat_level: ThreatLevel            # Low/Medium/High/Critical
    
    # Technology
    ai_maturity: AIMaturity              # None/Low/Moderate/Strong/VeryStrong
    saas_maturity: int                   # 1-10 scale
    tech_stack: list[str]                # Technologies used
    
    # Financial Data
    financials: FinancialMetric          # Revenue, growth, profitability, etc.
    
    # Scoring Results
    growth_score: float | None           # 0-10
    financial_health_score: float | None # 0-10
    competitive_position_score: float | None # 0-10
    composite_score: float | None        # Weighted average
    classification: str                  # Phoenix/Salt/Lead
    scoring_breakdown: dict[str, Any]    # Detailed scoring explanation
```

**Extension points:**
- Add new fields for custom scoring dimensions
- Update enums (AIMaturity, ThreatLevel) for new categories
- Add relationship fields (parent_company, subsidiaries, acquisitions)

#### `FinancialMetric` (Dataclass)
Time-series financial data for a company.

```python
@dataclass
class FinancialMetric:
    # Revenue & Growth
    revenue: float | None                # In millions EUR
    revenue_confidence: ConfidenceLevel   # Confirmed/Estimated/Unknown
    growth_rate: float | None            # Year-over-year %
    
    # Profitability
    profit_margin: float | None          # Percentage
    margin_confidence: ConfidenceLevel
    
    # Capital
    employees: int | None                # Headcount
    employees_confidence: ConfidenceLevel
    funding_raised: float | None         # In millions
    funding_confidence: ConfidenceLevel
    valuation: float | None              # In millions
```

**Why separate from Company?**
- Financial data is time-series (multiple records per company)
- Can be optional (many companies don't disclose)
- Separate entity allows better testing and evolution

#### Enums: AIMaturity, ThreatLevel, CompanyTier, ConfidenceLevel

```python
class AIMaturity(StrEnum):
    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"

class ThreatLevel(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
```

**Rationale for enums:**
- Type-safe (can't use invalid values)
- Version-controllable
- Database-friendly (stored as strings)
- Exhaustive case analysis in code

### When to Modify Domain Models

✅ **Good reasons:**
- New business requirement (new field needed)
- Better modeling (split entity, new relationship)
- Data quality improvement (add confidence tracking)

❌ **Bad reasons:**
- API schema needs it (move to schemas.py)
- Database schema changed (use repository pattern)
- Framework integration (keep frameworks out)

---

## 2. `core/` — Interfaces & Configuration

**Responsibility:** Define abstract interfaces and externalize configuration.

### `core/repositories.py` — Repository Pattern Interface

Defines how data is accessed. Implementations can swap without changing business logic.

```python
# Abstract interface
class CompanyRepository(ABC):
    """Abstract interface for company data access."""
    
    @abstractmethod
    def find_by_id(self, company_id: str) -> Company | None:
        """Retrieve single company by ID."""
        pass
    
    @abstractmethod
    def find_all(self, filters: CompanyFilter = None) -> list[Company]:
        """Retrieve all companies, optionally filtered."""
        pass
    
    @abstractmethod
    def save(self, company: Company) -> str:
        """Insert or update company. Returns company ID."""
        pass
    
    @abstractmethod
    def delete(self, company_id: str) -> bool:
        """Delete company. Returns success."""
        pass

# Concrete implementations exist in data/repositories.py
# - JsonFileRepository
# - SupabaseRepository (PostgreSQL via Supabase)
# - Future: PostgresRepository, MongoRepository, etc.
```

**Filter DTO:**
```python
@dataclass
class CompanyFilter:
    """Query filters for companies."""
    industry: str | None = None
    market: str | None = None
    tier: CompanyTier | None = None
    min_revenue: float | None = None  # Millions
    classification: str | None = None  # Phoenix/Salt/Lead
    skip: int = 0
    limit: int = 100
```

**Why repository pattern?**
- Swap implementations (JSON → PostgreSQL) without changing business logic
- Mock easily in tests (inject fake repo)
- Isolate data access concerns
- Support multiple simultaneous repositories (e.g., cache + primary)

### `core/scoring_config.py` — Tunable Scoring Configuration

```python
# Configurable scoring thresholds and weights

class GrowthScoringConfig(BaseModel):
    base_score: float = 5.0
    revenue_growth_divisor: float = 20.0
    revenue_growth_cap: float = 4.0
    efficiency_high_threshold: float = 500_000.0
    # ... many more tunable parameters

class FinancialHealthConfig(BaseModel):
    base_score: float = 5.0
    revenue_large_threshold: float = 100.0  # Millions
    # ... many more

class CompetitivePositionConfig(BaseModel):
    base_score: float = 5.0
    ai_adoption_bonus: float = 2.0
    # ... many more

class ScoringSettings(BaseSettings):
    """Main scoring config loaded from environment."""
    growth: GrowthScoringConfig = Field(default_factory=GrowthScoringConfig)
    financial_health: FinancialHealthConfig = Field(...)
    competitive_position: CompetitivePositionConfig = Field(...)
```

**Extension pattern:**
To add a new scoring dimension:
1. Create `NewDimensionConfig` class
2. Add to `ScoringSettings`
3. Implement calculation in `GrowthScorer`
4. Override thresholds via environment variables

---

## 3. `domain/` & `data/` — Model Layers

### Domain Models vs. Data Models

**Domain Models** (`domain/models.py`):
- Pure Python dataclasses
- NO framework dependencies
- Represent business concepts
- Used in business logic, tests, APIs

**Data Models** (`data/models.py`):
- Pydantic models for data validation
- Repository-specific shapes
- Used internally by repository implementations
- Can differ from domain models (e.g., add database metadata)

```python
# Domain model (pure business concept)
@dataclass
class Company:
    id: str
    name: str
    growth_score: float | None = None

# Data model (Pydantic, for JSON validation)
class CompanyData(BaseModel):
    id: str
    name: str
    growth_score: float | None = None
    created_at: datetime  # DB metadata
    updated_at: datetime  # DB metadata

# API schema (for HTTP responses)
class CompanySchema(BaseModel):
    id: str
    name: str
    growth_score: float | None = None
    # Different from domain model (only expose what clients need)
```

**Why separate?**
- Domain model is framework-agnostic (testable, portable)
- Data model encodes repository-specific concerns
- API schema controls what's exposed to clients
- Clear separation of concerns

---

## 4. `analytics/` — Business Logic & Scoring

**Responsibility:** Calculate scores, perform market analysis, generate insights.

### `analytics/scoring.py` — Core Scoring Engine

#### `GrowthScorer` Class

Main orchestrator for all scoring calculations.

```python
class GrowthScorer:
    """Calculate growth, financial health, and competitive position scores."""
    
    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()
    
    def calculate_scores(self, company: Company) -> Company:
        """
        Main entry point.
        Calculates all 3 scores, applies classification.
        MUTATES INPUT (known issue, see ADR-008).
        """
        # Calculate each dimension
        growth_score, growth_expl = self._calculate_growth_score(...)
        financial_score, fin_expl = self._calculate_financial_health_score(...)
        competitive_score, comp_expl = self._calculate_competitive_position_score(...)
        
        # Apply results to company
        company.growth_score = growth_score
        company.financial_health_score = financial_score
        company.competitive_position_score = competitive_score
        
        # Composite score (weighted average)
        company.composite_score = (
            growth_score * 0.4 +
            financial_score * 0.3 +
            competitive_score * 0.3
        )
        
        # Classification
        company.classification = classify_company(company.growth_score)
        
        # Scoring breakdown (for explainability)
        company.scoring_breakdown = {
            "growth": growth_expl,
            "financial": fin_expl,
            "competitive": comp_expl,
        }
        
        return company
```

#### Private Methods (Scoring Dimensions)

```python
def _calculate_growth_score(self, financials: FinancialMetric) -> tuple[float, ScoringExplanation]:
    """
    Measures revenue growth trajectory.
    
    Components:
    - Base score: 5.0
    - Revenue growth: min(growth_rate / 20, 4.0)
    - Profit margin: +bonuses for profitability
    - Employee efficiency: revenue per employee
    
    Range: 0-10
    """
    cfg = self.config.growth
    score = cfg.base_score
    explanation = ScoringExplanation(base_score=score)
    
    # Growth factor
    if financials.growth_rate:
        growth_factor = min(
            financials.growth_rate / cfg.revenue_growth_divisor,
            cfg.revenue_growth_cap
        )
        score += growth_factor
        explanation.components.append(ScoreComponent(
            name="Revenue Growth",
            value=growth_factor,
            formula=f"min({growth_rate}% / 20, 4.0)",
            reasoning=f"Growth rate of {growth_rate}% identified"
        ))
    
    # ... more scoring logic
    
    return min(score, 10.0), explanation
```

**Similar methods:**
- `_calculate_financial_health_score()` — Revenue scale, profitability, funding cushion
- `_calculate_competitive_position_score()` — AI maturity, SaaS adoption, tech depth

### `analytics/simulation.py` — What-If Analysis

```python
class CompanySimulation:
    """Simulate scoring changes for what-if scenarios."""
    
    def simulate_growth(self, company: Company, new_growth_rate: float) -> Company:
        """What if growth rate changed to X%?"""
        company_copy = deepcopy(company)
        company_copy.financials.growth_rate = new_growth_rate
        return GrowthScorer().calculate_scores(company_copy)
    
    def simulate_margin_improvement(self, company: Company, new_margin: float) -> Company:
        """What if profit margin improved to X%?"""
        # ... similar pattern
```

**Use case:** Show clients "if you improve profitability by 5%, your score would be..."

### `analytics/workflows.py` — Temporal Workflow Orchestration

Integrates with Temporal for long-running processes.

```python
class AnalysisWorkflow:
    """Long-running market analysis (uses Temporal for resilience)."""
    
    @workflow.run
    async def run_market_analysis(self, market: str) -> MarketAnalysis:
        """
        1. Load all companies in market
        2. Score each company
        3. Generate competitive overlap analysis
        4. Export to Excel (may timeout, so background task)
        """
        # Step 1
        companies = await workflow.execute_activity(
            load_companies_by_market,
            market
        )
        
        # Step 2 (with retry policy)
        scored = await workflow.execute_activity(
            batch_score_companies,
            companies,
            retry_policy=RetryPolicy(max_attempts=3)
        )
        
        # Step 3
        overlaps = await workflow.execute_activity(
            calculate_overlaps,
            scored
        )
        
        # Step 4 (enqueue Excel export)
        export_task = await workflow.execute_activity(
            enqueue_excel_export,
            scored
        )
        
        return MarketAnalysis(
            market=market,
            companies=scored,
            overlaps=overlaps,
            export_task_id=export_task
        )
```

---

## 5. `api/` — HTTP Request Handling

**Responsibility:** Transform HTTP requests into domain operations, return responses.

### `api/main.py` — FastAPI Application Entry Point

```python
app = FastAPI(
    title="SolStein Competitive Intelligence API",
    version="1.0.0",
)

# CORS, middleware, exception handlers

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Lightweight health check."""
    return {"status": "healthy", "version": "1.0.0"}
```

**Lifespan management:**
- Startup: initialize repositories, warm up caches
- Shutdown: close connections, save state

### `api/dependencies.py` — Dependency Injection

```python
# Injected into all routes, mockable in tests

def get_repository() -> CompanyRepository:
    """Provide repository (can be overridden in tests)."""
    return SupabaseRepository()  # or JsonFileRepository, etc.

def get_current_user(token: str = Header(...)) -> User:
    """Extract user from JWT token (permissive in demo phase)."""
    # See ADR-007: Permissive Authentication
    # Real auth to be implemented before production
    return decode_jwt(token) or User(sub="anonymous", role="viewer")
```

**Why dependency injection?**
- Mock repositories in tests (inject fake repo)
- Swap implementations globally (change one place, affects all routes)
- Testable without database

### `api/routers/` — Endpoint Definitions

Each router handles a domain concern:

#### `companies.py` — CRUD Operations
```python
@router.get("/companies", tags=["Companies"])
async def list_companies(
    filters: CompanyFilter = Body(default=CompanyFilter()),
    repo: CompanyRepository = Depends(get_repository),
) -> list[CompanySchema]:
    """List all companies with optional filtering."""
    companies = repo.find_all(filters)
    return [CompanySchema.from_orm(c) for c in companies]

@router.post("/companies", tags=["Companies"], status_code=201)
async def create_company(
    company_data: CreateCompanyRequest,
    repo: CompanyRepository = Depends(get_repository),
) -> CompanySchema:
    """Create new company."""
    company = company_data.to_domain()
    company_id = repo.save(company)
    return CompanySchema.from_orm(repo.find_by_id(company_id))
```

#### `scoring.py` — Score Calculation
```python
@router.post("/scoring/company/{company_id}/score")
async def score_company(
    company_id: str,
    repo: CompanyRepository = Depends(get_repository),
) -> CompanySchema:
    """Calculate scores for a company."""
    company = repo.find_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404)
    
    scorer = GrowthScorer()
    scored = scorer.calculate_scores(company)
    repo.save(scored)
    
    return CompanySchema.from_orm(scored)
```

#### `market.py` — Market Analysis
```python
@router.get("/market/analysis")
async def market_analysis(
    market: str,
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Analyze entire market."""
    companies = repo.find_all(CompanyFilter(market=market))
    
    analyzer = MarketAnalyzer()
    analysis = analyzer.analyze(companies)
    
    return analysis.to_dict()
```

### `api/schemas.py` — Request/Response Models

```python
# Request schemas
class CreateCompanyRequest(BaseModel):
    name: str
    industry: str
    ai_maturity: str
    # ...

# Response schemas
class CompanySchema(BaseModel):
    id: str
    name: str
    growth_score: float | None
    classification: str
    # ... other fields
    
    class Config:
        from_attributes = True

class ScoringBreakdownSchema(BaseModel):
    growth: ScoringExplanationSchema
    financial_health: ScoringExplanationSchema
    competitive_position: ScoringExplanationSchema
```

### `api/exceptions.py` — Error Handling

```python
class CompanyNotFoundError(Exception):
    """Raised when company doesn't exist."""
    pass

@app.exception_handler(CompanyNotFoundError)
async def handle_not_found(request: Request, exc: CompanyNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )
```

---

## 6. `data/` — Data Access Layer

**Responsibility:** Load/persist domain models, repository implementations.

### `data/repositories.py` — Concrete Implementations

#### `JsonFileRepository`
```python
class JsonFileRepository(CompanyRepository):
    """Load companies from JSON files in data/input/."""
    
    def __init__(self):
        self.data_dir = Settings().data.data_dir
    
    def find_by_id(self, company_id: str) -> Company | None:
        """Load single company JSON file."""
        file = self.data_dir / f"{company_id}.json"
        if not file.exists():
            return None
        
        data = json.loads(file.read_text())
        return Company(**data)  # Deserialize to domain model
    
    def find_all(self, filters: CompanyFilter = None) -> list[Company]:
        """Load all JSONs, apply filters in-memory."""
        companies = []
        for json_file in self.data_dir.glob("*.json"):
            data = json.loads(json_file.read_text())
            companies.append(Company(**data))
        
        # Apply filters
        if filters:
            if filters.industry:
                companies = [c for c in companies if c.industry == filters.industry]
            # ... more filters
        
        return companies[filters.skip : filters.skip + filters.limit]
```

#### `SupabaseRepository`
```python
class SupabaseRepository(CompanyRepository):
    """Persist to PostgreSQL via Supabase."""
    
    def __init__(self):
        self.engine = create_engine(Settings().database.url)
    
    def find_by_id(self, company_id: str) -> Company | None:
        """Query PostgreSQL, convert to domain model."""
        with Session(self.engine) as session:
            row = session.query(CompanyTable).filter_by(id=company_id).first()
            if not row:
                return None
            return row.to_domain()  # Convert DB row to Company
    
    def save(self, company: Company) -> str:
        """Insert or update in PostgreSQL."""
        with Session(self.engine) as session:
            row = CompanyTable.from_domain(company)
            session.merge(row)
            session.commit()
            return company.id
```

**Key difference from JsonFileRepository:**
- Queries vs. file I/O
- Database transactions
- Supports updates efficiently
- Indexed queries

### `data/loaders.py` — Data Ingestion

```python
class CompetitorDataLoader:
    """Load data from multiple sources."""
    
    def load_companies(self) -> list[Company]:
        """Load from JSON, enrich from Crunchbase, etc."""
        # 1. Load base data from JSON
        companies = []
        for file in (Settings().data.data_dir / "companies").glob("*.json"):
            companies.append(json.loads(file.read_text()))
        
        # 2. Enrich with Crunchbase (if API key available)
        if os.getenv("CRUNCHBASE_API_KEY"):
            cb_loader = CrunchbaseLoader()
            for i, company in enumerate(companies):
                enriched = cb_loader.fetch_company(company.name)
                if enriched:
                    companies[i] = self._merge(company, enriched)
        
        return companies
```

---

## 7. `exporters/` — Output Formats

**Responsibility:** Generate reports in different formats.

### `exporters/excel_exporter.py`

```python
class ExcelExporter:
    """Generate Excel dashboard reports."""
    
    def export(self, companies: list[Company], output_path: Path = None) -> Path:
        """Create Excel file with styled dashboard."""
        workbook = Workbook()
        
        # Summary sheet
        ws = workbook.active
        ws.title = "Summary"
        
        # Headers
        ws.append(["Company", "Industry", "Growth Score", "Classification"])
        
        # Data rows
        for company in companies:
            ws.append([
                company.name,
                company.industry,
                company.growth_score or "N/A",
                company.classification or "Unknown",
            ])
        
        # Styling
        self._apply_styles(ws)
        
        # Charts
        self._add_charts(workbook, companies)
        
        # Save
        workbook.save(output_path)
        return output_path
    
    def _apply_styles(self, ws):
        """Apply professional styling."""
        # Header formatting, colors, fonts, etc.
        # Uses openpyxl styling API
        ...
    
    def _add_charts(self, workbook, companies):
        """Add data visualizations."""
        chart = BarChart()
        # Configure and add
        ...
```

**Extension pattern:**
To add PDF export:
```python
class PDFExporter:
    def export(self, companies: list[Company]) -> Path:
        # Use reportlab
        ...
```

Then register in API:
```python
@router.post("/export/pdf")
async def export_pdf(companies: list[CompanySchema]) -> dict:
    exporter = PDFExporter()
    path = exporter.export([c.to_domain() for c in companies])
    return {"file_path": str(path)}
```

---

## 8. `tasks.py` & `worker.py` — Celery Background Jobs

**Responsibility:** Offload long-running operations.

### `tasks.py`

```python
@shared_task(bind=True, time_limit=600)  # 10 min timeout
def batch_score_companies(task, market: str) -> dict[str, Any]:
    """Score all companies in a market (background job)."""
    try:
        # 1. Load companies
        repo = SupabaseRepository()
        companies = repo.find_all(CompanyFilter(market=market))
        
        # 2. Score each
        scorer = GrowthScorer()
        for i, company in enumerate(companies):
            scored = scorer.calculate_scores(company)
            repo.save(scored)
            
            # Update task progress
            task.update_state(
                state='PROGRESS',
                meta={'current': i, 'total': len(companies)}
            )
        
        # 3. Export
        exporter = ExcelExporter()
        output_file = exporter.export(companies)
        
        return {
            "status": "completed",
            "companies_scored": len(companies),
            "file_path": str(output_file),
        }
    
    except Exception as exc:
        logger.error(f"Batch scoring failed: {exc}")
        raise
```

### `worker.py`

```python
from celery import Celery
from solstein.config import Settings

settings = Settings()

app = Celery(
    'solstein',
    broker=settings.redis.url,
    backend=settings.redis.url,
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
)
```

---

## 9. `config.py` — Application Configuration

**Responsibility:** Load and validate all settings from environment.

```python
class DatabaseConfig(BaseModel):
    """Database connection settings."""
    url: str = "postgresql://..."
    pool_size: int = 20
    echo: bool = False

class RedisConfig(BaseModel):
    """Redis connection (Celery broker)."""
    url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

class APIConfig(BaseModel):
    """API server settings."""
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

class Settings(BaseSettings):
    """Main application settings (loaded from .env)."""
    environment: str = "development"
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    scoring: ScoringSettings = Field(default_factory=ScoringSettings)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"  # SOLSTEIN_DATABASE__URL maps to database.url
```

**Access settings:**
```python
settings = Settings()  # Loads from environment
print(settings.database.url)  # postgresql://...
print(settings.api.port)  # 8000
```

---

## 10. `cli.py` — Command-Line Interface

**Responsibility:** Provide CLI commands for operators and batch operations.

```python
@click.group()
def cli():
    """SolStein command-line interface."""
    pass

@cli.command()
@click.argument("market")
def score_market(market: str):
    """Score all companies in a market."""
    repo = SupabaseRepository()
    companies = repo.find_all(CompanyFilter(market=market))
    
    scorer = GrowthScorer()
    for company in companies:
        scored = scorer.calculate_scores(company)
        repo.save(scored)
        click.echo(f"✓ {company.name}: {scored.classification}")

@cli.command()
@click.argument("input_file", type=click.File("r"))
@click.argument("output_file", type=click.Path())
def export_excel(input_file, output_file):
    """Export companies to Excel."""
    companies = json.load(input_file)
    exporter = ExcelExporter()
    exporter.export(companies, Path(output_file))
    click.echo(f"✓ Exported to {output_file}")

if __name__ == "__main__":
    cli()
```

**Usage:**
```bash
python -m solstein.cli score-market "European Energy"
python -m solstein.cli export-excel input.json output.xlsx
```

---

## Module Dependencies Graph

```
                         [API Routes]
                              │
                    [Dependency Injection]
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
       [Repository]       [GrowthScorer]   [Exporters]
            │                 │                 │
    ┌───────┴───────┐         │          [openpyxl, reportlab]
    │               │         │
[JsonFile]    [Supabase]   [domain/models]
    │               │         │
 [JSON files] [PostgreSQL]    │
              (via Supabase)   │
                              │
                    [ScoringSettings]
                      [config.py]
                      [.env file]
```

**Dependency direction:** All dependencies point INWARD (toward domain models). Domain models have NO dependencies.

---

## How to Add a New Module

1. **Define interface in `core/`** (if swappable)
2. **Implement business logic** (mostly in `analytics/`)
3. **Create API routes** (in `api/routers/new_feature.py`)
4. **Add repository methods** (if needs data access)
5. **Export in `__init__.py`** (make importable)
6. **Write tests** (unit + integration)
7. **Document in ADR** (explain design decisions)

---

## Testing Each Module

| Module | Test Location | What to Test |
|--------|---------------|-------------|
| `domain/` | `tests/unit/test_models.py` | Model instantiation, validation |
| `analytics/` | `tests/unit/test_scoring.py` | Calculation logic, boundaries |
| `api/` | `tests/test_fastapi.py` | Request/response contracts |
| `data/` | `tests/unit/test_repositories.py` | Repository interfaces |
| `exporters/` | `tests/integration/test_exporters.py` | File generation |
| `tasks.py` | `tests/integration/test_worker.py` | Task execution |

---

## References

- [Architecture Decisions](decisions.md) — Why design choices were made
- [Developer Guide → Code Structure](../guides/developer.md) — Overview
- [Extending Solstein](../guides/extending-solstein.md) — How to add features
- [Repository Structure](../STRUCTURE.md) — File layout

---

*Last Updated: February 20, 2026*
*Maintained by: Architecture Team*

