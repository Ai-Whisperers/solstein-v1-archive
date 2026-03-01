# STORY-137: Centralize All Environment Variables in config.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> 12+ env vars used but NOT in config.py: DATABASE_URL_TEST, DATABASE_URL_DEV, DATABASE_URL_PROD, SEC_EDGAR_TIMEOUT, COMPANIES_HOUSE_TIMEOUT, NEWS_API_TIMEOUT, MAX_RETRIES, ENRICHMENT_BATCH_SIZE, ENRICHMENT_ENABLED, NEWSAPI_KEY.

## Problem Statement

The configuration is a scavenger hunt. Environment variables are defined where they're used, not where they're documented. A developer trying to understand what settings exist must grep the entire codebase. Worse, some variables have similar names (NEWS_API_KEY vs NEWSAPI_KEY) creating confusion about which is canonical. The fix is a single source of truth: all environment variables defined in config.py with validation, defaults, and documentation.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Config scattered across 20+ files |
| **Operational** | No visibility into required settings |
| **Developer Experience** | Onboarding requires code archaeology |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/config.py` | Missing many env vars |
| All files with os.environ.get() | Scattered config |

## Architectural Requirements

- All environment variables moved to config.py
- Pydantic Settings class with validation for each variable
- Grouped by concern: Database, External APIs, LLM, Celery, Feature Flags
- Default values where appropriate, required markers where not
- Type annotations for all settings
- Documentation: docstring for each setting explaining purpose
- Deprecation: variables with duplicate names (NEWSAPI_KEY) marked deprecated, canonical name established

## Acceptance Criteria

- [ ] All env vars defined in config.py
- [ ] Validation errors on startup for missing required vars
- [ ] No os.environ.get() outside config.py
- [ ] Duplicate names resolved (single canonical name)
- [ ] Documentation for each setting

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: Config documentation
- **Code Review Gate**: grep for os.environ outside config.py returns zero results

## Notes

Single source of truth for configuration.
