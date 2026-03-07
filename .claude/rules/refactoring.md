# Refactoring Rules

## When to Refactor

### Trigger Conditions
Refactor when you encounter:
- **God functions** (>100 lines)
- **God classes** (>300 lines)
- **God files** (>500 lines)
- **Deep nesting** (>3 levels of indentation)
- **High cyclomatic complexity** (>10)
- **Duplicate code** (3+ occurrences)
- **Feature envy** (class uses another class's data excessively)
- **Shotgun surgery** (change requires modifying many classes)

### Refactoring Workflow
1. **Ensure tests exist** - Never refactor without tests
2. **Run tests** - Verify they pass before changes
3. **Make small changes** - One refactoring at a time
4. **Run tests** - Verify they still pass
5. **Commit** - Small, focused commits
6. **Repeat** - Until goal achieved

## Extraction Patterns

### Extract Method
```python
# ❌ BEFORE - Long function with mixed concerns
def process_company_data(data):
    # Validate data (20 lines)
    # Transform data (30 lines)
    # Save to database (25 lines)
    # Send notification (15 lines)
    pass

# ✅ AFTER - Extracted methods
def process_company_data(data):
    validated = self._validate_data(data)
    transformed = self._transform_data(validated)
    saved = self._save_to_database(transformed)
    self._send_notification(saved)
    return saved

def _validate_data(self, data): ...
def _transform_data(self, data): ...
def _save_to_database(self, data): ...
def _send_notification(self, data): ...
```

### Extract Class
```python
# ❌ BEFORE - Class with multiple responsibilities
class CompanyProcessor:
    def validate(self, data): ...      # Validation
    def transform(self, data): ...     # Transformation
    def save(self, data): ...          # Persistence
    def notify(self, data): ...        # Notification

# ✅ AFTER - Extracted classes
class CompanyValidator:
    def validate(self, data): ...

class CompanyTransformer:
    def transform(self, data): ...

class CompanyRepository:
    def save(self, data): ...

class NotificationService:
    def notify(self, data): ...

# Orchestrator
class CompanyProcessor:
    def __init__(self):
        self.validator = CompanyValidator()
        self.transformer = CompanyTransformer()
        self.repository = CompanyRepository()
        self.notifier = NotificationService()
```

### Extract Module
```python
# ❌ BEFORE - Monolithic module (800+ lines)
# database_models.py
class CompanyRecord: ...      # 150 lines
class ScoringRecord: ...      # 80 lines
class SignalRecord: ...       # 60 lines
class ResearchRunRecord: ...  # 100 lines
# ... 15 more models

# ✅ AFTER - Modular package
# models/
#   ├── __init__.py
#   ├── base.py              # SQLAlchemy Base
#   ├── company.py           # Company, Scoring, Signal
#   ├── research.py          # Research pipeline models
#   ├── enrichment.py        # Enrichment models
#   └── infrastructure.py    # Outbox, Tenant

# __init__.py - Re-export for backward compatibility
from .company import CompanyRecord, ScoringRecord, SignalRecord
from .research import ResearchRunRecord, ResearchStageRecord
# ... etc
```

## Design Patterns for Refactoring

### Strategy Pattern
Use when you have multiple algorithms or behaviors:
```python
from abc import ABC, abstractmethod

class DataSourceStrategy(ABC):
    @abstractmethod
    def fetch(self, company_id: str) -> dict: ...

class SECEDGARStrategy(DataSourceStrategy):
    def fetch(self, company_id: str) -> dict: ...

class CompaniesHouseStrategy(DataSourceStrategy):
    def fetch(self, company_id: str) -> dict: ...

class NewsAPIStrategy(DataSourceStrategy):
    def fetch(self, company_id: str) -> dict: ...

# Usage
strategies = {
    "sec_edgar": SECEDGARStrategy(),
    "companies_house": CompaniesHouseStrategy(),
    "news_api": NewsAPIStrategy(),
}
```

### Builder Pattern
Use when constructing complex objects:
```python
class CompanyBuilder:
    def __init__(self):
        self.company = Company()
    
    def with_basic_info(self, name, industry): ...
    def with_financials(self, revenue, growth): ...
    def with_funding(self, rounds, total): ...
    def with_ai_metrics(self, score, maturity): ...
    
    def build(self) -> Company:
        return self.company

# Usage
company = (CompanyBuilder()
    .with_basic_info("Acme Corp", "Technology")
    .with_financials(1000000, 0.25)
    .with_funding(["Series A"], 5000000)
    .with_ai_metrics(0.85, "advanced")
    .build())
```

### Pipeline Pattern
Use for multi-stage processing:
```python
class PipelineStage(ABC):
    @abstractmethod
    def execute(self, context: PipelineContext) -> StageResult: ...

class DiscoveryStage(PipelineStage):
    def execute(self, context): ...

class GatherStage(PipelineStage):
    def execute(self, context): ...

class AggregateStage(PipelineStage):
    def execute(self, context): ...

class ScoreStage(PipelineStage):
    def execute(self, context): ...

# Usage
pipeline = [DiscoveryStage(), GatherStage(), AggregateStage(), ScoreStage()]
for stage in pipeline:
    result = stage.execute(context)
    if not result.success:
        break
```

## Backward Compatibility

### Gradual Migration Strategy
When refactoring public APIs:
```python
# OLD location (deprecated but functional)
# infrastructure/database_models.py
from .models import CompanyRecord  # Re-export
import warnings

warnings.warn(
    "Import from infrastructure.database_models is deprecated. "
    "Use infrastructure.models instead.",
    DeprecationWarning,
    stacklevel=2
)

# NEW location
# infrastructure/models/company.py
class CompanyRecord(Base):
    """Primary location for CompanyRecord."""
    ...
```

### Deprecation Timeline
1. **Phase 1**: Create new structure, re-export from old
2. **Phase 2**: Update internal imports to use new location
3. **Phase 3**: Add deprecation warnings to old imports
4. **Phase 4**: Remove old imports (after 2-3 releases)

## Refactoring Checklist

Before refactoring:
- [ ] Tests exist for the code to refactor
- [ ] Tests pass before changes
- [ ] Understand the code fully
- [ ] Have a clear goal for the refactoring

During refactoring:
- [ ] Make small, focused changes
- [ ] Run tests after each change
- [ ] Keep backward compatibility if public API
- [ ] Update documentation as you go

After refactoring:
- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] No regression in functionality
- [ ] Performance verified (if applicable)
