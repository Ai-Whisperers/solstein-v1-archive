# EPIC-036: Configuration Consolidation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-002 (Configuration Integrity) |
| **Stories** | STORY-137, STORY-138, STORY-139, STORY-140 |

---

## Executive Summary

The forensic audit found a configuration system that is, charitably, distributed. Less charitably, it is a scavenger hunt spread across 20+ files with no central authority, no validation, and no documentation. Environment variables are defined where they happen to be used. Paths are hardcoded to a specific developer's home directory. Timeouts are magic numbers chosen, apparently, by intuition. The `.env.example` file — the canonical onboarding document — is missing the variable required for startup.

This epic consolidates all configuration into a single, validated, documented source of truth.

---

## Audit Findings

| Category | Count | Severity |
|----------|-------|----------|
| Hardcoded absolute paths (`/home/ai-whisperers/`) | 15+ | Critical |
| Environment variables NOT in `config.py` | 12+ | High |
| Magic numbers (timeouts, thresholds, limits) | 40+ | High |
| Hardcoded external URLs | 25+ | Medium |
| Missing variables in `.env.example` | 15+ | High |

### Missing from `.env.example` (Partial List)

The following variables are **required at runtime** but undocumented in `.env.example`:

- `GITHUB_TOKEN` — required for startup; absence causes immediate failure
- `COMPANIES_HOUSE_API_KEY`
- `GOOGLE_API_KEY`
- `EXA_API_KEY`
- `GROQ_API_KEY`
- `FIREWORKS_API_KEY`
- `MISTRAL_API_KEY`
- `DEEPINFRA_API_KEY`
- `GEMINI_API_KEY`
- `NVIDIA_API_KEY`
- `CEREBRAS_API_KEY`
- `KIMI_API_KEY`
- `OLLAMA_URL`
- `OLLAMA_MODEL`

A new developer following the documented setup process will have a non-functional system. This is not a minor inconvenience — it is a broken onboarding experience that erodes trust in the codebase before a single line of business logic is touched.

### Hardcoded Paths (Partial List)

- `/home/ai-whisperers/solstein` — project root, hardcoded
- `/home/ai-whisperers/.linuxbrew/bin/python3` — Python interpreter, hardcoded
- `/tmp/solstein-cycle-counter` — temp file, non-portable
- `/home/ai-whisperers/solstein/.cache` — cache directory, hardcoded

These paths work on exactly one machine. They do not work in CI, staging, production, or on any other developer's workstation.

### Environment Variables Outside `config.py` (Partial List)

- `DATABASE_URL_TEST`, `DATABASE_URL_DEV`, `DATABASE_URL_PROD`
- `SEC_EDGAR_TIMEOUT`, `COMPANIES_HOUSE_TIMEOUT`, `NEWS_API_TIMEOUT`
- `MAX_RETRIES`, `ENRICHMENT_BATCH_SIZE`, `ENRICHMENT_ENABLED`
- `NEWSAPI_KEY` (conflicts with `NEWS_API_KEY` — canonical name unclear)

### Magic Numbers (Sample)

- Timeouts: `10`, `15`, `20`, `30` seconds — scattered across 8+ adapter files
- Circuit breaker `failure_threshold`: `3`, `4`, `5` — varies by file
- Circuit breaker `recovery_timeout`: `45`, `60`, `90` — varies by file
- Celery `task_time_limit`: `30` — hardcoded in task definitions

---

## Problem Statement

Configuration management is the foundation of a deployable system. When configuration is scattered, undocumented, and hardcoded, every deployment is a debugging exercise. Every new developer is a detective. Every production incident involving a misconfigured timeout requires a code change, a review, and a deployment.

The current state is the result of incremental development without a configuration discipline. Each feature added its own environment variables where it needed them. Each adapter hardcoded its own timeouts. The `.env.example` was never kept in sync with reality. The result is a system that is difficult to configure, impossible to document accurately, and fragile under operational pressure.

This epic establishes the discipline that should have existed from the start: a single `config.py` as the authoritative source of all configuration, validated at startup, documented inline, and reflected accurately in `.env.example`.

---

## Goals

1. **Single source of truth**: All environment variables defined and validated in `config.py`
2. **Portability**: No hardcoded paths; all paths derived dynamically or from environment
3. **Configurability**: All timeouts, thresholds, and limits overridable via environment variables
4. **Accuracy**: `.env.example` reflects every variable required to run the system
5. **Enforcement**: CI checks prevent regression to the current state

---

## Non-Goals

- Migrating to a secrets management system (out of scope for this epic)
- Changing the configuration format (Pydantic Settings is already in use)
- Refactoring the LLM provider selection logic (separate concern)

---

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-137](STORIES/STORY-137-centralize-env-vars.md) | Centralize All Environment Variables in config.py | P2 | 🔴 Not Started |
| [STORY-138](STORIES/STORY-138-config-driven-paths.md) | Replace Hardcoded Paths with Config-Driven Paths | P2 | 🔴 Not Started |
| [STORY-139](STORIES/STORY-139-centralize-timeouts.md) | Centralize Timeouts and Magic Numbers | P2 | 🔴 Not Started |
| [STORY-140](STORIES/STORY-140-fix-env-example.md) | Fix .env.example with All Required Variables | P2 | 🔴 Not Started |

---

## Recommended Execution Order

1. **STORY-137** first — establishes the config.py structure that all other stories depend on
2. **STORY-138** second — path consolidation can reference the new config structure
3. **STORY-139** third — timeout consolidation populates the config structure established in 137
4. **STORY-140** last — `.env.example` is generated from the completed config.py

STORY-137 is a hard prerequisite for STORY-140. STORY-138 and STORY-139 can proceed in parallel after STORY-137 is complete.

---

## Impact Assessment

| Dimension | Current State | Target State |
|-----------|--------------|--------------|
| **Onboarding time** | Hours of archaeology | Follow `.env.example`, start system |
| **Configuration visibility** | Grep the entire codebase | Read `config.py` |
| **Portability** | One developer's machine | Any environment |
| **Operational tuning** | Code change + deploy | Environment variable update |
| **Startup validation** | Silent failures at runtime | Explicit error at startup |
| **CI enforcement** | None | Automated checks block regression |

---

## Definition of Done (Epic Level)

- [ ] All environment variables defined in `config.py` with validation and docstrings
- [ ] Zero occurrences of `os.environ.get()` outside `config.py`
- [ ] Zero occurrences of `/home/ai-whisperers/` in source files
- [ ] Zero magic timeout numbers in adapter files
- [ ] `.env.example` matches `config.py` (validated by CI script)
- [ ] New developer can follow `.env.example` and start the system without additional research
- [ ] CI pipeline enforces all of the above

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| EPIC-002 (Configuration Integrity) | Predecessor | Establishes Pydantic Settings baseline this epic extends |

---

## Notes

The audit verdict is unambiguous: configuration management in this codebase is an afterthought. The 15+ hardcoded paths to `/home/ai-whisperers/` are particularly telling — they suggest the code was written with the implicit assumption that it would only ever run on one machine. That assumption is incompatible with a production system.

The good news is that the fix is mechanical. There is no architectural ambiguity here, no competing design philosophies, no difficult trade-offs. The work is straightforward: find the scattered configuration, move it to `config.py`, document it, and enforce the discipline going forward. The difficulty is not intellectual — it is the patience required to touch 20+ files without introducing regressions.
