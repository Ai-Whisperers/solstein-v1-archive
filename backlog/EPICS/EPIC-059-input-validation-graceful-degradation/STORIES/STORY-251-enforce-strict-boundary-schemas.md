# STORY-251: Enforce Strict Boundary Schemas for Connector, API, and Domain Ingress

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-059 Input Validation and Graceful Degradation |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

The 2026-03-31 audit found multiple high-risk boundaries still behaving loosely. Connector fact envelopes allow undeclared keys through validation, API request models silently ignore unknown fields, and important domain ingress models do not make their extra-field policy explicit. This undermines the claim that schemas are strictly enforced at the system boundaries.

## Acceptance Criteria

- [ ] Connector fact validation rejects undeclared fields while preserving explicit legacy alias normalization (`type`, `_hash`, and `metadata=None` handling).
- [ ] Public API request models reject unknown fields unless a documented passthrough contract explicitly requires otherwise.
- [ ] High-risk domain ingress models or dedicated ingress DTOs define explicit extra-field behavior and are covered by tests.
- [ ] Behavioral tests prove undeclared fields fail at ingress and do not survive `model_dump()` on validated payloads.

## Tasks

- [ ] Audit extra-field policy on connector, API, and domain ingress models.
- [ ] Tighten boundary models to `forbid` or introduce explicit boundary DTOs where backward compatibility needs separation.
- [ ] Keep legacy alias translation explicit and narrow rather than relying on broad `extra=\"allow\"`.
- [ ] Add negative tests for unexpected keys on each hardened boundary.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story was added after the 2026-03-31 audit confirmed extra fields still survive or disappear silently at critical ingress points.

### Next Agent Action

- Start with connector fact ingestion and public API request models.
- Only widen scope to domain models where the ingress contract truly belongs there.

### Required Working Style

- Preserve intentional legacy compatibility through explicit normalization, not broad schema looseness.
- Favor fail-fast boundary contracts over downstream cleanup.

### Minimum Verification For Future Agents

- Add negative tests for unexpected keys on the hardened boundaries.
- Show legacy alias compatibility still works through explicit normalization rules.
