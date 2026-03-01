# STORY-139: Centralize Timeouts and Magic Numbers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-036: Configuration Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> 40+ magic numbers: timeouts 10-30s scattered across 8+ files, failure_threshold varies (3,4,5), recovery_timeout varies (45,60,90), Celery task_time_limit=30s.

## Problem Statement

Timeouts and retry thresholds are magic numbers scattered across the codebase. GitHub uses 15s, Companies House uses 20s, NewsAPI uses 10s — for no documented reason. When an API changes its SLA, finding and updating all the timeouts requires touching 8 files. When tuning for performance, there's no central place to adjust. The fix is configuration-driven timeouts with sensible defaults and environment overrides.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Timeouts scattered across files |
| **Operational** | Tuning requires code changes |
| **Reliability** | Inconsistent timeout behavior |

## Affected Files

| File | Issue |
|------|-------|
| All adapter files with timeout= | Magic numbers |
| Circuit breaker configs | Varying thresholds |
| `celery_config.py` | Magic numbers |

## Architectural Requirements

- Timeout configuration in config.py: DEFAULT_TIMEOUT, GITHUB_TIMEOUT, COMPANIES_HOUSE_TIMEOUT, etc.
- Circuit breaker configuration: FAILURE_THRESHOLD, RECOVERY_TIMEOUT, etc.
- Celery configuration: TASK_TIME_LIMIT, TASK_SOFT_TIME_LIMIT
- All magic numbers replaced with config references
- Environment variable overrides for all timeouts
- Documentation: rationale for each default timeout value
- Validation: timeouts must be positive integers

## Acceptance Criteria

- [ ] All timeouts defined in config.py
- [ ] No magic timeout numbers in adapter files
- [ ] Environment overrides work
- [ ] Documentation for each default

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: Timeout rationale documentation
- **Code Review Gate**: grep for "timeout=[0-9]" in adapters returns only config references

## Notes

Magic numbers should be config-driven with documented rationale.
