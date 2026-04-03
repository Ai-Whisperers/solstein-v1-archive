# EPIC-091: Test/Production Runtime Separation

> **Priority**: P0 — Ship Blocker (synthetic data enters production DB untagged today)
> **Stories**: 4 (STORY-370 through STORY-373)
> **Effort**: S (2–3 days total)
> **Dependencies**: EPIC-090 recommended first (gate must enforce before boundary matters)
> **Status**: 🔴 READY
> **Created**: 2026-04-03
> **Audit source**: `docs/audit/BACKLOG_STRUCTURAL_AUDIT_2026-04-03.md` (Contamination Analysis section)

---

## Problem

Three boundary violations allow test-time synthetic data to contaminate the production runtime:

1. **`scripts/seed_db.py`** uses `Faker()` to generate company data and writes directly to the
   production database via `CompanyRepository` + `get_async_session()`. It never sets
   `data_source_type="synthetic"`, so records default to `"unknown"` and pass any gate that
   only checks for `"synthetic"`.

2. **Two duplicate test factory modules** (`tests/factories.py` and `tests/factories/__init__.py`)
   both define `CompanyFactory` using `factory.faker.Faker` with 20–27 fields. Neither sets
   `data_source_type="synthetic"` as a factory default. The duplication is itself an alias risk:
   import order changes can silently switch which factory is resolved.

3. **No CI enforcement** prevents `src/` production modules from importing `tests.*` or
   `scripts.*`. The boundary is currently maintained by convention only.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-370 | Fix `seed_db.py` — tag all seeded records as `data_source_type="synthetic"` | P0 | XS | 🔴 READY |
| STORY-371 | Fix test factories — add `data_source_type="synthetic"` default to all factory classes | P0 | XS | 🔴 READY |
| STORY-372 | Deduplicate test factory modules — consolidate into one canonical source | P0 | S | 🔴 READY |
| STORY-373 | Add CI lint guard: no `src/` module may import from `tests.*` or `scripts.*` | P0 | XS | 🔴 READY |

All four stories are independent of each other and can be worked in any order.

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Role |
|------|------|------|
| `scripts/seed_db.py` | 20, 26, 51–90 | Faker import; `generate_company()` never sets `data_source_type` |
| `scripts/seed_db.py` | 99–119 | Direct `CompanyRepository.save()` call to production DB |
| `tests/factories.py` | 20–22, 44–90 | Factory-boy `CompanyFactory` — no `data_source_type` default |
| `tests/factories/__init__.py` | 34–35, 64–99 | Duplicate `CompanyFactory` — same omission |
| `tests/test_data.py` | 10–109 | Three hand-coded companies, none tagged synthetic |
| `tests/conftest.py` | 31–32, 64–86 | `mock_company` + `mock_repo` fixtures using untagged factories |

---

## Definition of Done

- [ ] `seed_db.py` sets `data_source_type="synthetic"` on every company it generates before saving
- [ ] `tests/factories.py` `CompanyFactory` and `FinancialMetricFactory` both default to `data_source_type="synthetic"`
- [ ] `tests/factories/__init__.py` `CompanyFactory` also defaults to `data_source_type="synthetic"`
- [ ] Single canonical test factory module — no duplicate `CompanyFactory` definitions
- [ ] CI script/check raises if any file under `src/` contains `from tests.` or `from scripts.` or `import tests.` or `import scripts.`
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors
