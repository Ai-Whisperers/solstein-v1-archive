# STORY-235: Eliminate Placeholder Token Leakage in Active Docs

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-064 Markdown Integrity and Registry Correctness |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Template placeholders are present in maintained docs, signaling incomplete or misleading content.

## Acceptance Criteria

- [ ] Placeholder scan rules are defined for active documentation trees.
- [ ] Tokens (`EPIC-XXX`, `STORY-XXX`, `ADR-XXX`, `FD-XXX`, `TODO:`, `TBD`) are removed or quarantined.
- [ ] Template-only directories are explicitly scoped to avoid false positives.
- [ ] Post-remediation scan output is attached to change log.

## Definition of Done

- [ ] Active docs scan returns zero unresolved placeholder tokens.
- [ ] Token policy is documented for contributors.
