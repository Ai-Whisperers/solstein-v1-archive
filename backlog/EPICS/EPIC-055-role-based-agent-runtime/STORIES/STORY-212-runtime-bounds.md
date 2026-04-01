# STORY-212: Migrate web acquisition connectors to runtime contracts

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-055](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | High |

## Problem Statement
Core acquisition connectors still bypass common contract wrapper and failure semantics.

## Affected Files
- `src/solstein/data/web_research_pipeline.py`
- `src/solstein/data/connectors/lookup_service.py`
- `src/solstein/data/enrichment_service.py`

## Acceptance Criteria
- Acquisition connectors return typed runtime envelope in all outcomes.
- No silent failures remain in migrated connector paths.
- Integration tests cover degraded and failure envelope branches.
