# STORY-373: Add CI lint guard — no `src/` module may import from `tests.*` or `scripts.*`

**Epic**: EPIC-091 — Test/Production Runtime Separation
**Priority**: P0
**Size**: XS (< 1 hour)
**Status**: 🔴 READY

---

## Context

The boundary between production code (`src/`) and test/script code (`tests/`, `scripts/`) is
currently maintained by convention only. Nothing in CI catches a developer accidentally writing
`from tests.factories import CompanyFactory` inside a production module — which would embed
Faker as a transitive production dependency and create a contamination vector.

This story closes that gap with an automated check that runs in CI and on pre-commit.

---

## Acceptance Criteria

- [ ] A script or ruff rule detects any file under `src/` that contains:
      - `from tests` (any subpath)
      - `from scripts` (any subpath)
      - `import tests` (any subpath)
      - `import scripts` (any subpath)
- [ ] The check is wired into the CI quality suite (`scripts/ci/` or equivalent)
- [ ] The check exits non-zero if violations are found, listing offending files and lines
- [ ] Verified: currently zero violations in `src/` (baseline is clean)
- [ ] Check is documented in the epic management rules or CI README

---

## Technical Notes

**Approach A — simple grep script** (preferred, minimal dependencies):

Create `scripts/ci/check_src_test_imports.py`:
```python
#!/usr/bin/env python3
"""CI guard: no src/ module may import from tests/ or scripts/."""
import sys
from pathlib import Path
import re

SRC_ROOT = Path("src")
PATTERNS = [re.compile(r"^\s*(from|import)\s+(tests|scripts)[\.\s]") for _ in [None]]

violations = []
for py_file in SRC_ROOT.rglob("*.py"):
    for line_no, line in enumerate(py_file.read_text().splitlines(), 1):
        for pat in [re.compile(r"^\s*(from|import)\s+(tests|scripts)[\.\s]")]:
            if pat.match(line):
                violations.append(f"{py_file}:{line_no}: {line.strip()}")

if violations:
    print("FAIL: src/ imports test/script modules:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
print(f"OK: no src/ → tests/scripts imports found ({sum(1 for _ in SRC_ROOT.rglob('*.py'))} files checked)")
```

**Approach B — ruff rule**: Use `ruff`'s `TID251` or a custom `noqa` pattern if preferred.
Approach A is simpler and self-contained.

**Wire into CI**: Add to `scripts/ci/run_quality_checks.py` or `.github/workflows/quality.yml`.
Also add to the pre-commit quick-check list in the rules index.

---

## Definition of Done

- [ ] `scripts/ci/check_src_test_imports.py` exists and is executable
- [ ] Running it against current `src/` exits 0 (zero violations today)
- [ ] CI pipeline runs it (add to existing quality check suite)
- [ ] `pytest` 0 failures, `ruff check` 0 errors
