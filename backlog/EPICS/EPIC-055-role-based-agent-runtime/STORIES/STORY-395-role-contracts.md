# STORY-395: Define connector request/response envelope schema

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-055](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Connector contracts are inconsistent across adapters, which causes silent parsing failures and brittle retries.

## Affected Files
- `src/solstein/data/connectors/base.py`
- `src/solstein/data/enrichment_types.py`

## Acceptance Criteria
- Canonical request/response envelope schema is defined and versioned.
- All migrated connectors validate envelope before returning payload.
