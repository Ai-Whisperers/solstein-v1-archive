# 📐 Solstein Code Conventions

**Formalized coding standards for Solstein development. Ensures consistency, maintainability, and team alignment.**

---

## 1. Type Hints & Type Safety

### Rule: Type hints on ALL functions

Every function must have complete type hints:

```python
# ✅ GOOD — Type hints on inputs and output
def calculate_score(
    revenue: float,
    growth_rate: float,
    employees: int | None = None
) -> float:
    """Calculate growth score from financial metrics."""
    ...

# ❌ BAD — Missing type hints
def calculate_score(revenue, growth_rate, employees=None):
    """Calculate growth score from financial metrics."""
    ...

# ❌ BAD — Incomplete type hints
def calculate_score(revenue: float, growth_rate, employees) -> float:
    ...
```

### mypy Strict Mode

All code must pass `mypy --strict`:

```bash
mypy src/solstein/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true        # Require type hints
check_untyped_defs = true
no_implicit_optional = true
strict = true
```

### Union Types

Use `|` syntax (Python 3.10+), not `Union`:

```python
# ✅ GOOD
def find_company(company_id: str) -> Company | None:
    ...

# ❌ BAD (outdated)
from typing import Union
def find_company(company_id: str) -> Union[Company, None]:
    ...

# ❌ BAD (use | instead)
from typing import Optional
def find_company(company_id: str) -> Optional[Company]:
    ...
```

### Generic Types

```python
# ✅ GOOD
def find_by_filter(filters: dict[str, Any]) -> list[Company]:
    ...

# ❌ BAD
def find_by_filter(filters):
    ...

# ❌ BAD (old syntax)
from typing import Dict, List
def find_by_filter(filters: Dict[str, Any]) -> List[Company]:
    ...
```

---

## 2. Error Handling

### Rule: NEVER Silent Failures

**This is the #1 code quality rule in Solstein.**

```python
# ✅ GOOD — Log and re-raise
try:
    company = repo.find_by_id(company_id)
except DatabaseError as e:
    logger.error(f"[DB] Failed to fetch company {company_id}: {e}")
    raise  # Re-raise to caller

# ✅ GOOD — Return error result
def save_company(company: Company) -> Result[str, Error]:
    try:
        return Ok(repo.save(company))
    except Exception as e:
        logger.error(f"Save failed: {e}")
        return Err(Error(code="SAVE_FAILED", message=str(e)))

# ❌ BAD — Silent failure
try:
    company = repo.find_by_id(company_id)
except DatabaseError:
    pass  # 🔥 BUG: Silently swallow error

# ❌ BAD — Comment-only catch
try:
    company = repo.find_by_id(company_id)
except DatabaseError:
    # Ignore errors
    pass  # 🔥 Still bad, just documented

# ❌ BAD — Return None without context
try:
    company = repo.find_by_id(company_id)
except DatabaseError:
    return None  # 🔥 Caller doesn't know why it failed
```

### Logging Errors

Always include context:

```python
# ✅ GOOD — Error with full context
logger.error(
    "Scoring failed for company",
    extra={
        "company_id": company_id,
        "error_type": type(exc).__name__,
        "scoring_dimension": "growth",
    }
)

# ❌ BAD — Vague error message
logger.error("Something went wrong")

# ❌ BAD — No context
logger.error(str(exc))
```

### Result Types for Operations

For operations that can fail, use Result type:

```python
from typing import TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")

class Ok:
    def __init__(self, value: T): self.value = value

class Err:
    def __init__(self, error: E): self.error = error

Result = Union[Ok, Err]

# Usage
def validate_company(data: dict) -> Result[Company, ValidationError]:
    try:
        company = Company(**data)
        return Ok(company)
    except ValueError as e:
        return Err(ValidationError(str(e)))

# Caller must handle both cases
result = validate_company(data)
if isinstance(result, Ok):
    company = result.value
elif isinstance(result, Err):
    logger.error(f"Validation failed: {result.error}")
```

---

## 3. Code Style & Formatting

### Ruff Configuration

All code must pass `ruff check` and `ruff format`:

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "N",    # pep8-naming
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
]

ignore = [
    "B008",  # function-call-in-default-argument
]
```

**Format before committing:**
```bash
ruff format src/ tests/
ruff check src/ tests/ --fix
```

### Naming Conventions

| What | Convention | Example |
|------|-----------|---------|
| Variables | `snake_case` | `company_id`, `growth_score` |
| Constants | `UPPER_SNAKE_CASE` | `ROCKET_THRESHOLD = 7.0` |
| Classes | `PascalCase` | `Company`, `GrowthScorer` |
| Functions | `snake_case` | `calculate_score()` |
| Private methods | `_snake_case` | `_calculate_growth_score()` |
| Protected members | Single underscore | `_internal_cache` |
| Magic methods | Dunder case | `__init__()`, `__str__()` |

```python
# ✅ GOOD
MAX_SCORE = 10.0
ROCKET_THRESHOLD = 7.0

class CompanyScorer:
    def __init__(self):
        self._cache: dict[str, float] = {}
    
    def calculate_score(self, company: Company) -> float:
        return self._calculate_from_metrics(company.financials)
    
    def _calculate_from_metrics(self, metrics: FinancialMetric) -> float:
        ...

# ❌ BAD
max_score = 10.0                           # Should be constant
rocket_threshold = 7.0
Company_Scorer = None                      # Misleading name

class companyScorer:                       # Should be PascalCase
    def __init__(self):
        self.cache = {}                    # Should be private (_cache)
    
    def CalculateScore(self, company):    # Should be snake_case
        ...
```

### Line Length

**Maximum 88 characters** (enforced by ruff):

```python
# ✅ GOOD — Under 88 chars
message = f"Scoring {company.name}: {score:.2f} ({classification})"

# ❌ BAD — Over 88 chars
message = f"Scoring {company.name} with a calculated score of {score:.2f} and final classification of {classification}"

# ✅ GOOD — Use line continuation
message = (
    f"Scoring {company.name}: "
    f"{score:.2f} ({classification})"
)
```

### Import Organization

```python
# ✅ GOOD — Standard order (isort enforced)

# 1. Standard library
from datetime import datetime
from pathlib import Path
from typing import Any

# 2. Third-party libraries
import pandas as pd
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from loguru import logger

# 3. Local imports
from solstein.config import Settings
from solstein.domain.models import Company
from solstein.analytics.scoring import GrowthScorer
```

**Let ruff fix imports:**
```bash
ruff check --select I src/ --fix
```

---

## 4. Documentation

### Docstring Format: Google Style

```python
# ✅ GOOD — Google-style docstring
def calculate_scores(self, company: Company) -> Company:
    """Calculate all scores for a company profile.
    
    Computes growth, financial health, and competitive position
    scores, then applies classification logic.
    
    Args:
        company: Company profile to score.
    
    Returns:
        The same company with scores and classification populated.
        Note: This method mutates the input (see ADR-008).
    
    Raises:
        ValueError: If company has no financial data.
    
    Examples:
        >>> scorer = GrowthScorer()
        >>> company = Company(id="test", name="Test Corp")
        >>> company.financials = FinancialMetric(revenue=100.0)
        >>> result = scorer.calculate_scores(company)
        >>> result.growth_score
        5.5
    """
    ...
```

### What Needs Documentation

✅ **ALWAYS document:**
- Public functions/methods (all of them)
- Classes (purpose, usage)
- Modules (what the module does)
- Complex algorithms (explain logic)
- Important edge cases
- Warning about side effects

❌ **Don't document:**
- Obvious getters/setters
- Standard library functions
- Repeated patterns (document once, link elsewhere)
- Disabled code (delete it instead)

### Comment Style

Use comments sparingly; let code be self-documenting:

```python
# ✅ GOOD — Code explains itself
companies_by_classification = {
    "Rocket": [],
    "Neutral": [],
    "Dinosaur": [],
}
for company in companies:
    companies_by_classification[company.classification].append(company)

# ❌ BAD — Obvious comment clutter
# Loop through companies
for company in companies:
    # Get the classification
    c = company.classification
    # Group by classification
    companies_by_classification[c].append(company)

# ✅ GOOD — Document WHY, not WHAT
# Cap score at 10.0 because scoring formulae can exceed due to
# bonuses stacking (see ADR-008 about mutation concern)
score = min(score, 10.0)

# ❌ BAD — Document WHAT (code already shows this)
# Cap the score
score = min(score, 10.0)
```

---

## 5. Functions & Methods

### Length Limits

- **Functions:** < 50 lines (< 20 preferred)
- **Methods:** < 30 lines (< 15 preferred)

If a function exceeds these, break it into smaller functions:

```python
# ❌ BAD — Too long, too many concerns
def process_market(market: str):
    # 1. Load data
    companies = load_companies(market)
    
    # 2. Score them
    for company in companies:
        calculate_scores(company)
    
    # 3. Filter
    rockets = [c for c in companies if c.classification == "Rocket"]
    
    # 4. Export
    exporter = ExcelExporter()
    exporter.export(rockets)
    
    # 5. Notify
    send_email(f"Processed {len(companies)} companies")
    # ... 40 more lines

# ✅ GOOD — Break into focused functions
def process_market(market: str) -> None:
    """Process market: load, score, export."""
    companies = load_companies(market)
    score_companies(companies)
    export_rockets(companies)
    notify_completion(len(companies))

def score_companies(companies: list[Company]) -> None:
    """Score all companies in-place."""
    scorer = GrowthScorer()
    for company in companies:
        scorer.calculate_scores(company)

def export_rockets(companies: list[Company]) -> None:
    """Export only Rocket-classified companies."""
    rockets = [c for c in companies if c.classification == "Rocket"]
    ExcelExporter().export(rockets)
```

### Single Responsibility Principle

Each function should do ONE thing:

```python
# ❌ BAD — Multiple concerns mixed
def save_and_export(company: Company, output_path: Path) -> None:
    """Save to database AND export to Excel (two concerns!)."""
    repo.save(company)
    exporter.export([company], output_path)

# ✅ GOOD — Separate concerns
def save_company(company: Company) -> None:
    """Save company to repository."""
    repo.save(company)

def export_to_excel(companies: list[Company], path: Path) -> None:
    """Export companies to Excel file."""
    exporter.export(companies, path)

# Combine in orchestrator
def process_company(company: Company, output_path: Path) -> None:
    save_company(company)
    export_to_excel([company], output_path)
```

### Pure Functions Preferred

Functions should have no side effects:

```python
# ✅ GOOD — Pure function (no side effects)
def classify_company(growth_score: float) -> str:
    """Classify based on score (pure, testable)."""
    if growth_score >= 7.0:
        return "Rocket"
    elif growth_score <= 4.0:
        return "Dinosaur"
    return "Neutral"

# ⚠️ ACCEPTABLE — Side effect necessary (logging)
def calculate_scores(company: Company) -> Company:
    """Calculate scores (mutates company, see ADR-008)."""
    logger.debug(f"Scoring {company.name}")  # Side effect OK for logging
    # ... calculation ...
    return company

# ❌ BAD — Unnecessary side effects
def classify_company(growth_score: float) -> str:
    global results_cache  # ❌ Hidden global state
    results_cache.append(growth_score)
    print(f"Classified: {growth_score}")  # ❌ Side effect
    # ... return ...
```

---

## 6. Logging

### Structured Logging

Use loguru with structured fields:

```python
from loguru import logger

# ✅ GOOD — Structured logging with context
logger.info(
    "Company scored successfully",
    extra={
        "company_id": company.id,
        "growth_score": company.growth_score,
        "classification": company.classification,
        "processing_time_ms": elapsed_ms,
    }
)

# ✅ GOOD — Log levels appropriately
logger.debug("Starting score calculation for company")  # Low-level detail
logger.info("Company scored as Rocket")                # Interesting event
logger.warning("Profit margin is negative")            # Potential issue
logger.error("Database connection failed")             # Error occurred

# ❌ BAD — Unstructured
logger.info(f"Company {company.id} scored {company.growth_score}")

# ❌ BAD — Wrong log level
logger.info("Debug: starting loop iteration 5")  # Should be debug()
logger.error("Skipping company with no revenue")  # Should be warning()
```

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Development details | "Loaded 5 companies from repository" |
| **INFO** | Interesting events | "Market analysis completed: 100 companies" |
| **WARNING** | Potential issues | "Company has negative margin" |
| **ERROR** | Recoverable errors | "Failed to score company, skipping" |
| **CRITICAL** | System failure | "Database offline, all operations failed" |

---

## 7. Configuration Management

### Rule: NO Hardcoded Values

All tuneable values go through configuration:

```python
# ❌ BAD — Hardcoded threshold
def classify(growth_score: float) -> str:
    if growth_score >= 7.0:  # 🔥 Magic number
        return "Rocket"
    ...

# ✅ GOOD — Configurable threshold
class ScoringConfig:
    rocket_threshold: float = 7.0

def classify(growth_score: float, config: ScoringConfig) -> str:
    if growth_score >= config.rocket_threshold:
        return "Rocket"
    ...

# Or use environment variable
ROCKET_THRESHOLD = os.getenv("ROCKET_THRESHOLD", "7.0")
```

### Configuration via Environment

```python
# .env file
SOLSTEIN_DATABASE__URL=postgresql://...
SOLSTEIN_REDIS__URL=redis://localhost:6379/0
SOLSTEIN_SCORING__GROWTH__ROCKET_THRESHOLD=7.0

# config.py loads with Pydantic
class Settings(BaseSettings):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scoring: ScoringSettings = Field(default_factory=ScoringSettings)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"  # Supports nested config

# Usage
settings = Settings()
print(settings.database.url)
```

### NO Hardcoded Paths

```python
# ❌ BAD — Hardcoded path
data_file = "/home/user/solstein/data/input/companies.json"

# ✅ GOOD — Configuration-driven
data_dir = settings.data.data_dir  # From config
data_file = data_dir / "companies.json"

# ✅ GOOD — Use pathlib
from pathlib import Path
data_file = Path(__file__).parent / "data" / "companies.json"
```

---

## 8. Dataclasses & Models

### Use Dataclasses for Domain Models

```python
# ✅ GOOD — Domain model is a dataclass (pure Python)
from dataclasses import dataclass, field

@dataclass
class Company:
    id: str
    name: str
    growth_score: float | None = None
    tech_stack: list[str] = field(default_factory=list)

# ✅ GOOD — Pydantic for validation/serialization
from pydantic import BaseModel, Field

class CompanySchema(BaseModel):
    id: str
    name: str
    growth_score: float | None = None

# ❌ BAD — Don't mix frameworks in domain model
from sqlalchemy import Column, String

@dataclass
class Company:
    id: str = Column(String, primary_key=True)  # ❌ Framework leak
```

### Immutability When Possible

```python
# ✅ GOOD — Frozen dataclass (immutable)
@dataclass(frozen=True)
class Score:
    """Immutable score value."""
    value: float
    dimension: str

# Mutation not allowed:
# score.value = 10.0  # ❌ TypeError

# ✅ ACCEPTABLE — Mutable domain model (document mutation!)
@dataclass
class Company:
    """Mutable company profile. Note: calculate_scores() mutates this (ADR-008)."""
    growth_score: float | None = None
```

---

## 9. Testing

### Test Naming Convention

```python
# ✅ GOOD — Clear test names
def test_rocket_classification_with_high_growth():
    """High growth should classify as Rocket."""
    ...

def test_dinosaur_classification_with_low_growth():
    """Low growth should classify as Dinosaur."""
    ...

def test_invalid_company_raises_validation_error():
    """Invalid company data should raise ValueError."""
    ...

# ❌ BAD — Unclear names
def test_classification():
    ...

def test_stuff():
    ...

def test_1():
    ...
```

### Test Structure (Arrange-Act-Assert)

```python
# ✅ GOOD — Clear 3-phase structure
def test_calculate_score():
    # Arrange — Set up test data
    company = make_company(growth_rate=50.0)
    scorer = GrowthScorer()
    
    # Act — Perform action
    result = scorer.calculate_scores(company)
    
    # Assert — Verify results
    assert result.growth_score > 7.0
    assert result.classification == "Rocket"
```

### Use pytest.approx for Floats

```python
# ✅ GOOD — Allow small floating-point differences
assert result.score == pytest.approx(7.5, abs=0.01)

# ❌ BAD — Exact comparison fails due to float precision
assert result.score == 7.5  # Might be 7.500000000001
```

---

## 10. Dependencies & Imports

### Dependency Management

```toml
# pyproject.toml

[project]
dependencies = [
    "pydantic>=2.0",
    "fastapi>=0.104",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "mypy>=1.6",
    "ruff>=0.1",
]
```

**Never pin exact versions** (except in `requirements.txt` for reproducibility):

```
# ✅ GOOD — Flexible versions
fastapi>=0.104,<1.0
pydantic>=2.0,<3.0

# ❌ BAD — Too restrictive
fastapi==0.104.1
pydantic==2.5.0
```

### Circular Imports

Avoid circular dependencies:

```python
# ❌ BAD — Circular dependency
# file: domain/models.py
from data.repositories import CompanyRepository  # ❌ Circular!

# file: data/repositories.py
from domain.models import Company  # Creates circular import

# ✅ GOOD — Use TYPE_CHECKING
# file: domain/models.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.repositories import CompanyRepository

@dataclass
class Company:
    repository: "CompanyRepository | None" = None  # String annotation, no import
```

---

## 11. Security Best Practices

### NO Secrets in Code

```python
# ❌ BAD — Hardcoded secret
database_url = "postgresql://admin:password123@localhost/solstein"

# ✅ GOOD — From environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not set in environment")
```

### Input Validation

```python
# ✅ GOOD — Validate all inputs
def search_companies(query: str) -> list[Company]:
    # Validate query
    if not query or len(query) < 2:
        raise ValueError("Query must be at least 2 characters")
    
    # Escape for SQL (if using raw SQL, which you shouldn't)
    # Or use parameterized queries
    return repo.search(query)

# ❌ BAD — No validation
def search_companies(query: str) -> list[Company]:
    return repo.search(query)  # What if query is None or malicious?
```

### SQL Injection Prevention

```python
# ✅ GOOD — Parameterized query
query = "SELECT * FROM companies WHERE industry = %s"
cursor.execute(query, (industry,))

# ❌ BAD — String interpolation (SQL injection risk!)
query = f"SELECT * FROM companies WHERE industry = '{industry}'"
cursor.execute(query)
```

---

## Pre-commit Checklist

Before committing code:

```bash
# 1. Format code
ruff format src/ tests/

# 2. Fix lint issues
ruff check src/ tests/ --fix

# 3. Type check
mypy src/

# 4. Run tests
pytest tests/

# 5. Check coverage
pytest tests/ --cov=src/solstein --cov-report=term-missing

# All pass? → git add . && git commit -m "..."
```

---

## Exceptions to These Rules

Document any deviation:

```python
# Deviation from convention, explained
# (Disable mypy check only for this specific issue)
# mypy: ignore
risky_thing: Any = get_user_input()  # Intentional: Necessary for CLI input validation

# Or with comment
company_id = str(user_input)  # noqa: E501 Intentional: Legacy API requires string IDs
```

Use `# noqa` (flake8) and `# type: ignore` (mypy) sparingly, with explanations.

---

## References

- [pyproject.toml](../../pyproject.toml) — Tool configurations
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — Contributing guidelines
- [Module Architecture](../architecture/modules.md) — How modules are organized

---

*Last Updated: February 20, 2026*
*Maintained by: Dev Standards Committee*

