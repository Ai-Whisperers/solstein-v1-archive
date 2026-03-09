# EPIC-002: Configuration Integrity

| Field | Value |
|-------|-------|
| Priority | **P0 — Ship Blocker** |
| Status | ✅ Complete |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | None — this is the root of the critical path |

## Context

The configuration system is the foundation on which every other component builds. That foundation is currently cracked in three places.

**Duplicate class body definitions.** `config.py` defines `DatabaseConfig` and at least 6 LLM provider configuration fields twice within the same class bodies. Python's class loading is deterministic but unforgiving: when a field name appears twice, the second definition silently replaces the first. Validators attached to the first definition — the ones engineers wrote and believe are running — are dead code. They will never execute regardless of what configuration values are provided. The effective configuration schema does not match what the source code appears to define.

**Default credentials.** `config.py` lines 42 and 379 hardcode the PostgreSQL connection string as `postgresql://postgres:postgres@localhost:5432/solstein`. Lines 133 and 141–145 hardcode the JWT signing secret as `change-me-in-production`. Both serve as fallback defaults. Any deployment where environment variables are not set — including misconfigured container orchestration, CI/CD environments, or staging — runs with publicly known credentials and a forgeable JWT secret.

**Incomplete startup validation.** Only `GITHUB_TOKEN` is validated at startup (lines 317–322). All other external API keys — OpenAI, Groq, Fireworks, Kimi, Companies House, Google Search — are not checked until runtime. A long-running research pipeline job discovers a missing key at the point of the first external API call, potentially hours into execution, after significant compute has been consumed.

This epic is the root of the critical path. EPIC-001 (Security Restoration) cannot begin until this is resolved. Authentication fixes built on broken configuration inherit the defects of their foundation.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-006](STORIES/STORY-006-fix-duplicate-config-class-bodies.md) | Fix Duplicate Class Body Definitions in config.py | CRITICAL |
| [STORY-007](STORIES/STORY-007-remove-hardcoded-credentials.md) | Remove All Hardcoded Credentials | CRITICAL |
| [STORY-008](STORIES/STORY-008-mandatory-startup-validation.md) | Add Mandatory Startup Validation for All API Keys | HIGH |

## Definition of Done

## Definition of Done

- [x] No duplicate class field definitions exist anywhere in `config.py`
- [x] No insecure credential defaults exist — every security-sensitive configuration field is required with no fallback
- [x] All required API keys are validated at startup before the application begins accepting requests
- [x] Missing required keys produce startup errors that name the specific missing variable
- [x] Missing optional keys produce WARNING-level logs and allow startup to continue
- [ ] No insecure credential defaults exist — every security-sensitive configuration field is required with no fallback
- [ ] All required API keys are validated at startup before the application begins accepting requests
- [ ] Missing required keys produce startup errors that name the specific missing variable
- [ ] Missing optional keys produce WARNING-level logs and allow startup to continue

## Ordering Rationale

STORY-006 must complete before STORY-007 and STORY-008. Removing hardcoded credentials from a file with duplicate class bodies risks applying the removal to the wrong (discarded) definition. Fix the structural defect first, then fix the values within the corrected structure.
