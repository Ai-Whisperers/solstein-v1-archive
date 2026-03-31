# STORY-256: Delete Runtime Aliases and Feature-Flag Branching Around Orchestration

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Legacy Runtime Canonicalization |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

`src/solstein/research/pipeline_async.py`, `src/solstein/research/pipeline.py`, and `src/solstein/adapters/registry.py` currently preserve multiple orchestration shapes behind aliases and feature flags. This makes debugging impossible because the active runtime changes with configuration and import path rather than explicit architecture.

## Acceptance Criteria

- [ ] `run_market_intelligence` has one canonical implementation and one documented ownership path.
- [ ] Runtime feature flags are removed or demoted to clearly temporary migration toggles with expiry.
- [ ] Registry construction does not branch between competing enrichment architectures for the canonical path.
- [ ] Tests prove which runtime path executes under default settings.
- [ ] If any temporary branch remains, it has an explicit deletion trigger and no silent default behavior.

## Tasks

- [ ] Remove or rename backward-compatible runtime aliases that hide ownership.
- [ ] Collapse orchestration feature flags around the canonical runtime.
- [ ] Add targeted regression tests for runtime selection behavior.
- [ ] Delete or quarantine orphaned alias entrypoints that are not part of the canonical runtime.
