# STORY-371: Fix test factories — add `data_source_type="synthetic"` default to all factory classes

**Epic**: EPIC-091 — Test/Production Runtime Separation
**Priority**: P0
**Size**: XS (< 1 hour)
**Status**: 🔴 READY

---

## Context

Two test factory modules define `CompanyFactory` using `factory.faker.Faker` with 20–27 fields.
Neither sets `data_source_type="synthetic"` as a factory default. Any test that uses these
factories creates Company objects tagged `"unknown"`, which will now be blocked by the export
gate (EPIC-090) when they flow through export tests.

**Files**:
- `tests/factories.py:56–90` — `CompanyFactory`, `FinancialMetricFactory`
- `tests/factories/__init__.py:64–99` — duplicate `CompanyFactory`

Both must be fixed. STORY-372 will later consolidate the two into one module, but fixing the
default now unblocks export tests without waiting for the consolidation.

---

## Acceptance Criteria

- [ ] `CompanyFactory` in `tests/factories.py` has `data_source_type = "synthetic"` as a
      class-level field (not computed, not Faker — a literal default)
- [ ] `CompanyFactory` in `tests/factories/__init__.py` has the same default
- [ ] `FinancialMetricFactory` in `tests/factories.py` is verified — if it has `data_source_type`,
      set it to `"synthetic"`; if `FinancialMetric` has no such field, skip
- [ ] All existing tests that use `make_company()` or `CompanyFactory()` continue to pass
- [ ] Export tests that use `mock_company` fixture continue to pass (and no longer create
      "unknown" records that would be blocked by EPIC-090 gate)

---

## Technical Notes

**factory-boy syntax for a literal default**:
```python
class CompanyFactory(factory.Factory):
    class Meta:
        model = Company
    
    data_source_type = "synthetic"   # literal, not factory.Faker(...)
    name = factory.Faker("company")
    # ... rest of fields
```

**Read first**: Check both factory files to confirm the exact class structure and Meta model.
Also check whether `FinancialMetric` (in `domain/models.py`) has a `data_source_type` field
before adding it to `FinancialMetricFactory`.

---

## Definition of Done

- [ ] Both `CompanyFactory` definitions default to `data_source_type="synthetic"`
- [ ] `pytest` passes with 0 failures, `ruff check` 0 errors
