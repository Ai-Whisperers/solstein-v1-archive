# STORY-253: Generate Boundary and State Ownership Registries

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | High |

---

## Problem Statement

Agents still need to open too many files to answer basic questions about pipeline boundaries, state ownership, and critical side effects.

## Acceptance Criteria

- [ ] A generated pipeline boundary registry exists for critical nodes.
- [ ] A generated state ownership map exists for orchestration/stateful flows.
- [ ] Each entry records read/write fields, side effects, persistence touches, related schemas, and covering tests.
- [ ] The registries are linked from the generated reference index and enforced for freshness.

## Definition of Done

- [ ] Source-derived generators committed
- [ ] Generated markdown and JSON committed
- [ ] Registry freshness included in generated-doc gate
