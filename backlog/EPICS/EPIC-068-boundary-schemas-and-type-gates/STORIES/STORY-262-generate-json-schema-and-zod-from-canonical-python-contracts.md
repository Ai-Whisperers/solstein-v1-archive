# STORY-262: Generate JSON Schema and Zod from Canonical Python Contracts

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-068 Boundary Schemas and Type Gates |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

The repo does not currently have a production TypeScript runtime, but the architecture target in `docs/quality-and-fixes/COMPREHENSIVE-UPDATE.md` expects TS-side contract enforcement as well. If Zod is introduced manually before canonical Python schemas are stable, the repo will create a second drift vector.

## Acceptance Criteria

- [ ] JSON Schema is generated from canonical Python models.
- [ ] Zod artifacts are generated from the same source schemas, not hand-written.
- [ ] Generated artifacts are versioned and diffable.
- [ ] No TS contract is declared canonical unless it is generated from the Python source of truth.

## Tasks

- [ ] Choose the canonical generation path from Pydantic to JSON Schema.
- [ ] Add Zod generation for the future TS control plane.
- [ ] Add CI to prevent manual divergence.
