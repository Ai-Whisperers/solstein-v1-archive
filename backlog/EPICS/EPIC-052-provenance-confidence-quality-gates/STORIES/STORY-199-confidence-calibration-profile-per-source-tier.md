# STORY-199: Implement Confidence Calibration Profile per Source Tier

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - Medium |
| **Epic** | EPIC-052 Provenance, Confidence, and Quality Gates |
| **Created** | 2026-03-30 |
| **Dependencies** | STORY-198, EPIC-050, EPIC-051 |

## Problem Statement

Confidence values are not yet normalized into one deterministic calibration model across source classes and reliability tiers.

## Acceptance Criteria

- [ ] Source classes and reliability tiers map to deterministic confidence behavior.
- [ ] Calibration rules are versionable and testable.
- [ ] Batch/reporting surfaces can expose the calibrated result without hidden heuristics.

## Definition of Done

- [ ] Calibration profile exists in one canonical location.
- [ ] Tests prove the same input source tier produces the same calibrated outcome.
- [ ] Downstream callers use the calibrated profile instead of ad-hoc per-source guesses.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This file was created in the 2026-03-30 autonomy pass because EPIC-052 previously lacked canonical story artifacts.

### Next Agent Action

- Keep this story focused on calibration ownership and deterministic mapping; do not bundle export/scoring block policy work here.

### Required Working Style

- Follow `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` and prefer explicit, machine-checkable mappings over prose explanations.

### Minimum Verification For Future Agents

- Add regression coverage for calibration per source tier.
- Show that recalculating the same fixture produces the same calibrated output.
