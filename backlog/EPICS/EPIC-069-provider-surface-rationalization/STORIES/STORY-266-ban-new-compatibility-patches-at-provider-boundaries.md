# STORY-266: Ban New Compatibility Patches at Provider Boundaries

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-069 Provider Surface Rationalization |
| **Created** | 2026-03-31 |
| **Risk** | Low |

---

## Problem Statement

The repo already has a pattern of preserving compatibility wrappers instead of fixing the canonical provider surface. If that pattern continues during consolidation, the provider cleanup will fail by accretion.

## Acceptance Criteria

- [ ] Provider-boundary compatibility patches are explicitly banned in engineering guardrails for the consolidation window.
- [ ] Existing exceptions are documented and time-bounded.
- [ ] CI or review checklists catch new compatibility wrappers in provider/runtime modules.
- [ ] The ban applies to adapters, provider payload transforms, and API/provider glue code.

## Tasks

- [ ] Add the policy to the canonical backlog and guardrail docs.
- [ ] Define the modules covered by the ban.
- [ ] Add review/CI enforcement where feasible.
