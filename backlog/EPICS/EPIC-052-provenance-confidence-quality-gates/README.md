# EPIC-052: Provenance, Confidence, and Quality Gates

| Field | Value |
|-------|-------|
| **Status** | ⚡ PARTIALLY UNBLOCKED |
| **Priority** | P0 – Ship Blocker |
| **Created** | 2026-03-10 |
| **Updated** | 2026-04-03 (gate enforcement stories 366–370, 378–380 added as READY from contamination audit; STORY-198/199 still blocked on EPIC-050/051; STORY-200/201 unblocked — gate code exists, needs wiring) |
| **Stories** | STORY-198, STORY-199, STORY-200, STORY-201, STORY-366–370, STORY-378–380 |
| **Dependencies** | STORY-198/199 blocked by: EPIC-050 **NOT STARTED**, EPIC-051 **NOT STARTED** · STORY-200/201/366–370/378–380: **no dependency — READY NOW** |

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

### Original stories (STORY-198/199 blocked; STORY-200/201 unblocked)

| Story | Title | Priority | Status | Blocked? |
|-------|-------|----------|--------|----------|
| STORY-198 | Enforce provenance completeness at enrichment write boundary | P0 | ⏳ BLOCKED | Yes — needs EPIC-050/051 |
| STORY-199 | Implement confidence calibration profile per source/reliability tier | P1 | ⏳ BLOCKED | Yes — needs EPIC-050/051 |
| STORY-200 | Add quality-gate policy before scoring and export | P0 | 🔴 READY | No — gate code exists, needs wiring (see STORY-366–368) |
| STORY-201 | Add CI contract tests for provenance, confidence, and synthetic gates | P1 | 🔴 READY | No (see STORY-369) |

> Note: STORY-200 and STORY-201 story files were never created. STORY-366–369 below are their
> concrete implementation tasks, verified against the live codebase. Treat 366–369 as the
> actionable decomposition of 200/201.

### Gate enforcement (contamination audit 2026-04-03 — all READY, no dependencies)

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-366](STORIES/STORY-366.md) | Extend gate to treat `data_source_type="unknown"` as blocked (allowlist: only "real"/"verified" pass) | P0 | XS | 🔴 READY |
| [STORY-367](STORIES/STORY-367.md) | Wire `SyntheticDataBlocker.ensure_safe()` into `export.py` — currently has zero callers | P0 | S | 🔴 READY |
| [STORY-368](STORIES/STORY-368.md) | Add `if not gate_result.passed: raise` guard after `gate.evaluate()` in `export.py` | P0 | XS | 🔴 READY |
| [STORY-369](STORIES/STORY-369.md) | Contract tests: gate blocks synthetic/unknown/mixed, passes real | P0 | S | 🔴 BLOCKED by 366–368 |

### Production loader provenance (contamination audit 2026-04-03 — all READY)

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-370](STORIES/STORY-370.md) | Fix `scripts/seed_db.py` — set `data_source_type="synthetic"` on all Faker-seeded records | P0 | XS | 🔴 READY |
| [STORY-378](STORIES/STORY-378.md) | Fix `src/solstein/data/seed_db.py` (production module) — set `data_source_type` before `repo.save()` | P0 | XS | 🔴 READY |
| [STORY-379](STORIES/STORY-379.md) | Fix `competitor_loader.py` — tag loaded companies; expose `reset_loader()` cache API | P0 | S | 🔴 READY |
| [STORY-380](STORIES/STORY-380.md) | Fix `CompetitorJsonSource.discover()` — propagate `data_source_type` into pipeline candidates | P0 | S | 🔴 READY (benefits from STORY-379 first) |

### Deep gate + schema pass (third-pass contamination audit 2026-04-03 — all READY)

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-382](STORIES/STORY-382.md) | Fix `test_modes.py` — change `SOLSTEIN_TEST_MODE` default from `"mixed"` to `"strict_real"` | P0 | XS | 🔴 READY |
| [STORY-383](STORIES/STORY-383.md) | Fix `research_dual_write.py` — remove hardcoded `strict_provenance=False` from production pipeline | P0 | S | 🔴 READY |
| [STORY-385](STORIES/STORY-385.md) | Fix `converters/company.py` — change `data_source_type` fallback from `"real"` to `"unknown"` | P0 | XS | 🔴 READY (benefits from STORY-384 first) |
| [STORY-388](STORIES/STORY-388.md) | Fix `instrumented.py` — propagate actual adapter confidence instead of hardcoding `1.0` | P1 | S | 🔴 READY |
| [STORY-389](STORIES/STORY-389.md) | Fix SEC EDGAR connectors — replace `solstein@example.com` placeholder with configured email | P1 | XS | 🔴 READY |
| [STORY-390](STORIES/STORY-390.md) | Fix `domain/models.py` — change `industry` default from `"Energy Software"` to `None` | P1 | M | 🔴 READY |

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
