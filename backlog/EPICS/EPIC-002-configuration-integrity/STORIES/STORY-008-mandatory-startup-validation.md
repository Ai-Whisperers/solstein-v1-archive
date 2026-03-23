# STORY-008: Add Mandatory Startup Validation for All Required API Keys

| Field | Value |
|-------|-------|
| Status | ✅ Complete |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-002: Configuration Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-006](STORY-006-fix-duplicate-config-class-bodies.md) (config structure), [STORY-007](STORY-007-remove-hardcoded-credentials.md) (credential removal) |

---

## The Audit Verdict

> `config.py` lines 317–322 validate only `GITHUB_TOKEN` at application startup. All other external API keys — OpenAI, Groq, Fireworks, Kimi, Companies House, Google Search — are not validated. Missing keys cause runtime failures mid-analysis, potentially hours into a long-running research pipeline job.

## Problem Statement

Without comprehensive startup validation, the application starts successfully with a broken configuration, then fails during actual work. A research pipeline job that takes hours to reach its first OpenAI call will fail at that call for a missing key, after all preceding computation has been completed and paid for. The startup validation that exists for `GITHUB_TOKEN` proves the pattern was known — it was simply not applied to the other 6+ external services.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Analysis jobs fail mid-execution due to missing configuration discovered at runtime |
| **Operational Cost** | Failed jobs waste compute resources, API quota on other providers, and operator time |
| **Developer Experience** | Configuration completeness cannot be verified before starting work — the only way to discover a missing key is to trigger the code path that uses it |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/config.py` | Modify | Lines 317–322: extend validation to all external API keys |
| `src/solstein/api/main.py` | Modify | Surface startup validation errors with provider-level detail |
| `tests/unit/test_config.py` | Add/Modify | Per-key validation tests |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Every external API key required for core functionality must be validated at startup before the application begins accepting requests
- **REQ-2**: Validation must confirm the key is non-empty and, where the format is known (key prefix, minimum length), it must match the expected format
- **REQ-3**: A startup summary log must list each provider with status: `configured`, `missing (optional)`, or `missing (required — halting)`
- **REQ-4**: Missing optional keys must log a WARNING; missing required keys must raise an exception that prevents startup

## Acceptance Criteria

- [ ] Starting the application with a required API key absent logs a specific error naming the missing key and fails to start
- [ ] Starting the application with all keys present logs a clean startup summary listing each provider's status
- [ ] Starting the application with an optional key absent logs a WARNING naming the key and continues
- [ ] The startup summary is human-readable and lists all providers in a single log block

## Definition of Done

**Tests Required:**
- [ ] Unit test: each required key absent → startup fails with correct error message naming the key
- [ ] Unit test: each optional key absent → startup continues with WARNING log
- [ ] Unit test: all keys present → startup summary log contains no warnings or errors

**Documentation Required:**
- [ ] Configuration reference updated with: required vs optional status, format requirements, and fallback behavior for each API key
- [ ] `.env.example` updated with all keys and their required/optional designation

**Code Review Gate:**
- [ ] Reviewer confirms every external API key used in the codebase has a corresponding startup validation check
- [ ] Reviewer confirms the startup summary log is produced before the application begins accepting HTTP requests

## Notes

This story depends on both STORY-006 and STORY-007. Adding startup validation to a config file with duplicate class bodies and hardcoded defaults risks validators firing against the wrong definitions or being silently discarded. The structural and credential issues must be resolved first.
