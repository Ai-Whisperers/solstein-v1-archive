# EPIC-019: Agent-Specific Code Quality Guidelines

## Pre-Commit Quality Checklist

This document provides quality guidelines for AI agents working on this codebase.

### Pre-Commit Hook

A pre-commit hook is available at `scripts/ci/agent_precommit_hook.py` that checks:

1. **Function Sizes** - No functions >100 lines
2. **Bare Except Clauses** - Use specific exceptions
3. **Lazy Imports** - All imports at top of file
4. **File Sizes** - No files >500 lines

### Installation

```bash
# Install the pre-commit hook
cp scripts/ci/agent_precommit_hook.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Quality Checklist

Before committing code, ensure:

- [ ] **Function Size**: All functions ≤100 lines
- [ ] **Class Size**: All classes ≤300 lines
- [ ] **File Size**: All files ≤500 lines
- [ ] **No Bare Except**: Use specific exception types
- [ ] **No Lazy Imports**: All imports at top of file
- [ ] **Type Hints**: Functions have type annotations
- [ ] **Docstrings**: Public functions have docstrings
- [ ] **Tests**: New code has tests

### Automated Checks

Run quality checks manually:

```bash
# Full quality check
python scripts/ci/quality_check.py

# Specific checks
python scripts/ci/check_function_sizes.py src/solstein --max-lines 100
python scripts/ci/check_class_sizes.py src/solstein --max-lines 300
python scripts/ci/check_file_sizes.py --max-lines 500
python scripts/ci/code_smell_detector.py src/solstein

# Quality score dashboard
python scripts/ci/quality_score_dashboard.py src/solstein --pr-comment
```

### Code Quality Standards

#### Function Size Limits
- **Maximum**: 100 lines
- **Target**: <50 lines
- **Action**: Break down if exceeds 50 lines

#### Class Size Limits
- **Maximum**: 300 lines
- **Target**: <200 lines
- **Action**: Extract classes if exceeds 200 lines

#### File Size Limits
- **Maximum**: 500 lines
- **Target**: <400 lines
- **Action**: Split into modules if exceeds 400 lines

#### Error Handling
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

#### Import Rules
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

### Refactoring Patterns

When code exceeds limits, use these patterns:

#### Extract Method
```python
# Before
def big_function():
    # 100 lines of code

# After
def big_function():
    self.step_one()
    self.step_two()
    self.step_three()

def step_one(self): ...
def step_two(self): ...
def step_three(self): ...
```

#### Extract Class
```python
# Before
class BigClass:
    def method_a(self): ...  # Uses fields 1, 2, 3
    def method_b(self): ...  # Uses fields 1, 2, 3
    def method_c(self): ...  # Uses fields 4, 5, 6
    def method_d(self): ...  # Uses fields 4, 5, 6

# After
class ExtractedA:
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

    def method_a(self): ...
    def method_b(self): ...

class ExtractedB:
    def __init__(self, field4, field5, field6):
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6

    def method_c(self): ...
    def method_d(self): ...

class BigClass:
    def __init__(self):
        self.a = ExtractedA(...)
        self.b = ExtractedB(...)
```

### CI/CD Integration

Quality checks run automatically on:
- Every pull request
- Every push to main

The checks will:
- Post quality scores as PR comments
- Block PRs with critical violations
- Suggest refactoring for warnings

### Getting Help

If you encounter quality check failures:

1. Run `python scripts/ci/quality_check.py` locally
2. Review the specific violations
3. Apply appropriate refactoring patterns
4. Re-run checks before committing

### Definition of Done

- [ ] All quality checks pass
- [ ] Quality score is B or better
- [ ] No new code smells introduced
- [ ] Tests added for new code
- [ ] Documentation updated
