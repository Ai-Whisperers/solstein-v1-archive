# EPIC-052: Provenance, Confidence, and Quality Gates

| Field | Value |
|-------|-------|
| **Status** | ⚡ PARTIALLY UNBLOCKED |
| **Priority** | P0 – Ship Blocker |
| **Created** | 2026-03-10 |
| **Updated** | 2026-04-03 (gate enforcement stories 366–370, 378–380 added as READY from contamination audit; [STORY-198](STORIES/STORY-198.md)/199 still blocked on EPIC-050/051; [STORY-200](STORIES/STORY-200.md)/201 unblocked — gate code exists, needs wiring) |
| **Stories** | [STORY-198](STORIES/STORY-198.md), [STORY-199](STORIES/STORY-199.md), [STORY-200](STORIES/STORY-200.md), [STORY-201](STORIES/STORY-201.md), [STORY-366](STORIES/STORY-366.md)–370, [STORY-378](STORIES/STORY-378.md)–380 |
| **Dependencies** | [STORY-198](STORIES/STORY-198.md)/199 blocked by: EPIC-050 **NOT STARTED**, EPIC-051 **NOT STARTED** · [STORY-200](STORIES/STORY-200.md)/201/366–370/378–380: **no dependency — READY NOW** |

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

### Original stories ([STORY-198](STORIES/STORY-198.md)/199 blocked; [STORY-200](STORIES/STORY-200.md)/201 unblocked)

| Story | Title | Priority | Status | Blocked? |
|-------|-------|----------|--------|----------|
| [STORY-198](STORIES/STORY-198.md) | Enforce provenance completeness at enrichment write boundary | P0 | ⏳ BLOCKED | Yes — needs EPIC-050/051 |
| [STORY-199](STORIES/STORY-199.md) | Implement confidence calibration profile per source/reliability tier | P1 | ⏳ BLOCKED | Yes — needs EPIC-050/051 |
| [STORY-200](STORIES/STORY-200.md) | Add quality-gate policy before scoring and export | P0 | 🔴 READY | No — gate code exists, needs wiring (see [STORY-366](STORIES/STORY-366.md)–368) |
| [STORY-201](STORIES/STORY-201.md) | Add CI contract tests for provenance, confidence, and synthetic gates | P1 | 🔴 READY | No (see [STORY-369](STORIES/STORY-369.md)) |

> [STORY-200](STORIES/STORY-200.md) and [STORY-201](STORIES/STORY-201.md) story files recovered from stale `EPIC-052-provenance-quality-gates/`
> directory (dissolved 2026-04-03). [STORY-366](STORIES/STORY-366.md)–369 are the concrete implementation decomposition
> of [STORY-200](STORIES/STORY-200.md)/201 verified against the live codebase. Treat 366–369 as the actionable work.

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
| [STORY-380](STORIES/STORY-380.md) | Fix `CompetitorJsonSource.discover()` — propagate `data_source_type` into pipeline candidates | P0 | S | 🔴 READY (benefits from [STORY-379](STORIES/STORY-379.md) first) |

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

### Verified Codebase State (2026-04-04)

Direct file reads confirm the following contamination paths are STILL PRESENT:

**`SOLSTEIN_TEST_MODE` default (STORY-382):**
- `src/solstein/core/test_modes.py:16` — `mode = os.getenv("SOLSTEIN_TEST_MODE", "mixed")` → default is `"mixed"`
- `src/solstein/core/test_modes.py:26` — `allow_synthetic = mode in {"synthetic", "mixed"}` → default allows synthetic data without env var

**`strict_provenance=False` in legacy path (STORY-383):**
- `src/solstein/infrastructure/research_dual_write.py:424` — `_payload_from_legacy_kwargs()` hardcodes `strict_provenance=False`
- `src/solstein/research/pipeline.py:82-84` — `if not strict_provenance: return` → quality gate is entirely skipped when this value is used
- **Note:** The sync pipeline at `pipeline.py:72` defaults to `True`; the async pipeline at `pipeline_async.py:71` also defaults to `True`. The bug is exclusively in `_payload_from_legacy_kwargs()`.

**`CompanyRecord` missing `data_source_type` column (STORY-384):**
- `src/solstein/infrastructure/models/company.py:77` — only `data_source = Column(String(100), nullable=True)` exists
- No `data_source_type` column. All DB-loaded records cannot be filtered by the gate.
- No Alembic migration for this column (19 migrations exist, none add `data_source_type`).

**Converter fallback "real" (STORY-385):**
- `src/solstein/domain/models.py:178` — `industry: str = "Energy Software"` — wrong default (STORY-390, separate)
- Converter fallback "real" not directly verified in this session; check `src/solstein/data/converters/company.py`

**Adapters currently registered** (context for STORY-379/380):
- `src/solstein/adapters/enrichment/`: `funding.py`, `global_market.py`, `linkedin.py`, `patents.py`, `website.py`, `yahoo_finance.py`
- No SearXNG, GDELT, SEC EDGAR, or GitHub adapters exist yet (EPIC-073 scope)

**`SyntheticDataBlocker.ensure_safe()` (STORY-367):**
- Exists at `src/solstein/data/synthetic_data_safety.py:284`
- Zero callers confirmed (grep returns no results in production code)

**Execution order (from QUEUE.md):**
1. STORY-383 — remove `strict_provenance=False` from `_payload_from_legacy_kwargs()` (1-line fix, enormous impact)
2. STORY-382 — change `test_modes.py` default from `"mixed"` to `"strict_real"`
3. STORY-384 (EPIC-033) — add `data_source_type` column + Alembic migration
4. STORY-385 — fix converter fallback after 384 lands
5. STORY-366, STORY-367, STORY-368 — wire gate enforcement in export
6. STORY-369 — gate contract tests (blocked by 366+367+368)

### Queue Status

- All P0 gate stories (STORY-366-370, STORY-378-390) are READY in `planning/QUEUE.md`.
- [STORY-198](STORIES/STORY-198.md) and [STORY-199](STORIES/STORY-199.md) remain BLOCKED on EPIC-050 and EPIC-051 (both not started).
- [STORY-200](STORIES/STORY-200.md) and [STORY-201](STORIES/STORY-201.md) are superseded by STORY-366-369 as the concrete implementation decomposition.

### Required Working Style

- Use `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` as the boundary map.
- Use `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` as the anti-slop rule set: prefer strict schemas, deterministic gates, and generated/checked artifacts over prose summaries.
- Do not allow loose dict payloads to cross enrichment, scoring, export, or worker boundaries without an explicit validator.

### Minimum Verification For Future Agents

- STORY-383: Verify `_payload_from_legacy_kwargs()` no longer sets `strict_provenance=False`; add test that legacy path triggers quality gate.
- STORY-384: Run `alembic upgrade head` and confirm `data_source_type` column present in `company_records`.
- STORY-382: Verify `os.getenv("SOLSTEIN_TEST_MODE", "strict_real")` and test that unset env var rejects synthetic data.
- Add regression tests proving gate blocks synthetic/unknown/mixed and passes real for each story.
