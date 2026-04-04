# STORY-398: Add config-driven session/proxy/page-budget controls

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-055](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Connector runtime parameters are hardcoded or scattered, reducing operational control.

## Affected Files
- `src/solstein/config/runtime.py`
- `src/solstein/data/source_policy.py`
- `src/solstein/data/web_research_pipeline.py`

## Acceptance Criteria
- Session/proxy/page-budget runtime settings are configurable per environment.
- Runtime reads and enforces limits for each connector call.
- Limit violations emit deterministic degraded/failure envelopes.
