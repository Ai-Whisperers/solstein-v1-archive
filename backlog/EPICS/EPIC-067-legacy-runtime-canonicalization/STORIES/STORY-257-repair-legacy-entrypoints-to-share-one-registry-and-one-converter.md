# STORY-257: Repair Legacy Entrypoints to Share One Registry and One Converter

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

The legacy path is only worth saving if every entrypoint uses the same core components. Today `src/solstein/research/pipeline.py`, `src/solstein/data/unified_loader.py`, and script-level conversion helpers still allow drift in registry choice, conversion logic, and enrichment execution.

## Acceptance Criteria

- [ ] CLI, scripts, and API paths use the same registry builder for the canonical runtime.
- [ ] CLI, scripts, and API paths use the same canonical raw-to-domain converter.
- [ ] No script-level inline compatibility converter remains in the canonical legacy flow.
- [ ] A smoke test proves one company and one market run take the same shared path.

## Tasks

- [ ] Inventory legacy runtime entrypoints and the registry/converter each one uses.
- [ ] Replace local deviations with the canonical shared path.
- [ ] Add one smoke test per entrypoint class: CLI, API, and script.
