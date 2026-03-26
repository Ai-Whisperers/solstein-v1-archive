# STORY-245: Expand Generated API Docs and Schema Registries

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | High |

---

## Problem Statement

The current automated docs layer only covers a small strict slice. High-risk folders such as `analytics`, `data`, and `domain` still need package cleanup and generated schema/boundary registries before the docs system becomes broadly useful.

## Acceptance Criteria

- [ ] Missing package-addressability blockers are resolved for the targeted modules.
- [ ] A generated schema ownership map is committed and linked from reference docs.
- [ ] A generated pipeline boundary registry is committed and linked from reference docs.
- [ ] A generated connector contract surface index is committed and linked from reference docs.
- [ ] Docs generation remains strict and blocking for the maintained subset while the broader expansion is phased in.

## Definition of Done

- [ ] `PYTHON_API_REFERENCE.md` expands beyond the current strict slice.
- [ ] Generated docs cover the critical business pipeline boundaries.
- [ ] Future agents can answer schema ownership and connector-contract questions without reopening large source areas.
