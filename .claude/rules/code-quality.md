# Code Quality Rules

## File Size Limits

### Maximum File Sizes
- **Python files**: 500 lines maximum
- **Class definitions**: 300 lines maximum
- **Function definitions**: 100 lines maximum
- **Test files**: 300 lines maximum (split by feature)

### When to Split Files
Split files when they exceed limits or when:
- Multiple unrelated classes in one file
- Mixed abstraction levels
- Different domains/concepts mixed together
- More than 5-7 public functions/classes

### Splitting Patterns
```python
# ❌ BAD - Monolithic file (800+ lines)
# src/solstein/infrastructure/database_models.py
# Contains 19 models in one file

# ✅ GOOD - Modular package
# src/solstein/infrastructure/models/
#   ├── __init__.py       # Re-exports
#   ├── base.py           # SQLAlchemy Base
#   ├── company.py        # Company, Scoring models
#   ├── research.py       # Research pipeline models
#   ├── enrichment.py     # Enrichment models
#   └── infrastructure.py # Outbox, Tenant models
```

## Function Size Limits

### Maximum Function Sizes
- **Public functions**: 100 lines maximum
- **Private functions**: 50 lines maximum
- **Test functions**: 30 lines maximum

### When to Extract Functions
Extract functions when:
- Function exceeds 50 lines
- Deep nesting (>3 levels)
- Multiple responsibilities
- Duplicate code blocks
- Complex conditional logic

### Extraction Patterns
```python
# ❌ BAD - God function (500+ lines)
def run_market_intelligence(args):
    # 500+ lines of mixed concerns
    pass

# ✅ GOOD - Extracted pipeline stages
def run_market_intelligence(args):
    context = PipelineContext(args)
    stages = [
        DiscoveryStage(),
        GatherStage(),
        AggregateStage(),
        ScoreStage(),
        ExportStage(),
    ]
    for stage in stages:
        result = stage.execute(context)
        if not result.success:
            break
    return context.results
```

## Class Size Limits

### Maximum Class Sizes
- **Service classes**: 300 lines maximum
- **Model classes**: 200 lines maximum
- **Utility classes**: 150 lines maximum

### When to Split Classes
Split classes when:
- Class exceeds 300 lines
- More than 10-15 methods
- Multiple responsibilities (SRP violation)
- High cohesion between some methods only

### Class Extraction Patterns
```python
# ❌ BAD - God class (454 lines, 50+ signals)
class SignalDefinitions:
    GROWTH_SIGNALS = [...]      # 80 lines
    FINANCIAL_SIGNALS = [...]   # 60 lines
    TECHNICAL_SIGNALS = [...]   # 70 lines
    # ... 5 more categories

# ✅ GOOD - Extracted by category
# definitions/growth.py
GROWTH_SIGNALS = [...]

# definitions/financial.py
FINANCIAL_SIGNALS = [...]

# definitions/__init__.py
from .growth import GROWTH_SIGNALS
from .financial import FINANCIAL_SIGNALS
# ... etc

class SignalDefinitions:
    """Registry that imports from category modules."""
    GROWTH_SIGNALS = GROWTH_SIGNALS
    FINANCIAL_SIGNALS = FINANCIAL_SIGNALS
    # ... etc
```

## Import Organization

### Import Structure
```python
# 1. Standard library
import os
import sys
from typing import Any

# 2. Third-party libraries
from sqlalchemy import Column
from pydantic import BaseModel

# 3. Local application - absolute imports
from solstein.domain.models import Company
from solstein.infrastructure.database import get_session

# 4. Local application - relative imports (within same package)
from .base import Base
from .utils import helper
```

### Import Rules
- **NEVER use circular imports** at module level
- **Use TYPE_CHECKING** for type-only imports
- **Move imports inside functions** to break circular dependencies
- **Prefer absolute imports** over relative for cross-package

### Circular Import Prevention
```python
# ❌ BAD - Circular import at module level
# file_a.py
from file_b import ClassB

# file_b.py
from file_a import ClassA

# ✅ GOOD - Use TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from file_b import ClassB

# ✅ GOOD - Import inside function
def process():
    from file_b import ClassB  # Breaks circular dependency
    return ClassB()
```

## Code Duplication

### DRY Principle
- Extract duplicate logic into shared functions
- Use inheritance or composition for similar classes
- Consider strategy pattern for similar algorithms
- Review exact duplicates for accidental copy-paste

### Detection
Run regularly:
```bash
python scripts/ci/detect_code_duplication.py --directory src
```

## Quality Gates

### Pre-Commit Checks
All code must pass:
1. Function size check (<100 lines)
2. Class size check (<300 lines)
3. File size check (<500 lines)
4. Import cycle detection (zero cycles)
5. Bare except detection (zero bare excepts)
6. Code duplication check (no exact duplicates)

### CI/CD Integration
```yaml
# .github/workflows/quality.yml
- name: Code Quality Checks
  run: |
    python scripts/ci/check_function_sizes.py --max-lines 100
    python scripts/ci/check_class_sizes.py --max-lines 300
    python scripts/ci/check_file_sizes.py --max-lines 500
    python scripts/ci/detect_import_cycles.py
    python scripts/ci/code_smell_detector.py
    python scripts/ci/detect_code_duplication.py
```
