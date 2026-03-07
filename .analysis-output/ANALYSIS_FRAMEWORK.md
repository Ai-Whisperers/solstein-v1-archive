# 🔍 SOLSTEIN CODEBASE ANALYSIS FRAMEWORK

> **Automated Hourly Analysis**  
> **Purpose:** Continuous codebase quality monitoring  
> **Output:** EPICs, Stories, and Improvement Recommendations

---

## 📋 ANALYSIS CHECKLIST

### 1. Code Quality & Anti-Patterns

#### God Objects & Functions
- [ ] Functions >100 lines
- [ ] Classes >300 lines
- [ ] Files >500 lines
- [ ] Modules with >20 public functions

#### Code Smells
- [ ] Bare except clauses
- [ ] Deep nesting (>4 levels)
- [ ] Long parameter lists (>5 params)
- [ ] Primitive obsession (strings instead of types)
- [ ] Lazy imports inside functions
- [ ] Mixed abstraction levels

#### Architecture Issues
- [ ] Circular imports
- [ ] Layer violations (domain → infrastructure)
- [ ] Mixed sync/async code
- [ ] Tight coupling between modules
- [ ] Missing interfaces/abstractions

### 2. Design Patterns Assessment

#### Missing Patterns
- [ ] **Factory Pattern**: Complex object creation scattered
- [ ] **Repository Pattern**: Data access mixed with business logic
- [ ] **Strategy Pattern**: Hardcoded algorithms
- [ ] **Observer Pattern**: No event-driven architecture
- [ ] **Command Pattern**: Actions not encapsulated
- [ ] **Adapter Pattern**: Inconsistent external API wrappers

#### Dependency Injection
- [ ] Hardcoded dependencies
- [ ] Missing DI containers
- [ ] Difficult-to-test code

### 3. Modularization Opportunities

#### File Splitting Candidates
- [ ] Files >500 lines
- [ ] Files with >10 classes
- [ ] Files with mixed responsibilities

#### Module Consolidation
- [ ] Duplicate functionality across modules
- [ ] Overlapping concerns
- [ ] Common utilities scattered

#### Interface Extraction
- [ ] Protocol classes needed
- [ ] Abstract base classes missing
- [ ] Public API surface unclear

### 4. Performance & Scalability

#### Async Issues
- [ ] Blocking I/O in async functions
- [ ] Missing await keywords
- [ ] Synchronous libraries in async contexts

#### Database Issues
- [ ] N+1 query patterns
- [ ] Missing pagination
- [ ] Unbounded result sets
- [ ] Missing indexes

#### Memory Issues
- [ ] Large in-memory datasets
- [ ] Memory leaks in long-running processes
- [ ] Unnecessary object retention

#### Caching Opportunities
- [ ] Repeated expensive computations
- [ ] Static data re-fetched
- [ ] Missing memoization

### 5. Security Analysis

#### Input Validation
- [ ] Unvalidated user input
- [ ] SQL injection risks
- [ ] Command injection risks
- [ ] Path traversal vulnerabilities

#### Authentication/Authorization
- [ ] Missing auth checks
- [ ] Weak password handling
- [ ] Session management issues
- [ ] Privilege escalation risks

#### Secrets Management
- [ ] Hardcoded secrets
- [ ] Secrets in logs
- [ ] Unsafe secret storage

### 6. Testing Gaps

#### Coverage Issues
- [ ] Untested critical paths
- [ ] Missing edge case tests
- [ ] No integration tests
- [ ] Mock-heavy tests (not testing real logic)

#### Testability Issues
- [ ] Hardcoded dependencies
- [ ] Global state
- [ ] Side effects in constructors
- [ ] Missing test fixtures

### 7. Documentation Gaps

#### Code Documentation
- [ ] Missing docstrings
- [ ] Unclear function purposes
- [ ] Complex logic without comments
- [ ] No type hints

#### Architecture Documentation
- [ ] Missing ADRs
- [ ] Unclear module boundaries
- [ ] No data flow diagrams
- [ ] Missing API documentation

---

## 🎯 ANALYSIS OUTPUT FORMAT

### EPIC Template

```markdown
# EPIC-XXX: [Title]

## Problem Statement
Clear description of the problem.

## Business Impact
Why this matters.

## Success Criteria
- [ ] Measurable outcome 1
- [ ] Measurable outcome 2

## Stories
| ID | Title | Points | Priority |
|----|-------|--------|----------|
| STORY-XXX.1 | Story 1 | 3 | P0 |

## Risks
| Risk | Probability | Mitigation |
|------|-------------|------------|
| Risk 1 | High | Mitigation 1 |
```

### Story Template

```markdown
# STORY-XXX: [Title]

**Parent EPIC:** EPIC-XXX
**Points:** X
**Priority:** P0/P1/P2

## Description
What needs to be done.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
Implementation guidance.

## Files to Modify
- `src/solstein/path/to/file.py`

## Testing Requirements
- [ ] Unit tests
- [ ] Integration tests
```

### Analysis Report Template

```markdown
# Codebase Analysis Report

## Executive Summary
Key findings in 3-5 bullet points.

## Critical Issues (Fix Immediately)
| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|

## High Priority (Fix This Sprint)
| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|

## Medium Priority (Fix This Month)
| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|

## Anti-Patterns Catalog
### Category: [Anti-pattern Name]
**Description:** What it is
**Impact:** Why it's bad
**Examples:** File:line references
**Solution:** How to fix

## New EPICs Created
1. EPIC-XXX: Title
2. EPIC-XXX: Title

## Stories Created
- 15 new stories across 5 EPICs
```

---

## 🔧 ANALYSIS TOOLS

### Static Analysis
```bash
# Code complexity
radon cc src/solstein -a

# Code smells
pylint src/solstein

# Type checking
mypy src/solstein

# Import cycles
python scripts/ci/detect_import_cycles.py

# Function sizes
python scripts/ci/check_function_sizes.py
```

### Dynamic Analysis
```bash
# Test coverage
pytest --cov=src/solstein --cov-report=html

# Performance profiling
pytest tests/performance/

# Load testing
locust -f tests/load/locustfile.py
```

### Custom Scripts
- `scripts/ci/code_smell_detector.py`
- `scripts/audit_data_quality.py`
- `scripts/coverage_report.py`

---

## 📊 METRICS TO TRACK

### Code Quality Metrics
- **Code Smell Density**: smells per 100 lines
- **Average Function Length**: lines per function
- **Cyclomatic Complexity**: avg complexity score
- **Test Coverage**: percentage
- **Documentation Coverage**: percentage with docstrings

### Architecture Metrics
- **Circular Dependencies**: count
- **File Cohesion**: related functions per file
- **Module Coupling**: inter-module dependencies
- **Public API Surface**: exposed functions/classes

### Performance Metrics
- **Test Execution Time**: seconds
- **Import Time**: milliseconds
- **Memory Usage**: MB at peak
- **Database Query Count**: per request

---

## 🎭 SEVERITY LEVELS

| Level | Description | Action Required |
|-------|-------------|-----------------|
| 🔴 **Critical** | Production risk, security vulnerability | Fix within 24 hours |
| 🟠 **High** | Significant technical debt, blocking features | Fix this sprint |
| 🟡 **Medium** | Code smell, maintainability issue | Fix this month |
| 🟢 **Low** | Minor improvement, nice-to-have | Backlog |

---

## 🔄 HOURLY ANALYSIS WORKFLOW

1. **Run Static Analysis** (5 min)
   - Detect code smells
   - Check function/class sizes
   - Find import cycles

2. **Analyze New Code** (10 min)
   - Check files modified since last run
   - Identify new anti-patterns
   - Assess test coverage

3. **Generate Reports** (5 min)
   - Create analysis markdown
   - Catalog anti-patterns
   - Prioritize findings

4. **Create EPICs/Stories** (15 min)
   - Group related issues into EPICs
   - Create actionable stories
   - Estimate effort

5. **Update Documentation** (5 min)
   - Add to backlog
   - Update status dashboard
   - Notify stakeholders

**Total Time:** ~40 minutes per run

---

## 📁 OUTPUT STRUCTURE

```
.analysis-output/
├── runs/
│   └── 2026-03-07_03-00-00/
│       ├── COMPREHENSIVE_CODEBASE_ANALYSIS.md
│       ├── ANTIPATTERNS_CATALOG.md
│       ├── EPIC_051_*.md
│       ├── EPIC_052_*.md
│       └── STORY_*.md (10-15 files)
├── latest/ -> symlink to latest run
├── trends/
│   ├── code-quality-trend.json
│   ├── anti-patterns-trend.json
│   └── metrics-history.csv
└amed reports/
    ├── executive-summary.md
    └── technical-debt-report.md
```

---

## ✅ SUCCESS CRITERIA

- [ ] Analysis runs automatically every hour
- [ ] New anti-patterns detected within 1 hour of introduction
- [ ] EPICs created for architectural issues
- [ ] Stories created for actionable fixes
- [ ] Trend data tracked over time
- [ ] Code quality metrics improving week-over-week

---

*Framework version: 1.0*  
*Last updated: 2026-03-07*
