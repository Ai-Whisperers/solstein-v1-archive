# EPIC-093: Production Data Loader Synthetic Tagging

> **Priority**: P0 — Ship Blocker (production pipeline discovers and seeds untagged data into Supabase and scoring today)
> **Stories**: 4 (STORY-378 through STORY-381)
> **Effort**: S (2–3 days total)
> **Dependencies**: EPIC-090 recommended first (gate must block before tagging matters)
> **Status**: 🔴 READY
> **Created**: 2026-04-03
> **Audit source**: `docs/audit/BACKLOG_STRUCTURAL_AUDIT_2026-04-03.md` (Third-Pass section)

---

## Problem

Four **production** code paths load company data from `competitor_data.json` and feed it into
Supabase or the scoring pipeline without setting `data_source_type`. This is separate from the
test-factory contamination addressed in EPIC-091. These are `src/` production modules:

1. **`src/solstein/data/seed_db.py`** (production module, not a script) — loads all companies
   from `competitor_data.json` via `CompetitorDataLoader`, scores them, and writes to Supabase
   via `SupabaseRepository.save()`. No `data_source_type` is ever set. All seeded records land
   with the default `"unknown"`.

2. **`src/solstein/adapters/discovery/competitor_json.py`** — the production pipeline's
   `CompetitorJsonSource.discover()` method instantiates `CompetitorDataLoader` on each call
   and feeds loaded companies as `DiscoveryCandidates` into `run_market_intelligence()`. No
   `data_source_type` is propagated from loader to pipeline. Every market intelligence run
   seeds untagged records from this source.

3. **`src/solstein/data/competitor_loader.py:107–115`** — the module-level `_loader_instance`
   singleton caches loaded companies. The cache is never invalidated between production and
   test calls in the same process. `convert_to_domain_company()` (called at line 84) does not
   set `data_source_type`, so all loaded companies default to `"unknown"`.

4. **`src/solstein/migrations/load_competitor_data.py:77`** — the migration script builds
   `CompanyRecord` objects with `data_source="competitor_data.json"` (a free-text string) but
   no `data_source_type` field, making migrated records indistinguishable from real data by
   the export gate.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-378 | Fix `src/solstein/data/seed_db.py` — set `data_source_type` before `repo.save()` | P0 | XS | 🔴 READY |
| STORY-379 | Fix `competitor_loader.py` — `convert_to_domain_company()` must tag loaded companies; clear singleton cache API | P0 | S | 🔴 READY |
| STORY-380 | Fix `CompetitorJsonSource.discover()` — propagate `data_source_type` from loader into pipeline candidates | P0 | S | 🔴 READY |
| STORY-381 | Fix `load_competitor_data.py` migration — set `data_source_type` on all `CompanyRecord` objects built | P0 | XS | 🔴 READY |

All four stories are independent of each other.

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Issue |
|------|------|-------|
| `src/solstein/data/seed_db.py` | 21–31 | Seeds Supabase via `CompetitorDataLoader` + `SupabaseRepository`, no `data_source_type` |
| `src/solstein/adapters/discovery/competitor_json.py` | 41–44 | Production discovery uses `CompetitorDataLoader`, no type propagation |
| `src/solstein/data/competitor_loader.py` | 82–88, 107–115 | `convert_to_domain_company()` drops type; singleton cache never cleared |
| `src/solstein/migrations/load_competitor_data.py` | 53–80 | `_build_company_record()` sets `data_source` (string) but not `data_source_type` |

---

## Definition of Done

- [ ] `seed_db.py` sets `data_source_type` on every company before saving; value determined by
      the source file's known provenance (if loading from `tests/fixtures/`, tag `"synthetic"`;
      if from `data/input/` with a real-data manifest, tag `"real"`)
- [ ] `competitor_loader._load_from_json()` propagates or derives `data_source_type` for all
      loaded companies; a `clear_cache()` method is exposed and tested
- [ ] `CompetitorJsonSource.discover()` passes `data_source_type` from loaded companies into
      the pipeline so downstream scoring can gate on it
- [ ] `_build_company_record()` in the migration sets `data_source_type`; if the column does
      not exist on `CompanyRecord`, add it as part of this story
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors
