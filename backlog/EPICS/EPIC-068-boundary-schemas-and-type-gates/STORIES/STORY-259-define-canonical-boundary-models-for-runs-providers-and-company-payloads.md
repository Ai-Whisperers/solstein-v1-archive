# STORY-259: Define Canonical Boundary Models for Runs, Providers, and Company Payloads

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-068 Boundary Schemas and Type Gates |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

Critical runtime boundaries still pass loose dictionaries between connectors, pipelines, and workers. The system already has strong individual models in places like `src/solstein/api/schemas/enrichment.py`, but the canonical research runtime does not yet have one strict contract set for run state, provider envelopes, and company payload ingestion.

## Acceptance Criteria

- [ ] Canonical Pydantic models exist for research run state, provider request/response envelopes, and raw company payload ingestion.
- [ ] The canonical models are used at the entry and exit boundaries of the legacy runtime.
- [ ] Model ownership is documented in one place.
- [ ] Contract fixtures exist for both pass and fail cases.

## Tasks

- [ ] Inventory current loose dict boundaries in research, provider, worker, and export flows.
- [ ] Replace them with explicit models.
- [ ] Add contract fixtures and validation tests.
