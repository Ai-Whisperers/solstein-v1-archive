# Solstein Audit Report — 2026-03-31

## Executive Summary

The project has **3 critical runtime bugs**, a **broken test suite** (43 files can't collect), **22 duplicate story numbers**, **4 conflicting status documents**, and a **12-week timeline that is fantasy** (realistic: 33 weeks). Several "completed" epics introduced regressions.

---

## 1. Critical Runtime Bugs

| # | Bug | Impact | Fix Time |
|---|-----|--------|----------|
| C1 | `solstein/security/jwt.py` does not exist — `auth.py:125,405,432` and `tenant/context.py:161` import it | **Every login returns HTTP 500** | 1 hour |
| C2 | `Settings` requires env vars at import time (STORY-007/008) | **43 test files can't collect** | 2 hours |
| C3 | Classification tests assert old thresholds (5.49=Lead vs actual 5.49=Salt) | **14 scoring tests fail** | 1 hour |

---

## 2. Completed Work — Verified Status

### EPIC-002: Configuration Integrity — ~90% Done
- STORY-006 ✅ Config class unified, no duplicate bodies
- STORY-007 ✅ Required fields enforced — BUT regressed tests
- STORY-008 ✅ Startup validation works — BUT regressed tests
- **Problem introduced:** Tests broken, no conftest mock provided

### EPIC-003: Core Product Correctness — ~80% Done
- STORY-009 ✅ Thresholds centralized in `analytics/constants.py`
- STORY-010 ⚠️ Scoring dedup partially done, 3 tests fail
- STORY-011 ✅ Constants named
- **Problem introduced:** Tests use old threshold values

### EPIC-004: Data Integrity — 33% Done
- STORY-012 ✅ Dual-write atomicity with outbox pattern
- STORY-013 ❌ NOT DONE — conflict resolution still open
- STORY-014 ❌ NOT DONE — hardcoded date path still exists

### EPIC-005/006: Dead Code / Duplicates — NOT STARTED
- 7 stub agents returning fake data as real intelligence
- 6 duplicate adapter pairs from incomplete migration
- `domain/models.py` still 843 lines

### Async Migration — 40% Done
- ✅ github_agent, web_search_agent, companies_house_agent migrated to httpx
- ❌ 15+ files still use sync `requests` in async code

### File Decomposition — FALSE CLAIM
- COMPREHENSIVE-ANALYSIS claims "0 files >500 lines"
- **Reality: 13 files still exceed 500 lines** (largest: 1,220 lines)

---

## 3. Backlog Structural Issues

### Duplicate Story Numbers (22 collisions)
- STORY-202–205: EPIC-053 vs EPIC-058 (different content)
- STORY-206–210: EPIC-054/055 vs EPIC-059 (different content)
- STORY-211–214: EPIC-055/056 vs EPIC-060 (different content)
- STORY-169/170: EPIC-044 vs EPIC-045 (different content)

### Four Conflicting Status Documents
| Document | EPIC-002 Status | EPICs 019-030 |
|----------|----------------|---------------|
| `backlog/README.md` | 🔴 Open | 🔴 Open |
| `EPIC_STATUS_DASHBOARD.md` | 🔴 Not Started | Not listed |
| `COMPREHENSIVE-ANALYSIS.md` | ✅ COMPLETE | ✅ ALL COMPLETE |
| `EPIC_RECONCILIATION.md` | 🔶 Partial | Not listed |

### Timeline Fantasy
- Claimed: 12 weeks for 65 epics, 255+ stories
- **23 epics not assigned to any milestone**
- **180+ stories have no milestone**
- Realistic estimate: 33 weeks (8 months)

### Epics That Should Merge (8 pairs)
- EPIC-002 + EPIC-036 (both configuration)
- EPIC-005 + EPIC-037 (both dead code)
- EPIC-006 + EPIC-032 (both adapter migration)
- EPIC-018 + EPIC-027 (both CI/CD)
- EPIC-014 + EPIC-053 (both observability)
- EPIC-033 + EPIC-060 (both export integrity)
- EPIC-003 + EPIC-046 (both scoring correctness)
- EPIC-017 + EPIC-049 (both developer experience)

---

## 4. Regressions From Completed Work

| Work Done | Regression | Severity |
|-----------|------------|----------|
| STORY-007/008 (required config fields) | 43 test files can't import | 🔴 Critical |
| STORY-009 (unified thresholds) | 14 tests assert wrong values | 🟡 High |
| STORY-010 (scoring dedup) | 3 tests fail | 🟡 High |
| Config Company ID min_length=3 | Test factories crash | 🟡 High |
| Various refactoring | `jwt.py` module deleted but still imported | 🔴 Critical |

---

## 5. What's Missing (No Stories Exist)

| Issue | Severity |
|-------|----------|
| 15 files with blocking `requests` in async code | 🔴 |
| `.env` file committed to repo | 🔴 |
| Domain imports infrastructure (hex violation) | 🟡 |
| Unbounded caches growing without limits | 🟡 |
| No database migration framework story | 🟡 |
| No backup/disaster recovery story | 🟡 |
| No load testing story | 🟡 |
| Rate limiting not wired to all endpoints | 🟡 |

---

## 6. Recommended Immediate Actions

### TIER 0: Emergency (This Week)
1. Create `solstein/security/jwt.py` with module-level wrappers
2. Fix test conftest to mock Settings
3. Fix classification test assertions
4. Fix Company ID in test factories

### TIER 1: Must Fix (Next 2 Weeks)
5. Complete requests→httpx migration (15 files)
6. Fix scoring dedup tests (3 failing)
7. Wire rate limiting to all endpoints
8. Remove or flag 7 stub agents as fake

### TIER 2: Foundation (Weeks 3-6)
9. Complete EPIC-004 (STORY-013, STORY-014)
10. Dead code elimination (EPIC-005)
11. Duplicate adapter consolidation (EPIC-006)
12. File decomposition (13 files >500 lines)

### TIER 3: New Features (Only After Above)
13. Supabase Auth (EPIC-020)
14. Multi-tenancy (EPIC-019)
15. LangGraph agents (EPIC-022)
16. pgvector search (EPIC-023)
