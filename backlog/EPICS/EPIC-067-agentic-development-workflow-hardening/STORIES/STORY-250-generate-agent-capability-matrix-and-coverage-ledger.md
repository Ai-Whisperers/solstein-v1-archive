# STORY-250: Generate Agent Capability Matrix and Coverage Ledger

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | Medium |

---

## Problem Statement

There is no compact generated artifact that tells a new agent session which runtime agents/nodes are real, deprecated, excluded, stubbed, or partially migrated, and which tests/audits cover each one.

## Acceptance Criteria

- [ ] A generated capability matrix exists for runtime agents, coordinator paths, graph nodes, and critical adapters.
- [ ] Each entry records implementation status, owning module, external tool/API, schema boundary, and linked tests/audits.
- [ ] Deprecated or excluded agent paths are explicitly marked instead of inferred from scattered prose.
- [ ] The matrix is linked from the main reference docs.

## Definition of Done

- [ ] Generator committed under `scripts/docs/`
- [ ] Generated markdown and JSON artifacts committed
- [ ] Freshness check added to the generated-doc workflow
