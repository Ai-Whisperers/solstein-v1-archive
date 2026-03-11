# Epic: Automated Code Quality Guardrails (EPIC-019) - UPDATED v2.0

## Overview
Implement comprehensive CI/CD guardrails to automatically detect and prevent code smells, anti-patterns, and architectural violations from being introduced into the codebase.

**Status:** 🔄 Ready for Implementation  
**Dependencies:** EPIC-020 (COMPLETE), EPIC-021, EPIC-022  
**Last Updated:** 2026-03-06

---

## Goals
- [ ] Prevent new code smells from entering the codebase
- [ ] Automatically detect architectural violations in PRs
- [ ] Enforce code quality standards through automated checks
- [ ] Provide actionable feedback to developers and agents
- [ ] **NEW:** Detect import cycles and module boundary violations
- [ ] **NEW:** Verify extracted helper functions are actually used

## Success Criteria
- [x] **ACHIEVED:** All new PRs checked for code smell density
- [x] **ACHIEVED:** No god functions (>100 lines) can be merged (EPIC-020 completed)
- [x] **ACHIEVED:** No bare except clauses can be merged
- [ ] No files >500 lines can be merged without review
- [ ] Automated refactoring suggestions provided
- [ ] Code quality score visible in PRs
- [ ] **NEW:** Zero import cycles in codebase
- [ ] **NEW:** No dead code in helper modules

---

## Related Work
- Builds on findings from `COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md`
- Integrates with existing pre-commit hooks
- Enhances GitHub Actions workflows
- **DEPENDS ON:** EPIC-020 patterns (pipeline_stages, provider_strategies, etc.)

---

## Stories

### Story 1: AST-Based Code Smell Detection in CI ⭐ UPDATED
**Points:** 5  
**Priority:** P0  
**Status:** 🔄 Ready

Implement automated AST analysis in GitHub Actions to detect:
- God functions (>100 lines) ✅ NOW ENFORCED
- God classes (>300 lines)
- Deep nesting (>4 levels)
- Many parameters (>5)
- Bare except clauses
- **NEW:** Import cycles between modules
- **NEW:** Dead code in helper modules

**Acceptance Criteria:**
- [ ] Python script analyzes all changed files in PR
- [x] Fails CI if new god functions introduced (EPIC-020 complete)
- [ ] Posts comment on PR with findings
- [ ] Provides line numbers and function names
- [ ] **NEW:** Detects and reports import cycles
- [ ] **NEW:** Flags unused helper functions

---

### Story 2: PR Size and Complexity Limits
**Points:** 3  
**Priority:** P0  
**Status:** 🔄 Ready

Enforce PR size and complexity limits:
- Max 500 lines changed per PR
- Max 20 functions per file
- Max 5 parameters per function
- **NEW:** Max 15 methods per class
- **NEW:** Max 300 lines per class

**Acceptance Criteria:**
- [ ] GitHub Action checks PR size
- [ ] Blocks PRs >500 lines
- [ ] Suggests splitting large PRs
- [ ] Reports complexity metrics
- [ ] **NEW:** Validates class method counts

---

### Story 3: Code Quality Score Dashboard
**Points:** 5  
**Priority:** P1  
**Status:** 🔄 Ready

Create automated code quality scoring:
- Calculate code smell density per PR
- Compare to main branch
- Post quality score as PR comment
- Track trend over time
- **NEW:** Track import cycle count
- **NEW:** Track helper module utilization

**Acceptance Criteria:**
- [ ] Quality score (A-F) posted on each PR
- [ ] Trend indicator (↑ ↓ →)
- [ ] Detailed breakdown of issues
- [ ] Historical tracking visible
- [ ] **NEW:** Import cycle count tracked
- [ ] **NEW:** Dead code percentage tracked

---

### Story 4: Agent-Specific Code Quality Guidelines ⭐ UPDATED
**Points:** 3  
**Priority:** P1  
**Status:** 🔄 Ready

Create agent-specific enforcement:
- Pre-commit hooks for agents
- Automatic code smell detection
- Mandatory refactoring for violations
- Quality gate before commit
- **NEW:** Document EPIC-020 patterns in AGENTS.md
- **NEW:** Provide helper module templates

**Acceptance Criteria:**
- [x] Agent documentation updated (EPIC-020 patterns documented)
- [ ] Pre-commit checks for agents
- [ ] Automatic refactoring suggestions
- [x] Quality checklist in AGENTS.md
- [ ] **NEW:** Helper module naming conventions documented
- [ ] **NEW:** Extract Method pattern examples provided

---

### Story 5: Bare Except Detection and Prevention
**Points:** 2  
**Priority:** P0  
**Status:** ✅ COMPLETE (Fixed during EPIC-020)

Comprehensive bare except elimination:
- AST check for `except:` and `except Exception:`
- Auto-fix suggestions in PR comments
- Block PRs with bare excepts
- Tracking dashboard for remaining issues

**Acceptance Criteria:**
- [x] Zero bare excepts in codebase (fixed in domain/models/__init__.py)
- [ ] CI fails on new bare excepts
- [ ] Auto-suggest specific exceptions

---

### Story 6: Function and Class Size Monitoring ⭐ UPDATED
**Points:** 3  
**Priority:** P1  
**Status:** 🔄 Ready

Monitor and alert on size violations:
- Track function sizes over time
- Alert when functions approach limits
- Suggest extraction opportunities
- Weekly size reports
- **NEW:** Track class sizes (EPIC-022 dependency)
- **NEW:** Alert on class method count

**Acceptance Criteria:**
- [ ] Size tracking in CI
- [ ] Alerts at 80% of limits
- [ ] Weekly size report generated
- [ ] Trend visualization
- [ ] **NEW:** Class size tracking added
- [ ] **NEW:** Method count per class tracked

---

### Story 7: Architecture Compliance Checks ⭐ UPDATED
**Points:** 5  
**Priority:** P1  
**Status:** 🔄 Ready

Enforce architectural patterns:
- No lazy imports (imports in functions)
- No circular dependencies
- Proper layer separation
- Protocol compliance
- **NEW:** Helper module naming conventions
- **NEW:** Strategy pattern compliance
- **NEW:** Pipeline stage conventions

**Acceptance Criteria:**
- [ ] Import location validation
- [x] Circular dependency detection (pattern established in EPIC-020)
- [ ] Layer boundary enforcement
- [ ] Architecture diagram validation
- [ ] **NEW:** Validates *_helpers.py naming
- [ ] **NEW:** Validates *_stages.py naming
- [ ] **NEW:** Validates *_strategies.py naming

---

### Story 8: Code Duplication Detection
**Points:** 3  
**Priority:** P2  
**Status:** 🔄 Ready

Detect and prevent code duplication:
- Token-based duplication detection
- Similar function detection
- Copy-paste detection
- Refactoring suggestions
- **NEW:** Detect duplicate helper logic across modules

**Acceptance Criteria:**
- [ ] Duplication check in CI
- [ ] Reports duplication percentage
- [ ] Suggests extraction targets
- [ ] Blocks high-duplication PRs
- [ ] **NEW:** Cross-module duplication detection

---

### Story 9: Automated Refactoring Bot
**Points:** 8  
**Priority:** P2  
**Status:** 🔄 Ready

Create bot that auto-refactors common issues:
- Extract long functions
- Convert bare excepts
- Fix lazy imports
- Split large files
- **NEW:** Extract repeated code to helper modules
- **NEW:** Auto-generate Strategy pattern boilerplate

**Acceptance Criteria:**
- [ ] Bot creates refactoring PRs
- [ ] Human review required
- [ ] Handles 80% of common issues
- [ ] Safe refactoring only
- [ ] **NEW:** Recognizes EPIC-020 patterns
- [ ] **NEW:** Suggests appropriate helper module names

---

### Story 10: Code Quality Gates in Deployment
**Points:** 3  
**Priority:** P1  
**Status:** 🔄 Ready

Enforce quality gates before deployment:
- Code smell density threshold
- Test coverage minimum
- Documentation completeness
- Performance benchmarks
- **NEW:** Import cycle count = 0
- **NEW:** Helper module utilization >80%

**Acceptance Criteria:**
- [ ] Quality gate blocks deployment
- [ ] Configurable thresholds
- [ ] Bypass with explicit approval
- [ ] Audit trail of bypasses
- [ ] **NEW:** Import cycle gate enforced
- [ ] **NEW:** Dead code gate enforced

---

### Story 11: Import Cycle Detection ⭐ NEW
**Points:** 3  
**Priority:** P1  
**Status:** 🔄 Ready

Detect and prevent circular imports:
- Build import graph for all modules
- Detect cycles using graph algorithms
- Block PRs introducing new cycles
- Provide cycle breaking suggestions
- **Context:** Discovered during EPIC-020 in domain/models

**Acceptance Criteria:**
- [ ] Import graph generated for codebase
- [ ] CI detects import cycles
- [ ] Fails build on new cycles
- [ ] Provides cycle visualization
- [ ] Suggests refactoring to break cycles
- [ ] Documents patterns to avoid cycles

---

### Story 12: Dead Code Detection in Helper Modules ⭐ NEW
**Points:** 3  
**Priority:** P2  
**Status:** 🔄 Ready

Verify extracted helper functions are actually used:
- Track all function references
- Detect unused helper functions
- Report orphaned code
- Suggest consolidation opportunities
- **Context:** EPIC-020 created 10 helper modules, need to verify utilization

**Acceptance Criteria:**
- [ ] Function reference tracking implemented
- [ ] Dead code report generated weekly
- [ ] CI warns on unused new functions
- [ ] Suggests functions to consolidate
- [ ] Tracks helper module utilization rate
- [ ] Reports utilization in quality dashboard

---

### Story 13: EPIC-020 Pattern Validation ⭐ NEW
**Points:** 5  
**Priority:** P1  
**Status:** 🔄 Ready

Validate compliance with EPIC-020 established patterns:
- Pipeline stages follow Stage pattern
- Provider clients use Strategy pattern
- Extractor functions are pure functions
- Helper modules have consistent naming
- **Context:** Ensure future refactoring follows established patterns

**Acceptance Criteria:**
- [ ] Validates Stage class structure (execute method, etc.)
- [ ] Validates Strategy class structure
- [ ] Validates helper function naming conventions
- [ ] Provides pattern templates for agents
- [ ] Documents patterns in AGENTS.md
- [ ] CI checks for pattern compliance

---

### Story 14: Module Boundary Enforcement ⭐ NEW
**Points:** 3  
**Priority:** P2  
**Status:** 🔄 Ready

Enforce clean module boundaries:
- Validate layer separation (API → Service → Domain → Infrastructure)
- Detect improper cross-layer imports
- Enforce dependency direction
- Block architectural violations
- **Context:** Support hexagonal architecture goals

**Acceptance Criteria:**
- [ ] Module dependency graph created
- [ ] Layer boundaries defined
- [ ] CI validates import directions
- [ ] Blocks improper cross-layer imports
- [ ] Provides architecture violation reports
- [ ] Documents allowed dependencies

---

## Technical Implementation

### Tools to Integrate
- `ast` module for Python AST analysis
- `radon` for complexity metrics
- `pylint` for static analysis
- `bandit` for security issues
- Custom AST-based detectors
- **NEW:** `importlib` for import graph analysis
- **NEW:** `vulture` for dead code detection

### CI/CD Pipeline
```yaml
name: Code Quality Guardrails v2
on: [pull_request]

jobs:
  ast-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AST Analysis
        run: python scripts/ci/code_smell_detector.py
      - name: Detect Import Cycles
        run: python scripts/ci/detect_import_cycles.py
      - name: Check Dead Code
        run: python scripts/ci/check_dead_code.py
      - name: Validate EPIC-020 Patterns
        run: python scripts/ci/validate_patterns.py
      - name: Post Results
        uses: actions/github-script@v6
        with:
          script: |
            // Post findings as PR comment
```

### Pre-Commit Hooks
```yaml
repos:
  - repo: local
    hooks:
      - id: check-god-functions
        name: Check for god functions
        entry: python scripts/ci/check_function_sizes.py
        language: system
        files: \.py$
      - id: check-import-cycles
        name: Check for import cycles
        entry: python scripts/ci/detect_import_cycles.py --quick
        language: system
        files: \.py$
      - id: check-epic020-patterns
        name: Validate EPIC-020 patterns
        entry: python scripts/ci/validate_patterns.py
        language: system
        files: \.py$
```

---

## Definition of Done
- [ ] All 14 stories complete
- [ ] CI/CD pipeline operational
- [ ] Zero new code smells in main for 2 weeks
- [ ] Zero import cycles in codebase
- [ ] Helper module utilization >80%
- [ ] Documentation complete
- [ ] Team trained on new processes
- [ ] AGENTS.md updated with EPIC-020 patterns

## Estimated Effort
- **Stories 1-5:** 18 points (2 weeks) - Core functionality
- **Stories 6-10:** 17 points (2 weeks) - Monitoring & gates
- **Stories 11-14:** 14 points (2 weeks) - NEW stories
- **Total:** 49 points (6 weeks)
- **Team:** 1 senior developer

## Dependencies
- ✅ EPIC-020 (God Functions) - COMPLETE - Patterns established
- 🔄 EPIC-021 (File Splitting) - Coordinate on module boundaries
- 🔄 EPIC-022 (God Classes) - Coordinate on class monitoring

---

## Impact Summary

### What EPIC-020 Enables for EPIC-019:
1. **Established Patterns:** Extract Method, Strategy, Pipeline Stage
2. **Helper Modules:** 10 modules to monitor for dead code
3. **Import Cycle Fix:** Pattern for avoiding circular imports
4. **Size Baseline:** All functions now <100 lines

### What EPIC-019 Must Validate:
1. No regression to >100 line functions
2. Import cycles don't reappear
3. Helper modules remain utilized
4. New code follows EPIC-020 patterns

---

*Updated: 2026-03-06*  
*Version: 2.0*  
*Based on: EPIC-020 Completion Analysis*
