# Solstein Health Report — April 1, 2026

## Executive Summary

18 open PRs, 66 open issues, 11 test collection errors from ONE root cause,
13 security vulnerabilities, ALL CI workflows failing, no branch protection.
The good news: all PRs merge cleanly, the root cause is a single import fix,
and the backlog is well-organized.

---

## 1. CRITICAL — Fix Immediately

### 1A. AuthenticationMiddleware Import Error (blocks ALL tests)

**Root cause:** `src/solstein/api/middleware/__init__.py` line 17 imports
`AuthenticationMiddleware` from `security.py`, but it was renamed to
`SupabaseJWTMiddleware` (STORY-068). The `__init__.py` was never updated.

**Impact:** 11 test files fail to collect. ANY test that imports `from solstein.api.main import app` crashes.

**Fix (one line):**
```python
# In src/solstein/api/middleware/__init__.py, line 16-18:
# CHANGE:
from .security import (
    AuthenticationMiddleware,        # ← this name doesn't exist anymore
    setup_security_middleware,
)
# TO:
from .security import (
    SupabaseJWTMiddleware as AuthenticationMiddleware,  # backward compat
    setup_security_middleware,
)
```

**Affected test files (11):**
- test_cors.py
- test_security_comprehensive.py
- test_stale_docs.py
- test_story079_checkpointing.py
- test_api_base_coverage.py
- test_api_middleware_exceptions_coverage.py
- test_api_routers_coverage.py
- test_docs_health_dashboard.py
- test_docs_quality_gate.py
- adapters/test_news_funding_async.py
- agents/test_ch_website_async.py

### 1B. Missing __init__.py Files

7 REAL packages missing `__init__.py` (ignoring __pycache__):
- `src/solstein/domain/__init__.py`
- `src/solstein/tenant/__init__.py`
- `src/solstein/analytics/__init__.py`
- `src/solstein/data/__init__.py`
- `src/solstein/monitoring/__init__.py`
- `src/solstein/intelligence/__init__.py`
- `src/solstein/application/__init__.py`
- `src/solstein/extractors/__init__.py`
- `src/solstein/config/__init__.py`
- `src/solstein/utils/__init__.py`
- `src/solstein/data/financial_loaders/__init__.py`
- `src/solstein/infrastructure/connectors/__init__.py`
- `src/solstein/application/analytics/__init__.py`
- `src/solstein/application/analytics/filters/__init__.py`
- `src/solstein/application/exporters/__init__.py`
- `src/solstein/application/services/__init__.py`
- `src/solstein/api/schemas/__init__.py`
- `src/solstein/migrations/__init__.py`

---

## 2. OPEN PRs — 18 Total

All PRs merge cleanly against develop (no conflicts). Grouped by priority:

### Already Merged in develop (can close):
- **PR #204** fix(CI): resolve failing workflows — ALREADY MERGED

### Audit Hotfixes (merge first):
| PR | Story | Title | Files | Status |
|----|-------|-------|-------|--------|
| #217 | STORY-254 | Remove test collection side effects | 10 | ✓ Clean |
| #218 | STORY-253 | Behavioral contract tests | 5 | ✓ Clean |
| #219 | STORY-250 | Reconcile export schema | 4 | ✓ Clean |
| #220 | STORY-251 | Enforce strict boundary schemas | 2 | ✓ Clean |
| #222 | STORY-252 | Tighten LLM contracts | 2 | ✓ Clean |
| #223 | STORY-255 | Freeze graph runtime | 5 | ✓ Clean |

### EPIC-067 Consolidation:
| PR | Story | Title | Files |
|----|-------|-------|-------|
| #216 | STORY-264 | Remove replaceable providers | 35 |

### EPIC-031 Shared Library:
| PR | Story | Title | Files |
|----|-------|-------|-------|
| #225 | STORY-116 | Centralize retry/backoff | 3 |
| #226 | STORY-117 | Introduce shared/ package | 7 |
| #227 | STORY-118 | Formalize CLI entrypoint | 15 |
| #228 | STORY-119 | Verify unified_loader split | 1 |
| #229 | STORY-120 | UTC timezone policy | 49 ← LARGE |

### EPIC-067 Runtime Hardening:
| PR | Story | Title | Files |
|----|-------|-------|-------|
| #230 | STORY-257 | Repair legacy entrypoints | 12 |
| #231 | STORY-267 | Provider-level golden contract runs | 11 |
| #232 | STORY-268 | Full-market golden run | 15 |
| #233 | STORY-269 | Block empty/placeholder/mock paths | 14 |

### Documentation:
| PR | Story | Title | Files |
|----|-------|-------|-------|
| #224 | STORY-245 | Expand generated API docs | 18 ← 13,698 additions |

### Recommended Merge Order:
1. Close PR #204 (already in develop)
2. Merge #217, #218, #219, #220, #222, #223 (audit hotfixes)
3. Merge #225, #226, #227, #228 (shared library — ordered deps)
4. Merge #229 (UTC policy — large, review carefully)
5. Merge #216, #230, #231, #232, #233 (runtime hardening)
6. Merge #224 (docs — harmless, large)

---

## 3. OPEN ISSUES — 66 Total

| Phase | Count | Examples |
|-------|-------|---------|
| P0 (Emergency) | 16 | Export schema validation, scoring determinism, data loading correctness |
| P1 (Foundation) | 16 | API hardening, security ops, release pipeline, dependency governance |
| P2 (Data) | 16 | Search & retrieval, rate limiting, backup/DR, data retention |
| P3 (Business) | 16 | Frontend dashboard, domain expansion, operations excellence |
| Epic-level | 16 | Tracking issues for EPIC-1 through EPIC-16 |
| Auto/test | 2 | Automated issue creation test (can close) |

### Issues to Close (garbage):
- **#67** [Backlog Auto] [AUTO] Test automated issue creation — test issue, close it
- **#69** [Backlog Auto] Test automated issue creation — test issue, close it

### Issues vs Backlog Duplication:
The 64 roadmap issues (#3-#66) duplicate the backlog/ EPICS and QUEUE.md.
Consider: either use GitHub Issues OR backlog/QUEUE.md as source of truth, not both.
Currently the cron jobs use QUEUE.md, so the GitHub issues are informational.

---

## 4. CI/CD — ALL FAILING

Every CI workflow is failing on develop:

| Workflow | Status | Likely Cause |
|----------|--------|-------------|
| CI Pipeline | ✗ | AuthenticationMiddleware import error |
| Code Quality Guardrails v2 | ✗ | Same import chain |
| Pre-commit Checks | ✗ | Same import chain |
| Security Scan | ✗ | Trivy action compromised (Dependabot alert) |
| DB Migrations | ✗ | No database configured in CI |
| Chaos Engineering | ✗ | No infrastructure in CI |
| Load Testing | ✗ | No infrastructure in CI |
| Generated Docs Freshness | ✗ | Stale generated docs |
| Integration Tests | ✗ | No database in CI |

**Fix priority:**
1. Fix AuthenticationMiddleware import → fixes CI Pipeline, Quality Guardrails, Pre-commit
2. Update trivy-action to non-compromised version → fixes Security Scan
3. DB Migrations, Chaos, Load Testing are INFRASTRUCTURE tests — they need Docker services in CI (lower priority)

---

## 5. SECURITY — 13 Dependabot Alerts

| Severity | Package | Issue |
|----------|---------|-------|
| 🔴 CRITICAL | aquasecurity/trivy-action (x2) | Supply chain compromised |
| 🟠 HIGH | langchain-core (x2) | Path traversal in legacy load() |
| 🟠 HIGH | PyJWT (x2) | Accepts unknown crit header extensions |
| 🟠 HIGH | black (x1) | Arbitrary file writes from user input |
| 🟡 MEDIUM | requests (x2) | Insecure temp file reuse |
| ⚪ LOW | Pygments (x2) | ReDoS vulnerability |
| ⚪ LOW | cryptography (x2) | Incomplete DNS constraint enforcement |

**Fixes:**
1. trivy-action: Update to latest in `.github/workflows/security.yml`
2. langchain-core: Update to >=0.3.x in pyproject.toml
3. PyJWT: Update to >=2.10 in pyproject.toml
4. black: Update to latest (or switch to ruff format, which is already used)
5. requests: Part of EPIC httpx migration (replace requests entirely)

---

## 6. CODE QUALITY

| Metric | Value | Status |
|--------|-------|--------|
| Lint errors | 1 (UP037 quoted-annotation) | 🟢 Good |
| TODO/FIXME/HACK/XXX | 3 | 🟢 Good |
| Bare except: clauses | 2 | 🟡 Fix |
| God files (>300 lines) | 14 | 🟠 Needs decomposition |
| Missing __init__.py (real packages) | 18 | 🔴 Fix immediately |
| Test collection errors | 11 | 🔴 Fix immediately (one root cause) |

### God Files (top 5):
| File | Lines | Module |
|------|-------|--------|
| domain/models.py | 1,158 | Domain models |
| intelligence/deep_analyzer.py | 811 | Deep analysis |
| research/aggregate.py | 663 | Data aggregation |
| analytics/scoring.py | 617 | Scoring engine |
| data/provenance.py | 584 | Data provenance |

---

## 7. BRANCH PROTECTION

⚠️ **develop has NO branch protection rules.**

This means anyone (including Hermes cron jobs) can push directly to develop
without PR review. Recommended:
- Require PR reviews before merge
- Require status checks to pass
- Require branches to be up to date

---

## 8. RECOMMENDED IMMEDIATE ACTIONS

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | Fix AuthenticationMiddleware import in middleware/__init__.py | 5 min | Unblocks 11 tests + CI |
| 2 | Create missing __init__.py files (18 packages) | 10 min | Fixes import chains |
| 3 | Close PR #204 (already merged) | 1 min | Cleanup |
| 4 | Close issues #67, #69 (test issues) | 1 min | Cleanup |
| 5 | Update trivy-action in security.yml | 5 min | Fixes security scan CI |
| 6 | Update langchain-core, PyJWT in pyproject.toml | 10 min | Fixes 5 Dependabot alerts |
| 7 | Merge audit hotfix PRs (#217-#223) | 30 min | 6 stories completed |
| 8 | Set up branch protection on develop | 10 min | Safety |

Total: ~1 hour of work to clear the critical path.
