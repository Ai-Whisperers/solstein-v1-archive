# STORY-200: Add Quality-Gate Policy Before Scoring and Export

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - High |
| **Epic** | EPIC-052 Provenance, Confidence, and Quality Gates |
| **Created** | 2026-03-30 |
| **Dependencies** | STORY-198, STORY-199 |

## Problem Statement

Records can still reach scoring and export paths without one explicit quality gate that blocks or downgrades untrusted, synthetic, or insufficiently evidenced data.

## Acceptance Criteria

- [ ] A deterministic gate runs before scoring and export on the intended maintained path.
- [ ] Synthetic or mixed payloads do not silently pass into production exports.
- [ ] Gate outcomes are explicit: pass, downgrade, or block.

## Definition of Done

- [ ] The gate policy is implemented in one canonical place.
- [ ] Tests cover pass, downgrade, and block behavior.
- [ ] Downstream behavior matches the gate decision instead of bypassing it.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This file was created in the 2026-03-30 autonomy pass because EPIC-052 previously lacked canonical story artifacts.

### Next Agent Action

- Start only after the provenance and calibration boundaries are explicit enough to drive a deterministic gate.

### Required Working Style

- Keep the gate machine-checkable and observable.
- Do not replace a gate with narrative warnings or soft reviewer-only guidance.

### Minimum Verification For Future Agents

- Prove a low-quality or synthetic fixture is blocked or downgraded.
- Prove a valid fixture still reaches scoring/export cleanly.
