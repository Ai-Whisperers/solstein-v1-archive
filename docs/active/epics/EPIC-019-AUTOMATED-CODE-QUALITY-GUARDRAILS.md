# Epic: Automated Code Quality Guardrails (EPIC-019)

## Overview
Implement comprehensive CI/CD guardrails to automatically detect and prevent code smells, anti-patterns, and architectural violations from being introduced into the codebase.

## Goals
- Prevent new code smells from entering the codebase
- Automatically detect architectural violations in PRs
- Enforce code quality standards through automated checks
- Provide actionable feedback to developers and agents

## Success Criteria
- [ ] All new PRs checked for code smell density
- [ ] No god functions (>100 lines) can be merged
- [ ] No bare except clauses can be merged
- [ ] No files >500 lines can be merged without review
- [ ] Automated refactoring suggestions provided
- [ ] Code quality score visible in PRs

## Related Work
- Builds on findings from `COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md`
- Integrates with existing pre-commit hooks
- Enhances GitHub Actions workflows

---

## Stories

### Story 1: AST-Based Code Smell Detection in CI
**Points:** 5
**Priority:** P0

Implement automated AST analysis in GitHub Actions to detect:
- God functions (>100 lines)
- God classes (>300 lines)
- Deep nesting (>4 levels)
- Many parameters (>5)
- Bare except clauses

**Acceptance Criteria:**
- [ ] Python script analyzes all changed files in PR
- [ ] Fails CI if new god functions introduced
- [ ] Posts comment on PR with findings
- [ ] Provides line numbers and function names

### Story 2: PR Size and Complexity Limits
**Points:** 3
**Priority:** P0

Enforce PR size and complexity limits:
- Max 500 lines changed per PR
- Max 20 functions per file
- Max 5 parameters per function

**Acceptance Criteria:**
- [ ] GitHub Action checks PR size
- [ ] Blocks PRs >500 lines
- [ ] Suggests splitting large PRs
- [ ] Reports complexity metrics

### Story 3: Code Quality Score Dashboard
**Points:** 5
**Priority:** P1

Create automated code quality scoring:
- Calculate code smell density per PR
- Compare to main branch
- Post quality score as PR comment
- Track trend over time

**Acceptance Criteria:**
- [ ] Quality score (A-F) posted on each PR
- [ ] Trend indicator (↑ ↓ →)
- [ ] Detailed breakdown of issues
- [ ] Historical tracking visible

### Story 4: Agent-Specific Code Quality Guidelines
**Points:** 3
**Priority:** P1

Create agent-specific enforcement:
- Pre-commit hooks for agents
- Automatic code smell detection
- Mandatory refactoring for violations
- Quality gate before commit

**Acceptance Criteria:**
- [ ] Agent documentation updated
- [ ] Pre-commit checks for agents
- [ ] Automatic refactoring suggestions
- [ ] Quality checklist in AGENTS.md

### Story 5: Bare Except Detection and Prevention
**Points:** 2
**Priority:** P0

Comprehensive bare except elimination:
- AST check for `except:` and `except Exception:`
- Auto-fix suggestions in PR comments
- Block PRs with bare excepts
- Tracking dashboard for remaining issues

**Acceptance Criteria:**
- [ ] Zero bare excepts in codebase
- [ ] CI fails on new bare excepts
- [ ] Auto-suggest specific exceptions

### Story 6: Function and Class Size Monitoring
**Points:** 3
**Priority:** P1

Monitor and alert on size violations:
- Track function sizes over time
- Alert when functions approach limits
- Suggest extraction opportunities
- Weekly size reports

**Acceptance Criteria:**
- [ ] Size tracking in CI
- [ ] Alerts at 80% of limits
- [ ] Weekly size report generated
- [ ] Trend visualization

### Story 7: Architecture Compliance Checks
**Points:** 5
**Priority:** P1

Enforce architectural patterns:
- No lazy imports (imports in functions)
- No circular dependencies
- Proper layer separation
- Protocol compliance

**Acceptance Criteria:**
- [ ] Import location validation
- [ ] Circular dependency detection
- [ ] Layer boundary enforcement
- [ ] Architecture diagram validation

### Story 8: Code Duplication Detection
**Points:** 3
**Priority:** P2

Detect and prevent code duplication:
- Token-based duplication detection
- Similar function detection
- Copy-paste detection
- Refactoring suggestions

**Acceptance Criteria:**
- [ ] Duplication check in CI
- [ ] Reports duplication percentage
- [ ] Suggests extraction targets
- [ ] Blocks high-duplication PRs

### Story 9: Automated Refactoring Bot
**Points:** 8
**Priority:** P2

Create bot that auto-refactors common issues:
- Extract long functions
- Convert bare excepts
- Fix lazy imports
- Split large files

**Acceptance Criteria:**
- [ ] Bot creates refactoring PRs
- [ ] Human review required
- [ ] Handles 80% of common issues
- [ ] Safe refactoring only

### Story 10: Code Quality Gates in Deployment
**Points:** 3
**Priority:** P1

Enforce quality gates before deployment:
- Code smell density threshold
- Test coverage minimum
- Documentation completeness
- Performance benchmarks

**Acceptance Criteria:**
- [ ] Quality gate blocks deployment
- [ ] Configurable thresholds
- [ ] Bypass with explicit approval
- [ ] Audit trail of bypasses

---

## Technical Implementation

### Tools to Integrate
- `ast` module for Python AST analysis
- `radon` for complexity metrics
- `pylint` for static analysis
- `bandit` for security issues
- Custom AST-based detectors

### CI/CD Pipeline
```yaml
name: Code Quality Guardrails
on: [pull_request]

jobs:
  ast-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AST Analysis
        run: python scripts/ci/code_smell_detector.py
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
```

---

## Definition of Done
- [ ] All 10 stories complete
- [ ] CI/CD pipeline operational
- [ ] Zero new code smells in main for 2 weeks
- [ ] Documentation complete
- [ ] Team trained on new processes

## Estimated Effort
- **Total Points:** 40
- **Duration:** 4-6 weeks
- **Team:** 1 senior + 1 junior developer

## Dependencies
- EPIC-018 (Observability) - For metrics
- EPIC-016 (Security) - For security gates

---

*Created: 2026-03-06*  
*Based on: COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md*
