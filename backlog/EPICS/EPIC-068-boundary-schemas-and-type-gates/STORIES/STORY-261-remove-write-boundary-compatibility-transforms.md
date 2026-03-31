# STORY-261: Remove Write-Boundary Compatibility Transforms

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-068 Boundary Schemas and Type Gates |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

`src/solstein/domain/payload_compat.py` and alias logic in `src/solstein/data/converters/company.py` silently reshape payloads to preserve backward compatibility. That makes it impossible to tell whether upstream producers are sending canonical data or stale legacy variants.

## Acceptance Criteria

- [ ] Write boundaries reject non-canonical payloads unless they pass through an explicit migration utility with audit logging.
- [ ] Compatibility transforms are removed from hot-path write boundaries.
- [ ] Alias use is measurable and visible while migrations are still in progress.
- [ ] Tests prove canonical acceptance and legacy rejection behavior.

## Tasks

- [ ] Inventory every write-boundary compatibility transform.
- [ ] Replace implicit aliasing with explicit migration or hard failure.
- [ ] Add audit reporting for residual legacy payloads.
