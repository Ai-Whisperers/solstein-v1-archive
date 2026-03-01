# EPIC-036: Configuration Consolidation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

Forensic audit found 15+ hardcoded paths, 12+ env vars NOT in config.py, 40+ magic numbers, 25+ hardcoded URLs. .env.example is missing GITHUB_TOKEN (required for startup!) and all LLM provider keys. Configuration is scattered across files with no central authority.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-137 | Centralize All Environment Variables in config.py | P2 |
| STORY-138 | Replace Hardcoded Paths with Config-Driven Paths | P2 |
| STORY-139 | Centralize Timeouts and Magic Numbers | P2 |
| STORY-140 | Fix .env.example with All Required Variables | P2 |

## Dependencies

- EPIC-002 (Configuration Integrity)

## Notes

The configuration is a scavenger hunt. Environment variables are defined where they're used, not where they're documented.
