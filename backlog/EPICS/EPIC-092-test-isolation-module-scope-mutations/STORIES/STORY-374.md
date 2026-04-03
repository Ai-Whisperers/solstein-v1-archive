# STORY-374: Fix `test_api_routers_coverage.py` — move module-scope mutations into fixtures

**Epic**: EPIC-092 — Test Isolation
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY

---

## Context

`tests/unit/test_api_routers_coverage.py` lines 19–25 execute three mutations at **module import
time** with no cleanup. These affect the production `app` object and process environment for every
subsequent test in the session:

```python
# Line 20-21: permanent for the entire test session
app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
app.dependency_overrides[get_current_tenant] = lambda: {"tenant_id": "test-tenant", "name": "Test Tenant"}

# Line 23-24: Settings singleton mutated globally
_settings = get_settings()
_settings.api.require_api_key = False

# Line 25: env var never reset
os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"] = "true"
```

Note that `get_company_repository` IS handled correctly in the `mock_repo` fixture (lines 40–42)
with proper `yield` + `pop()` cleanup — that pattern must be extended to the three above.

---

## Acceptance Criteria

- [ ] `app.dependency_overrides[get_current_user]` and `[get_current_tenant]` are set/removed
      inside an `autouse` fixture scoped to the module (not at module level)
- [ ] `_settings.api.require_api_key = False` uses `monkeypatch.setattr` so it auto-restores
- [ ] `os.environ["SOLSTEIN_DISABLE_RATE_LIMIT"] = "true"` uses `monkeypatch.setenv` so it
      auto-restores
- [ ] No module-level code executes outside import statements and class/function definitions
- [ ] All 21 existing tests in the file still pass after the restructuring

---

## Technical Notes

**Pattern** — convert module-scope mutations to an `autouse` fixture:

```python
@pytest.fixture(autouse=True, scope="module")
def _setup_auth_overrides(monkeypatch):
    app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
    app.dependency_overrides[get_current_tenant] = lambda: {"tenant_id": "test-tenant", "name": "Test Tenant"}
    monkeypatch.setattr(_settings, "api.require_api_key", False)  # auto-restored
    monkeypatch.setenv("SOLSTEIN_DISABLE_RATE_LIMIT", "true")     # auto-restored
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_tenant, None)
```

**Caution**: `monkeypatch` with `scope="module"` requires `pytest >= 6.2`. Verify the pytest
version in `pyproject.toml` before using module-scoped `monkeypatch`.

---

## Definition of Done

- [ ] Zero module-scope mutations in `test_api_routers_coverage.py`
- [ ] All overrides are cleaned up after the module's tests complete
- [ ] `pytest tests/unit/test_api_routers_coverage.py` passes at 0 failures
- [ ] `ruff check tests/unit/test_api_routers_coverage.py` at 0 errors
