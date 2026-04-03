# STORY-379: Fix `competitor_loader.py` — tag loaded companies; expose cache-clear API

**Epic**: EPIC-093 — Production Loader Synthetic Tagging
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY

---

## Context

`CompetitorDataLoader._load_from_json()` at `src/solstein/data/competitor_loader.py:82–88`
calls `convert_to_domain_company(comp, i)` for each JSON entry. The converter does not set
`data_source_type`, so all loaded companies default to `"unknown"`.

Additionally, the module-level `_loader_instance` singleton at line 107 holds a `_cache` dict
that persists for the lifetime of the process. Tests that call `load_companies()` with test data
populate this cache. Any subsequent call — including production calls — returns the cached result.

The `clear_cache()` method exists (line 97) but only clears `self._cache` on the instance —
it does not reset `_loader_instance` to `None`, so `get_loader()` will still return the
same instance with a now-empty cache but all the same state.

---

## Acceptance Criteria

- [ ] `_load_from_json()` sets `data_source_type` on each loaded `Company` object based on
      the source file path:
      - Path contains `tests/fixtures/` or `synthetic` → `"synthetic"`
      - Path is `data/input/competitor_data.json` → `"real"` (or configurable via param)
      - All other paths → raise `ValueError` or set `"unknown"` with a warning log
- [ ] A module-level `reset_loader()` function is added that sets `_loader_instance = None`,
      allowing tests to fully reset the singleton between test runs
- [ ] The `clear_cache()` instance method also calls `reset_loader()` (or the module exposes
      both independently and tests use `reset_loader()`)
- [ ] `tests/conftest.py` `mock_competitor_data` fixture uses `reset_loader()` in teardown

---

## Technical Notes

**File**: `src/solstein/data/competitor_loader.py`

**Tagging pattern** in `_load_from_json`:
```python
def _load_from_json(self, json_path: Path, limit=None) -> list[Company]:
    source_type = _infer_source_type(json_path)
    ...
    for comp in competitors:
        company = convert_to_domain_company(comp, i)
        company.data_source_type = source_type   # tag at load time
        companies.append(company)
    return companies

def _infer_source_type(path: Path) -> str:
    parts = str(path).lower()
    if "tests/fixtures" in parts or "synthetic" in parts:
        return "synthetic"
    if "data/input" in parts:
        return "real"
    logger.warning(f"Unknown data source path: {path} — defaulting to 'unknown'")
    return "unknown"
```

**Reset function** (add after `get_loader()`):
```python
def reset_loader() -> None:
    """Reset the global loader singleton. Use in tests to ensure clean state."""
    global _loader_instance
    _loader_instance = None
```

---

## Definition of Done

- [ ] Every company loaded via `_load_from_json()` has `data_source_type` set (not `"unknown"`)
- [ ] `reset_loader()` exists and is called in `conftest.py`'s `mock_competitor_data` teardown
- [ ] Unit test: loading from a path containing `"synthetic"` → companies have `data_source_type="synthetic"`
- [ ] Unit test: loading from `data/input/` path → companies have `data_source_type="real"`
- [ ] `pytest` 0 failures, `ruff check` 0 errors
