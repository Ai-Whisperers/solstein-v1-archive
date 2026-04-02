# STORY-201: Add CI Contract Tests for Provenance, Confidence, and Synthetic Gates

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - Medium |
| **Epic** | EPIC-052 Provenance, Confidence, and Quality Gates |
| **Created** | 2026-03-30 |
| **Dependencies** | STORY-198, STORY-199, STORY-200 |

## Problem Statement

Even correct gate logic will drift if provenance, confidence, and synthetic protections are not enforced by repeatable CI contract tests.

## Acceptance Criteria

- [ ] Fast contract tests cover provenance completeness, confidence calibration, and synthetic gate behavior.
- [ ] CI can run the contract set without depending on unrelated app startup.
- [ ] The contract suite fails when boundary drift reappears.

## Definition of Done

- [ ] The contract suite is targeted and deterministic.
- [ ] At least one regression case exists for each protected gate family.
- [ ] The intended CI entrypoint is documented in the epic/story docs or audit references.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This file was created in the 2026-03-30 autonomy pass because EPIC-052 previously lacked canonical story artifacts.

### Next Agent Action

- Treat this as the capstone enforcement story after the underlying provenance, calibration, and pre-scoring/export gates exist.

### Required Working Style

- Follow the harness-modularity guidance in `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Keep the suite narrow enough to fail fast on boundary drift.

### Minimum Verification For Future Agents

- Run the new contract suite in isolation.
- Show one intentional bad fixture fails for the expected reason.
