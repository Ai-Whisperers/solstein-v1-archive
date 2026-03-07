# EPIC-032: Repository Cleanup and Hygiene

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 21  
**Sprint Allocation:** 1 sprint  
**Target Date:** Week 2

---

## Problem Statement

The repository contains build artifacts and has hygiene issues:
- 54 `__pycache__` directories in src/
- 849 `.pyc` files in src/
- `.env` file committed (security risk)
- 12 files still >500 lines (violating code quality standards)
- No .gitignore for common artifacts

### Impact
- Repository bloat (slower clones)
- Security risk (.env with credentials)
- Code quality violations
- CI/CD pollution

---

## Success Criteria

1. ✅ Zero build artifacts in repository
2. ✅ .env file removed and secured
3. ✅ All files <500 lines
4. ✅ Proper .gitignore for all artifacts
5. ✅ Pre-commit hooks enforce standards

---

## Stories

### Story 2.1: Clean Build Artifacts (3 pts)
**Task:** Remove all __pycache__ and .pyc files

**Acceptance Criteria:**
- [ ] All `__pycache__` directories removed from git
- [ ] All `.pyc` files removed from git
- [ ] .gitignore updated to prevent future commits
- [ ] CI/CD cache strategy documented

**Implementation:**
```bash
# Remove from git but keep locally
git rm -r --cached src/**/__pycache__
git rm --cached src/**/*.pyc

# Update .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo ".pytest_cache/" >> .gitignore
```

---

### Story 2.2: Secure Environment Files (5 pts)
**Task:** Remove .env from repository and secure credentials

**Acceptance Criteria:**
- [ ] .env file removed from git history
- [ ] .env.example created (template)
- [ ] All credentials rotated (assume compromised)
- [ ] Documentation updated
- [ ] Team notified of credential rotation

**Implementation:**
```bash
# Remove from git history (requires force push)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Create template
cp .env .env.example
# Remove all real values from .env.example
```

**Security Note:** All credentials in the committed .env must be considered compromised and rotated immediately.

---

### Story 2.3: Split Large Files (8 pts)
**Task:** Split remaining files >500 lines

**Files to Split:**
1. `analytics/scorers/models.py` - 817 lines
2. `infrastructure/database_models.py` - 513 lines
3. `research/aggregate.py` - 663 lines
4. `research/pipeline_stages.py` - 575 lines
5. `agents/ai_research_orchestrator.py` - 542 lines

**Acceptance Criteria:**
- [ ] All files <500 lines
- [ ] No functionality lost
- [ ] Tests updated
- [ ] Imports work correctly

**Implementation Pattern:**
```python
# Before: models.py (817 lines)
# After:
# - models/base.py
# - models/company.py
# - models/financial.py
# - models/scoring.py
# - models/__init__.py (exports all)
```

---

### Story 2.4: Update .gitignore (2 pts)
**Task:** Comprehensive .gitignore for all artifacts

**Acceptance Criteria:**
- [ ] Python artifacts ignored
- [ ] IDE files ignored
- [ ] OS files ignored
- [ ] Test artifacts ignored
- [ ] Documentation artifacts ignored

**Implementation:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment
.env
.env.local
.env.*.local

# Documentation
docs/_build/
site/

# Logs
*.log
logs/
```

---

### Story 2.5: Pre-commit Hooks (3 pts)
**Task:** Install pre-commit hooks to prevent future issues

**Acceptance Criteria:**
- [ ] Pre-commit framework installed
- [ ] Black formatting hook
- [ ] Ruff linting hook
- [ ] Large file check hook
- [ ] Secret detection hook
- [ ] All team members install hooks

**Implementation:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: no-commit-to-branch
        args: ['--branch', 'main']
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
```

---

## Definition of Done

- [ ] Zero `__pycache__` directories in git
- [ ] Zero `.pyc` files in git
- [ ] .env file removed from history
- [ ] All credentials rotated
- [ ] All files <500 lines
- [ ] .gitignore comprehensive
- [ ] Pre-commit hooks installed
- [ ] CI/CD pipeline green

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking imports when splitting | Medium | High | Careful refactoring, tests |
| Credential rotation disruption | Medium | Medium | Coordinate with team |
| Force push complications | Low | High | Backup first, notify team |

---

## Resources

- **Developers:** 1-2 backend engineers
- **Time:** 1 week
- **Dependencies:** EPIC-031 (tests should pass first)

---

*Epic created as part of Comprehensive Analysis*
