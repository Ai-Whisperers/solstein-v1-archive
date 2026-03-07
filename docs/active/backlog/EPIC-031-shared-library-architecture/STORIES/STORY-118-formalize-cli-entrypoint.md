# STORY-118: Formalize CLI as Proper Package Entrypoint

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-031: Shared Library & Architecture |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-027/STORY-100 (Delete bypass scripts) |

## The Audit Verdict

> `scripts/solstein_cli.py` — Click-decorated CLI that calls domain layer directly, bypassing API auth, middleware, rate limiting, and audit logging. Not documented as official entrypoint. Not tested. Not installed via `pip install -e .` entry_points.

## Problem Statement

The CLI is a script that lives in `scripts/`, isn't installed, isn't tested, and calls the domain layer by importing Python modules directly. This means CLI operations bypass every security and observability control that the API enforces. An analyst who runs `solstein research "Company X"` gets an unauthenticated, unlogged, unrate-limited domain call that produces results indistinguishable from API results — except they're invisible to the audit trail and monitoring. After STORY-100 deletes the bypass scripts, the CLI must become a proper first-class entrypoint that calls the API.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Security** | CLI bypasses all middleware |
| **Operational** | CLI operations invisible to monitoring |
| **Maintainability** | Two code paths to maintain for the same operation |

## Affected Files

| File | Issue |
|------|-------|
| `scripts/solstein_cli.py` | Calls domain layer directly |
| `pyproject.toml` | No entrypoint defined |

## Architectural Requirements

- CLI registered as a package entrypoint in `pyproject.toml` under `[project.scripts]`: `solstein = "solstein.cli:main"`
- CLI commands call the API via HTTP (with authentication) rather than domain layer directly
- CLI manages auth: `solstein login` command stores token in `~/.solstein/credentials` (similar to AWS CLI)
- `solstein research <company>` → POST `/api/v1/research`, poll status, display progress
- `solstein export <company_id> --format excel` → POST `/api/v1/exports`, wait, download file
- `solstein status <job_id>` → GET `/api/v1/jobs/{job_id}`, display status
- `solstein companies list` → GET `/api/v1/companies`, formatted table output
- All CLI commands have `--help` documentation and `--output json` flag for scripting
- CLI tested with pytest (mock API responses, not live API)

## Acceptance Criteria

- [ ] `pip install -e .` makes `solstein` available as a shell command
- [ ] `solstein --help` displays all commands with descriptions
- [ ] `solstein research "Company X"` calls the API (verifiable via API audit log)
- [ ] `solstein login` stores credentials and subsequent commands use them
- [ ] Zero direct domain imports remain in CLI module

## Definition of Done

- **Tests Required**: Integration test: install package, run `solstein companies list` against live API
- **Documentation Required**: CLI usage guide
- **Code Review Gate**: Reviewer verifies zero `from solstein.domain` imports in CLI module

## Notes

The CLI becomes a first-class API client, not a domain bypass tool.
