# EPIC-052: Provenance, Confidence, and Quality Gates

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P0 – Ship Blocker |
| **Created** | 2026-03-10 |
| **Stories** | STORY-198, STORY-199, STORY-200, STORY-201 |
| **Dependencies** | EPIC-050 (Web Acquisition Pipeline), EPIC-051 (Multi-Source Growth Signals), EPIC-003 (Core Product Correctness) |

## Context

Collecting more data does not improve outcomes unless quality is measurable and enforced. Solstein already has `data_source_type`, provenance models, and synthetic-data safety gates, but quality control is not yet end-to-end enforced at ingestion and scoring boundaries.

This epic creates hard quality gates so untrusted or low-confidence data cannot silently influence classification.

## Scope

| Category | Action |
|----------|--------|
| Provenance Completeness | Enforce source URL/time/confidence per field |
| Confidence Calibration | Normalize and calibrate confidence scores per source class |
| Quality Gate | Block scoring/export for insufficient-quality records |
| Synthetic Guardrails | Strengthen synthetic/mixed detection and gating |
| Contract Testing | Add automated tests for provenance + gate behavior |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-198](STORIES/STORY-198-enforce-provenance-completeness-at-write-boundary.md) | Enforce provenance completeness at enrichment write boundary | P0 | 🔴 Not Started |
| [STORY-199](STORIES/STORY-199-confidence-calibration-profile-per-source-tier.md) | Implement confidence calibration profile per source/reliability tier | P1 | 🔴 Not Started |
| [STORY-200](STORIES/STORY-200-quality-gate-before-scoring-and-export.md) | Add quality-gate policy before scoring and export | P0 | 🔴 Not Started |
| [STORY-201](STORIES/STORY-201-ci-contract-tests-for-provenance-confidence-and-synthetic-gates.md) | Add CI contract tests for provenance, confidence, and synthetic gates | P1 | 🔴 Not Started |

## Target Integration Points

- `src/solstein/data/provenance.py`
- `src/solstein/data/synthetic_data_safety.py`
- `src/solstein/data/enrichment_types.py`
- `src/solstein/analytics/completeness.py`
- `src/solstein/analytics/data_quality.py`
- `src/solstein/analytics/scoring.py`

## Architectural Requirements

- **REQ-1**: Each scored field must include provenance and confidence metadata or be explicitly marked unavailable.
- **REQ-2**: Confidence must be normalized to deterministic tiers with documented mapping.
- **REQ-3**: Records below minimum quality threshold must be blocked or downgraded before classification.
- **REQ-4**: Synthetic/mixed source types must never flow into production exports.
- **REQ-5**: Gate decisions must be observable and reproducible from logs/metadata.

## Success Criteria

- 100% of scored companies carry field-level provenance for all non-null enriched fields.
- Quality-gate false-pass rate (bad data marked good) < 2% in evaluation set.
- Synthetic/mixed leakage to production export: 0 occurrences.
- Confidence calibration report produced for each batch run.
- Regression suite includes gate contract tests with pass rate 100%.

## Risks

| Risk | Mitigation |
|------|------------|
| Strict gates reduce usable coverage initially | Roll out warn mode first, then enforce block mode by milestone |
| Confidence mapping drifts by source changes | Version confidence profiles and retune quarterly |
| Gate checks add latency | Run gate checks as deterministic lightweight validators |
| Teams bypass quality checks in scripts | Move checks into shared boundary APIs used by all flows |

## Notes

This epic is the trust boundary. Without it, improved acquisition can still produce polished garbage. With it, every score is quality-qualified and auditable.

## Autonomous Continuation Notes

### Queue Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` before starting any story here.
- `planning/QUEUE.md` last marked this epic `BLOCKED` because canonical story files were missing.
- This pass adds canonical story files for `STORY-198` through `STORY-201`, so future agents must re-check the queue blocker text before implementation instead of trusting the old reason blindly.

### Develop-Relevant Evidence

- The current develop branch already contains stricter batch-enrichment boundary models in `src/solstein/api/schemas/enrichment.py` and `src/solstein/data/unified/batch_outcomes.py`.
- `tests/unit/test_issue11_batch_enrichment_outcomes.py` is the closest existing regression anchor for explicit typed outcomes, partial-status validation, and aggregate consistency checks.
- Future provenance/confidence work should follow this explicit boundary-contract style instead of introducing loose intermediary dict payloads.

### Next Agent Action

- Use the new canonical story files to plan the next queue update or implementation pass.
- Preferred execution order remains: provenance write-boundary enforcement -> confidence calibration -> pre-scoring/export quality gate -> CI contract tests.

### Required Working Style

- Use `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` as the boundary map.
- Use `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` as the anti-slop rule set: prefer strict schemas, deterministic gates, and generated/checked artifacts over prose summaries.
- Do not allow loose dict payloads to cross enrichment, scoring, export, or worker boundaries without an explicit validator.

### Minimum Verification For Future Agents

- Add regression coverage for every new gate.
- Prove gate behavior in both pass and fail modes.
- Keep verification focused on machine-checkable outputs: schema validation, targeted tests, and gate commands rather than narrative inspection.
