# STORY-137: Centralize All Environment Variables in config.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-002 (Configuration Integrity) |

---

## The Audit Verdict

> 12+ env vars used but NOT in `config.py`: `DATABASE_URL_TEST`, `DATABASE_URL_DEV`, `DATABASE_URL_PROD`, `SEC_EDGAR_TIMEOUT`, `COMPANIES_HOUSE_TIMEOUT`, `NEWS_API_TIMEOUT`, `MAX_RETRIES`, `ENRICHMENT_BATCH_SIZE`, `ENRICHMENT_ENABLED`, `NEWSAPI_KEY`.

---

## Problem Statement

The configuration is a scavenger hunt. Environment variables are defined where they're used, not where they're documented. A developer trying to understand what settings exist must grep the entire codebase — and even then, they'll miss the ones buried in shell scripts and service files. The audit found 12 variables in active use that do not appear anywhere in `config.py`. They are invisible to anyone who reads the configuration module expecting it to be authoritative.

Worse, the naming is inconsistent. `NEWS_API_KEY` and `NEWSAPI_KEY` both exist. One is presumably canonical; neither is documented as such. A developer setting up the system must guess which one the code actually reads. If they guess wrong, the news adapter silently fails — because the error handling is also inadequate, but that is a different story.

The fix is a single source of truth: all environment variables defined in `config.py` using Pydantic Settings, with validation, type annotations, default values, and inline documentation. No variable should be read from the environment anywhere else in the codebase. If it's not in `config.py`, it doesn't exist.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Configuration scattered across 20+ files; no single place to understand what the system requires |
| **Operational** | No visibility into required settings; missing variables discovered at runtime, not startup |
| **Developer Experience** | Onboarding requires code archaeology; new developers cannot know what to configure without reading every file |
| **Reliability** | Duplicate variable names create silent misconfiguration; wrong key name = silent failure |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/config.py` | Missing 12+ environment variables; not the authoritative source it claims to be |
| `src/solstein/infrastructure/adapters/github_adapter.py` | Reads `GITHUB_TOKEN` directly via `os.environ.get()` |
| `src/solstein/infrastructure/adapters/news_adapter.py` | Reads `NEWSAPI_KEY` directly; conflicts with `NEWS_API_KEY` |
| `src/solstein/infrastructure/adapters/sec_edgar_adapter.py` | Reads `SEC_EDGAR_TIMEOUT` directly |
| `src/solstein/infrastructure/adapters/companies_house_adapter.py` | Reads `COMPANIES_HOUSE_TIMEOUT` directly |
| `src/solstein/worker.py` | Reads `ENRICHMENT_BATCH_SIZE`, `ENRICHMENT_ENABLED` directly |
| `src/solstein/infrastructure/database/` | Reads `DATABASE_URL_TEST`, `DATABASE_URL_DEV`, `DATABASE_URL_PROD` directly |
| `scripts/` | Various shell scripts reading env vars not in config.py |

---

## Architectural Requirements

- All environment variables moved to `config.py` as fields on the Pydantic Settings class
- Pydantic Settings class with field-level validation for each variable (type, range, format where applicable)
- Settings grouped by concern using nested models or comment sections: Database, External APIs, LLM Providers, Celery, Feature Flags
- Default values provided where a sensible default exists; `Required` (no default) where the variable is mandatory
- Type annotations for all settings fields — no `str` where `int` or `bool` is appropriate
- Inline docstring for each setting field explaining: what it controls, what happens if absent, and where to obtain the value
- Canonical name established for all duplicate variables; deprecated alias documented with migration note
- All call sites updated to read from the settings object, not from `os.environ.get()` directly
- Startup validation: Pydantic raises `ValidationError` on startup if required variables are absent or invalid
- No `os.environ.get()` calls permitted outside `config.py`

---

## Acceptance Criteria

- [ ] All environment variables in active use are defined as fields in `config.py`
- [ ] Pydantic `ValidationError` is raised at startup if any required variable is missing
- [ ] `grep -r 'os.environ.get' src/` returns zero results
- [ ] `grep -r 'os.environ\[' src/` returns zero results
- [ ] Duplicate variable names resolved: one canonical name, deprecated alias removed or aliased with deprecation warning
- [ ] Every settings field has an inline docstring explaining its purpose
- [ ] Settings are grouped by concern (Database, APIs, LLM, Celery, Feature Flags)
- [ ] All call sites updated to use `settings.<field>` instead of `os.environ.get()`

---

## Definition of Done

- **Tests Required**: Unit test that instantiating `Settings` with a missing required variable raises `ValidationError`. Unit test that duplicate variable names resolve to the canonical name. Integration smoke test that the application starts successfully with a complete `.env`.
- **Documentation Required**: Inline docstrings on every settings field. Comment headers for each settings group. Update developer setup guide to reference `config.py` as the authoritative settings reference.
- **Code Review Gate**: Reviewer runs `grep -r 'os.environ' src/` and confirms zero results. Reviewer verifies every field has a docstring. Reviewer confirms no field uses `Any` as its type annotation.

---

## Notes

The Pydantic Settings class is already in use in `config.py` — this story extends it, not replaces it. The work is additive: add the missing fields, add the missing docstrings, add the missing validation, and remove the scattered `os.environ.get()` calls.

The duplicate `NEWS_API_KEY` / `NEWSAPI_KEY` situation requires a decision on canonical naming before implementation begins. The canonical name should be `NEWS_API_KEY` (consistent with the `_API_KEY` suffix pattern used by other providers). `NEWSAPI_KEY` should be treated as a deprecated alias during a transition period, then removed.

This story is a prerequisite for STORY-140 (Fix .env.example). The `.env.example` cannot be accurate until `config.py` is complete.
