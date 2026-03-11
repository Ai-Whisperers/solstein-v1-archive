# STORY-238: Implement CI Docs Quality Gates

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-11 |
| **Risk** | Medium |

---

## Problem Statement

Docs quality regressions are not consistently blocked during pull-request review.

## Acceptance Criteria

- [ ] CI workflow includes link check, placeholder token check, and metadata validation.
- [ ] Rule severities are defined (block vs warn).
- [ ] Allowlist/exception mechanism requires `owner`, `rationale`, and `expiry` metadata.
- [ ] Developer guide includes local pre-flight command.

## Definition of Done

- [ ] CI gate runs on docs/backlog changes.
- [ ] At least one sample violation demonstrates failing behavior.
