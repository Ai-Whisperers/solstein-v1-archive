# M0 Emergency — Pre-Production

**Goal:** Make the system runnable and fix the critical bugs before building anything new features.

**Must complete before any other work.**

**Duration:** 1 week (1 sprint +2 hours)

## Stories

All stories must be done in 1 hour each.

### T0.1: Fix jwt module (C1)

- Create `solstein/security/jwt.py` with `verify_token()` and `create_token()` module-level functions wrappers
- Update conftest to mock Settings so tests can import without env vars
- Update test factories to use 3+ char IDs

- Fix auth bypass (STORY-002→005 replacement)

### T0.2: Fix test infrastructure (STORY-007/008 regression)
- Create `tests/conftest.py` that provides Settings override
- Fix Company model test factories (min_length=3)
- Fix growth score range test expectations (3 tests)
- Remove `_=5.3.0` artifact from repo root

 Add `.gitignore for patterns for Remove `__pycache__` dirs from .gitignore
- Remove pytest.ini (merge into pyproject.toml)
- Remove `requirements.txt` (only has 1 dependency)
- Remove duplicate config directories (`src/solstein/config/` and top-level `config/`)

## Critical Security Fixes (STORY-067/070)
- Wire rate limiting to all endpoints (STORY-070)
- Remove hardcoded secrets from .env.example (STORY-007 partial)
- Replace fake health checks with real dependency checks (STORY-047)

## Triage 1: Must FIX (Week 1-2)
- Complete requests→httpx migration (15 files) (STORY-133-136)
- Fix failing scoring tests (6 tests)
- Remove/flag 7 stub agents returning fake data (STORY-017)
- Eliminate duplicate adapters pairs (STORY-019/124)

## T0.2: SAFE TO BUILD ON (Week 3-5, after T0-1)
- Complete EPIC-004 remaining stories (STORY-013/014)
- Dead code elimination (EPIC-005/037)
- Decompose 13 files >500 lines (EPIC-008)
- Merge duplicate route directories (EPIC-006/022)
- Consolidate loader systems (EPIC-006/020)

## T0.3: NEW FEATURES (Week 5-8)
- EPIC-020: Supabase Auth (requires C1)
- EPIC-019: Multi-tenancy (requires C1,2)
- EPIC-023: pgvector (requires M2-M4)
- EPIC-022: LangGraph agents (requires M3-M4)

## NOT DOING (Defer or Remove)
| Epic | Action | Reason |
|------|--------|--------|
| EPIC-016 CQRS | Premature optimization | codebase needs basic correctness first |
| EPIC-040 Multi-Market | No customers yet |
| EPIC-041 Equity Model | Business speculation |
| EPIC-042 Rapid Validation | No product-market fit |

## Dependencies

```
M0 → M1 → M2 → M3 → M4 → M5 → M6
