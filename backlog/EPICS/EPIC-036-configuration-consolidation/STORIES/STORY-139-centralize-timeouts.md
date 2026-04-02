# STORY-139: Centralize Timeouts and Magic Numbers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-002 (Configuration Integrity), STORY-137 |

---

## The Audit Verdict

> 40+ magic numbers: timeouts `10`–`30`s scattered across 8+ files, `failure_threshold` varies (`3`, `4`, `5`), `recovery_timeout` varies (`45`, `60`, `90`), Celery `task_time_limit=30`.

---

## Problem Statement

Timeouts and retry thresholds are magic numbers scattered across the codebase. The GitHub adapter uses 15 seconds. The Companies House adapter uses 20 seconds. The NewsAPI adapter uses 10 seconds. None of these values are documented. None of them are configurable without a code change. None of them are consistent with each other, and there is no evidence that any of them were chosen based on actual SLA data from the respective APIs.

The circuit breaker configuration is worse. `failure_threshold` — the number of consecutive failures before a circuit opens — is `3` in one file, `4` in another, and `5` in a third. These are not different thresholds for different services with different reliability characteristics. They are the same conceptual setting, implemented three times with three different values, because each implementation was written independently without reference to a central configuration.

The operational consequence is that tuning the system for production requires touching 8+ files, running tests on each, and hoping nothing was missed. When an external API changes its SLA and the timeout needs to be increased, the change requires a code review and a deployment. This is unnecessary friction for what should be a configuration change.

The fix is to move all timeouts, thresholds, and limits into `config.py` with environment variable overrides. Operators can then tune the system without touching code. The defaults should be documented with rationale — not just the value, but why that value was chosen.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Timeouts scattered across 8+ files; no single place to understand or change timeout behavior |
| **Operational** | Tuning for production requires code changes, review, and deployment; no runtime configurability |
| **Reliability** | Inconsistent circuit breaker thresholds produce unpredictable failure behavior across adapters |
| **Observability** | Magic numbers in logs are meaningless without context; named constants are self-documenting |

---

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/infrastructure/adapters/github_adapter.py` | `timeout=15` hardcoded |
| `src/solstein/infrastructure/adapters/companies_house_adapter.py` | `timeout=20` hardcoded |
| `src/solstein/infrastructure/adapters/news_adapter.py` | `timeout=10` hardcoded |
| `src/solstein/infrastructure/adapters/sec_edgar_adapter.py` | `timeout=30` hardcoded |
| `src/solstein/infrastructure/adapters/exa_adapter.py` | `timeout=15` hardcoded |
| `src/solstein/infrastructure/circuit_breaker.py` | `failure_threshold` and `recovery_timeout` hardcoded with inconsistent values |
| `src/solstein/worker.py` | `task_time_limit=30`, `task_soft_time_limit=25` hardcoded |
| `src/solstein/infrastructure/celery_config.py` | Multiple Celery timing constants hardcoded |

---

## Architectural Requirements

- Per-adapter timeout configuration in `config.py`: `GITHUB_TIMEOUT`, `COMPANIES_HOUSE_TIMEOUT`, `NEWS_API_TIMEOUT`, `SEC_EDGAR_TIMEOUT`, `EXA_TIMEOUT`, plus a `DEFAULT_HTTP_TIMEOUT` fallback
- Circuit breaker configuration in `config.py`: `CIRCUIT_BREAKER_FAILURE_THRESHOLD`, `CIRCUIT_BREAKER_RECOVERY_TIMEOUT`, `CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS`
- Celery timing configuration in `config.py`: `CELERY_TASK_TIME_LIMIT`, `CELERY_TASK_SOFT_TIME_LIMIT`, `CELERY_RESULT_EXPIRES`
- All magic numbers in adapter files replaced with references to the settings object
- Environment variable overrides for all timeout and threshold values
- Inline documentation for each setting: the default value, the rationale for that default, and the operational impact of changing it
- Validation: all timeout values must be positive integers; `SOFT_TIME_LIMIT` must be less than `TIME_LIMIT`; `FAILURE_THRESHOLD` must be a positive integer
- Consistent circuit breaker configuration: all adapters use the same settings object, not independent hardcoded values

---

## Acceptance Criteria

- [ ] All timeout values defined as named settings in `config.py`
- [ ] All circuit breaker thresholds defined as named settings in `config.py`
- [ ] All Celery timing constants defined as named settings in `config.py`
- [ ] `grep -rE 'timeout=[0-9]' src/solstein/infrastructure/adapters/` returns zero results
- [ ] `grep -rE 'failure_threshold=[0-9]' src/` returns zero results
- [ ] `grep -rE 'task_time_limit=[0-9]' src/` returns zero results
- [ ] Environment variable overrides verified: changing `GITHUB_TIMEOUT` env var changes the timeout used by the GitHub adapter
- [ ] Every timeout setting has an inline docstring with rationale for the default value
- [ ] `CELERY_TASK_SOFT_TIME_LIMIT` validation confirms it is less than `CELERY_TASK_TIME_LIMIT`

---

## Definition of Done

- **Tests Required**: Unit test that settings validation rejects negative timeout values. Unit test that `SOFT_TIME_LIMIT >= TIME_LIMIT` raises `ValidationError`. Integration test that adapter timeout is read from settings, not hardcoded (verify by changing the setting and confirming the adapter uses the new value).
- **Documentation Required**: Inline docstrings on every timeout and threshold setting, including: default value, rationale, and operational guidance for tuning. Operator guide section on timeout configuration.
- **Code Review Gate**: Reviewer runs `grep -rE 'timeout=[0-9]' src/solstein/infrastructure/adapters/` and confirms zero results. Reviewer verifies all circuit breaker configurations reference the same settings object. Reviewer confirms every setting has a docstring with rationale.

---

## Notes

The rationale for each default timeout should be documented even if the rationale is simply "this was the original hardcoded value and has not been validated against actual API SLAs." Honest documentation is better than no documentation. A follow-up story can establish proper SLA-based timeout values once the configuration infrastructure is in place.

The inconsistent circuit breaker thresholds (`3`, `4`, `5`) should be unified to a single default. The recommended default is `5` consecutive failures before opening, with a `60`-second recovery timeout. These values are conservative and can be tuned per-environment via environment variables once the configuration infrastructure exists.

This story can proceed in parallel with STORY-138 after STORY-137 is complete.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
