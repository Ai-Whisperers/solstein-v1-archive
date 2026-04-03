# STORY-372: Deduplicate test factory modules — consolidate into one canonical source

**Epic**: EPIC-091 — Test/Production Runtime Separation
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY (can run after STORY-371 or independently)

---

## Context

Two separate modules define `CompanyFactory`:
- `tests/factories.py` (module-level file)
- `tests/factories/__init__.py` (package-level file)

Both exist, both are imported in different test files. This creates an alias risk: depending
on which import is resolved (`from tests.factories import CompanyFactory` vs
`from tests import factories`), the behavior may differ silently — especially if the two
definitions diverge over time (already have different field counts: 27 vs 20+).

The duplication also means STORY-371 must be applied in two places. Future changes to test
data structure will require the same double-maintenance.

---

## Acceptance Criteria

- [ ] Exactly one `CompanyFactory` definition exists in the test suite
- [ ] The canonical location is determined by grepping all test file imports — keep whichever
      path is used by more test files, or prefer `tests/factories.py` (module) over
      `tests/factories/__init__.py` (package) if equal
- [ ] All test files that imported the removed definition are updated to import from the canonical
      module
- [ ] The non-canonical factory file is either deleted or converted to a re-export shim that
      imports from the canonical source (re-export shim is acceptable to avoid breaking external
      references)
- [ ] All tests pass after the consolidation

---

## Technical Notes

**Step 1 — inventory**: Find all imports of both factory modules across the test suite:
```bash
grep -r "from tests.factories" tests/
grep -r "from tests import factories" tests/
grep -r "import factories" tests/
```

**Step 2 — pick canonical**: Keep whichever module has more callers.

**Step 3 — merge differences**: The two factories may have different field sets. Before deleting
one, compare their field lists and ensure the canonical definition includes all unique fields.

**Step 4 — redirect non-canonical**: Either delete or convert to a shim:
```python
# tests/factories/__init__.py (if making tests/factories.py canonical)
from tests.factories import CompanyFactory, FinancialMetricFactory, make_company
__all__ = ["CompanyFactory", "FinancialMetricFactory", "make_company"]
```

Do not leave two divergent implementations. One source of truth only.

---

## Definition of Done

- [ ] Single `CompanyFactory` definition in the test codebase
- [ ] All existing tests continue to import successfully (no `ImportError`)
- [ ] `pytest` 0 failures, `ruff check` 0 errors
