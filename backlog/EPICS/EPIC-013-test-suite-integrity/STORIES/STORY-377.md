# STORY-377: Add CI guard detecting module-scope mutations in test files

**Epic**: EPIC-092 — Test Isolation
**Priority**: P0
**Size**: S (2–4 hours)
**Status**: 🔴 READY

---

## Context

STORY-374 and STORY-375 fix the existing module-scope mutations. This story adds a CI check
that prevents them from re-appearing. Without it, any developer can add `os.environ[...] = ...`
at module scope in a new test file and the contamination is silently re-introduced.

The check should detect patterns that are fundamentally unsafe at module scope in test files:
- `os.environ["KEY"] = ...` (env mutation without monkeypatch)
- `app.dependency_overrides[...] = ...` (dependency injection bypass)
- `get_settings()` called and result mutated (settings singleton poisoning)
- `sys.path.insert(...)` or `sys.path.append(...)` (import path manipulation)

---

## Acceptance Criteria

- [ ] A script `scripts/ci/check_test_module_scope_mutations.py` exists
- [ ] It scans all `tests/**/*.py` files and detects the dangerous patterns listed above
- [ ] It exits non-zero listing offending file:line when violations are found
- [ ] After STORY-374 and STORY-375 are complete, running this script against current `tests/`
      exits 0 (clean baseline)
- [ ] The script is added to the CI quality check suite

---

## Technical Notes

**Detection approach** — AST-based (preferred over regex):

Parse each test file's AST. Flag any `ast.Assign` or `ast.Subscript` node that matches the
dangerous patterns AND is at module scope (i.e., not inside a function, class, or `if` block).

```python
import ast
import sys
from pathlib import Path

DANGEROUS_CALLS = {"get_settings", "app.dependency_overrides"}
DANGEROUS_ATTRS = {"environ"}   # os.environ assignments

violations = []
for py_file in Path("tests").rglob("*.py"):
    tree = ast.parse(py_file.read_text())
    for node in ast.walk(tree):
        # Only check module-level statements (direct children of Module)
        ...
```

A simpler but less precise approach: use `grep` for the patterns limited to lines that have
less than 4 spaces of indentation (module-level lines):
```python
import re
MODULE_SCOPE_ENV = re.compile(r"^os\.environ\[")
MODULE_SCOPE_OVERRIDE = re.compile(r"^app\.dependency_overrides\[")
```

**Note**: The script should have a `# noqa: test-isolation-ok` escape hatch for any intentional
module-scope patterns that are genuinely safe (e.g., `os.environ.get(...)` reads are fine).

---

## Definition of Done

- [ ] `scripts/ci/check_test_module_scope_mutations.py` exists and is executable
- [ ] Zero violations on current clean test suite (after STORY-374 + 375)
- [ ] Wired into CI quality suite
- [ ] `pytest` and `ruff check` at 0 errors/failures
