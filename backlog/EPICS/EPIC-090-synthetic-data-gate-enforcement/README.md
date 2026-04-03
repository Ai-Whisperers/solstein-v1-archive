# EPIC-090: Synthetic Data Gate Enforcement

> **Priority**: P0 — Ship Blocker (silent contamination reaches production exports today)
> **Stories**: 4 (STORY-366 through STORY-369)
> **Effort**: S (2–3 days total)
> **Dependencies**: None — all changes isolated to gate + export layers
> **Status**: 🔴 READY
> **Created**: 2026-04-03
> **Audit source**: `docs/audit/BACKLOG_STRUCTURAL_AUDIT_2026-04-03.md` (Contamination Analysis section)

---

## Problem

The synthetic data safety infrastructure exists but is **not wired to block**. Three independent
failure modes allow Faker-generated or untagged test data to reach production exports silently:

1. **`data_source_type` defaults to `"unknown"`** (`domain/models.py:294`) and the export gate
   only checks for `"synthetic"` / `"mixed"` — so "unknown" passes through unchecked.

2. **`SyntheticDataBlocker.ensure_safe()`** (`data/synthetic_data_safety.py:284–322`) raises
   `SyntheticDataError` on detection but is **never called** by any exporter.

3. **`ReportReleaseGate.evaluate()`** (`data/report_release_gate.py:168`) appends gate violations
   to its result but callers in `export.py` never check `gate_result.passed` — export proceeds
   regardless of violations.

All three must be fixed together. Fixing any single one in isolation leaves the others open.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-366 | Extend gate to treat `data_source_type="unknown"` as blocked | P0 | XS | 🔴 READY |
| STORY-367 | Wire `SyntheticDataBlocker.ensure_safe()` into `export.py` | P0 | S | 🔴 READY |
| STORY-368 | Add `if not gate_result.passed: raise` guard in `export.py` | P0 | XS | 🔴 READY |
| STORY-369 | Contract tests: gate blocks synthetic/unknown, passes real | P0 | S | 🔴 BLOCKED by 366–368 |

All three implementation stories (366–368) are independent of each other and can be done in any order.
STORY-369 requires 366–368 to be complete.

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Role |
|------|------|------|
| `src/solstein/domain/models.py` | 294 | `data_source_type: str = "unknown"` — default allows bypass |
| `src/solstein/data/report_release_gate.py` | 168–178 | Gate detects synthetic/mixed but not "unknown"; result never enforced |
| `src/solstein/data/synthetic_data_safety.py` | 284–322 | `ensure_safe()` — raises on contamination; currently dead code |
| `src/solstein/api/routers/export.py` | ~41–45 | Calls `gate.evaluate()`, ignores result, exports unconditionally |

---

## Definition of Done

- [ ] `ReportReleaseGate` blocks records with `data_source_type in {"synthetic", "mixed", "unknown"}`
- [ ] `SyntheticDataBlocker.ensure_safe()` is called in `export.py` before any file is written
- [ ] `if not gate_result.passed: raise ExportBlockedError(...)` guard exists in `export.py`
- [ ] Contract test: exporting a company with `data_source_type="synthetic"` raises or returns 4xx
- [ ] Contract test: exporting a company with `data_source_type="unknown"` raises or returns 4xx
- [ ] Contract test: exporting a company with `data_source_type="real"` succeeds
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors
