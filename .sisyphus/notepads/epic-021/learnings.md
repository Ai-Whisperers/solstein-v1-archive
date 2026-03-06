# EPIC-021 File Splitting Modularization - Learnings

## Conventions

### File Size Limits
- **Maximum:** 500 lines per file
- **Target:** <400 lines per file
- **Function Max:** 100 lines per function
- **Class Max:** 300 lines per class

### Migration Strategy (Phase 1: Internal Extraction)
1. Create new module files
2. Move classes/functions to new modules
3. Import in original file for backward compatibility
4. Update tests
5. Later phases will update imports and remove original files

### Module Structure Patterns

#### For exporters/markdown/:
```
exporters/markdown/
├── __init__.py          # Public API exports
├── generator.py         # Orchestration only (~200 lines)
├── templates.py         # Template definitions (~250 lines)
├── formatters.py        # Formatting logic (~300 lines)
├── tables.py            # Table generation (~200 lines)
├── charts.py            # Chart embedding (~150 lines)
├── sections/            # Section generators
│   ├── __init__.py
│   ├── executive_summary.py
│   ├── competitive_analysis.py
│   └── financial_analysis.py
└── utils.py             # Shared utilities (~100 lines)
```

#### For data/loaders/:
```
data/loaders/
├── __init__.py
├── unified.py           # Orchestration (~200 lines)
├── sec_edgar.py         # SEC EDGAR loading (~250 lines)
├── companies_house.py   # UK Companies House (~200 lines)
├── linkedin.py          # LinkedIn loading (~150 lines)
├── news.py              # News loading (~150 lines)
└── merger.py            # Data merging logic (~150 lines)
```

#### For infrastructure/models/:
```
infrastructure/models/
├── __init__.py
├── base.py              # Shared base classes (~100 lines)
├── company.py           # Company models (~150 lines)
├── research.py          # Research models (~200 lines)
├── enrichment.py        # Enrichment models (~150 lines)
├── scoring.py           # Scoring models (~150 lines)
└── audit.py             # Audit models (~150 lines)
```

### Import Compatibility Pattern
```python
# In original file (e.g., exporters/markdown/generator.py)
# After splitting, keep backward compatibility:
from .templates import ReportTemplate, SectionTemplate
from .formatters import format_currency, format_percentage
from .tables import generate_comparison_table
# ... etc

# Or re-export from __init__.py
```

### Testing Requirements
- Golden tests for behavior preservation
- Import tests for each new module
- Integration tests for cross-module calls
- All existing tests must pass

## Code Quality Rules (from AGENTS.md)
- **NEVER use bare except clauses**
- **ALWAYS catch specific exceptions**
- **NO lazy imports** (imports inside functions)
- **Place all imports at top of file**
- **Use absolute imports** (not relative)
- Type hints required for functions under mypy coverage
- Google-style docstrings

## Python Standards
- Line Length: 120 characters (Black)
- Import Order: isort (stdlib → third-party → local)
- Naming: snake_case modules, PascalCase classes
- Error handling: Use loguru logger, never silent catches
