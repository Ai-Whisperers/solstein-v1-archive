#!/usr/bin/env python3
"""CI gate: no Python scripts in project root (except config files).

Prevents bypass scripts (run_*.py) from reappearing in the project root.
Only configuration files (pyproject.toml, setup.py, setup.cfg, conftest.py)
are allowed.

Usage:
    python scripts/ci/check_root_scripts.py

Exit codes:
    0 — no forbidden scripts found
    1 — forbidden .py files found in project root
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Files allowed in project root
ALLOWED_ROOT_PY = {
    "conftest.py",
    "setup.py",
    "setup.cfg",
}


def check_root_scripts() -> int:
    """Check for unauthorized Python scripts in project root.

    Returns:
        0 if no violations found, 1 otherwise.
    """
    violations = []

    for path in PROJECT_ROOT.glob("*.py"):
        if path.name not in ALLOWED_ROOT_PY:
            violations.append(path.name)

    if violations:
        print("ERROR: Forbidden Python scripts found in project root:")
        for name in sorted(violations):
            print(f"  - {name}")
        print()
        print("Python scripts must live in src/ or scripts/, not in the project root.")
        print("Configuration files (conftest.py, setup.py) are exempt.")
        print("See: docs/active/backlog/EPIC-027-cicd-automation/STORIES/STORY-100-delete-bypass-scripts.md")
        return 1

    print("OK: No unauthorized Python scripts in project root.")
    return 0


if __name__ == "__main__":
    sys.exit(check_root_scripts())
