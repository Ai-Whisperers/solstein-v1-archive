# EPIC-019: Code Quality Guardrails

This document describes the automated code quality guardrails implemented for the Solstein project.

## Overview

EPIC-019 establishes CI/CD and pre-commit hooks to detect and prevent code smells from entering the codebase. This prevents accumulation of technical debt and ensures code quality standards are maintained.

## Quality Gates

### Required Checks (CI/CD Blocking)

These checks **MUST PASS** before a PR can be merged:

| Check | Limit | Description |
|-------|-------|-------------|
| **Function Sizes** | Max 100 lines | No function can exceed 100 lines |
| **Class Sizes** | Max 300 lines | No class can exceed 300 lines |
| **File Sizes** | Max 500 lines | No file can exceed 500 lines |
| **Folder Structure** | Standard only | Validates project folder structure |
| **Import Cycles** | None allowed | Detects circular imports between modules |
| **EPIC-020 Patterns** | Must follow | Validates architectural patterns |

### Optional Checks (Warnings)

These checks run but don't block PRs:

| Check | Description |
|-------|-------------|
| **Code Smells** | Detects god functions, god classes, bare excepts |
| **Dead Code** | Identifies potentially unused code |
| **Module Boundaries** | Enforces architectural layer boundaries |
| **Architecture Compliance** | Checks for lazy imports and other violations |
| **Code Duplication** | Detects duplicate code blocks |

## Running Checks

### Run All Checks
```bash
python3 scripts/ci/quality_check.py
```

### Run Only Required Checks
```bash
python3 scripts/ci/quality_check.py --only-required
```

### List Available Checks
```bash
python3 scripts/ci/quality_check.py --list
```

### Check Specific File
```bash
python3 scripts/ci/code_smell_detector.py src/solstein/path/to/file.py
python3 scripts/ci/check_function_sizes.py src/solstein/path/to/file.py
python3 scripts/ci/check_class_sizes.py src/solstein/path/to/file.py
python3 scripts/ci/check_file_sizes.py src/solstein/path/to/file.py
```

## Pre-commit Hook

The pre-commit hook automatically runs on staged Python files:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run agent-code-quality
pre-commit run code-smell-detector
```

## CI/CD Integration

Code quality checks run automatically on every PR via GitHub Actions:

- `.github/workflows/code-quality-guardrails.yml` - Full quality gate suite
- `.github/workflows/pre-commit.yml` - Pre-commit hook validation

### Quality Score

The CI calculates a quality score based on:
- Function size compliance
- Class size compliance
- File size compliance
- Code smell density
- Architecture compliance

Scores are posted as PR comments for visibility.

## Configuration

### Limits (Hard-coded in Scripts)

```python
# Function size limits
MAX_FUNCTION_LINES = 100      # Hard fail
WARNING_FUNCTION_LINES = 50   # Warning

# Class size limits
MAX_CLASS_LINES = 300         # Hard fail
MAX_CLASS_METHODS = 15        # Hard fail
WARNING_CLASS_LINES = 200     # Warning

# File size limits
MAX_FILE_LINES = 500          # Hard fail
WARNING_FILE_LINES = 400      # Warning

# Parameter limits
MAX_PARAMETERS = 5            # Warning

# Nesting limits
MAX_NESTING_DEPTH = 4         # Warning
```

### Ignoring Violations (Temporary)

**NOT RECOMMENDED**, but possible with comments:

```python
# noqa: function-size  # Temporary override, needs refactoring
```

## Code Smell Definitions

### Function Smells

1. **God Function** (>100 lines)
   - **Detection**: AST traversal counting executable lines
   - **Fix**: Extract methods, use strategy pattern

2. **Many Parameters** (>5 parameters)
   - **Detection**: AST argument counting
   - **Fix**: Use parameter objects or builders

3. **Deep Nesting** (>4 levels)
   - **Detection**: AST depth analysis
   - **Fix**: Extract early returns, guard clauses

4. **Bare Except Clause**
   - **Detection**: AST except handlers without type
   - **Fix**: Catch specific exceptions

### Class Smells

1. **God Class** (>300 lines OR >15 methods)
   - **Detection**: AST class definition analysis
   - **Fix**: Extract classes, single responsibility

## CI/CD Failure Examples

### ❌ Failed: Function Too Large
```
🔴 src/solstein/api/services.py:42
   Function: analyze_company (127 lines)
   Issue: Function exceeds 100 line limit
```

### ❌ Failed: Bare Except
```
🔴 src/solstein/utils.py:88
   Issue: Bare except clause detected
   Fix: Use 'except SpecificError:' instead of 'except:'
```

### ❌ Failed: Circular Import
```
🔴 Circular import detected:
   src/solstein/domain/models.py ->
   src/solstein/infrastructure/database_models.py ->
   src/solstein/domain/models.py
```

### ✅ All Checks Passed
```
============================================================
Summary
============================================================
✅ Function Sizes (required)
✅ Class Sizes (required)
✅ File Sizes (required)
✅ Folder Structure (required)
✅ Import Cycles (required)
✅ EPIC-020 Patterns (required)

============================================================
✅ All required checks passed!
============================================================
```

## Current Baseline

The codebase has existing code smells that are tracked in:
- `COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md`

**New code must not increase smell count.**

Current counts (as of 2026-03):
- 24 God Functions (>100 lines)
- 84 Long Functions (50-100 lines)
- 19 God Classes (>300 lines)
- 25 Files (>500 lines)

## Agent Guidelines

When working with Claude Code agents:

1. **Agents must run checks before committing**
2. **Agents must fix violations before creating PRs**
3. **Agents must not increase smell counts**

The agent pre-commit hook enforces these rules automatically.

## Related Epics

- **EPIC-020**: God Function Refactoring
- **EPIC-021**: File Splitting and Modularization
- **EPIC-022**: God Class Refactoring

## References

- [GitHub Actions Code Quality Workflow](../../.github/workflows/code-quality-guardrails.yml)
- [Pre-commit Configuration](../../.pre-commit-config.yaml)
- [Quality Check Script](../../scripts/ci/quality_check.py)
- [Code Smell Detector](../../scripts/ci/code_smell_detector.py)
