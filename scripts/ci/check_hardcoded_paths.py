#!/usr/bin/env python3
"""CI guard: fail the build if any tracked file contains a hardcoded /home/ path.

Usage:
    python scripts/ci/check_hardcoded_paths.py [--root <project-root>]

Returns exit code 0 when clean, non-zero when violations are found.

Why this matters:
    Hardcoded absolute paths (e.g. /home/ai-whisperers/solstein) mean the code
    only works on the original developer's machine.  Any CI runner, staging
    environment, or colleague's workstation will fail immediately.  This check
    catches regressions before they are committed.

What is allowed:
    - Template files (*.template) may contain ${PROJECT_ROOT} placeholders.
    - Comments that explain why a path was removed are fine (/home/ must not
      appear in an actual string literal or assignment that is evaluated).
    - This script itself is excluded from the check.
"""

import argparse
import sys
from pathlib import Path

# File extensions / names that are expected to contain /home/ placeholders
ALLOWED_PATTERNS: list[str] = [
    "*.template",  # systemd service/timer templates
    "check_hardcoded_paths.py",  # this script itself
]

# Directories that are always excluded from the scan
EXCLUDE_DIRS: list[str] = [
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "node_modules",
    ".analysis-output",
]


def _is_allowed(file_path: Path) -> bool:
    """Return True if this file is exempt from the check."""
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return any(file_path.match(pattern) for pattern in ALLOWED_PATTERNS)


# Directories within the project root that are in scope for the check.
# Markdown docs and backlog files may legitimately reference /home/ paths as historical records.
IN_SCOPE_DIRS: list[str] = ["src", "bin", "scripts"]


def scan(root: Path, scope_dirs: list[str] | None = None) -> list[tuple[Path, int, str]]:
    """Scan tracked files for hardcoded /home/ paths.

    Only files under ``scope_dirs`` (default: src/, bin/, scripts/) are examined.
    Documentation files may legitimately reference old paths as historical records.

    Returns a list of (file, line_number, line_content) tuples for each hit.
    """
    effective_scope = scope_dirs if scope_dirs is not None else IN_SCOPE_DIRS

    # Collect candidate files
    candidates: list[Path] = []
    for scope_dir in effective_scope:
        target = root / scope_dir
        if target.is_dir():
            candidates.extend(target.rglob("*"))

    violations: list[tuple[Path, int, str]] = []

    for file_path in candidates:
        if not file_path.is_file():
            continue
        if _is_allowed(file_path):
            continue

        try:
            lines = file_path.read_text(errors="replace").splitlines()
        except OSError:
            continue

        for lineno, line in enumerate(lines, start=1):
            if "/home/" in line:
                violations.append((file_path.relative_to(root), lineno, line.strip()))

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for hardcoded /home/ paths in src/, bin/, scripts/")
    parser.add_argument("--root", type=Path, default=None, help="Project root (defaults to this script's grandparent)")
    args = parser.parse_args()

    root = args.root or Path(__file__).resolve().parent.parent.parent

    violations = scan(root)

    if not violations:
        print("PASS: No hardcoded /home/ paths found in tracked files.")
        return 0

    print(f"FAIL: {len(violations)} hardcoded /home/ path(s) found:\n")
    for file_path, lineno, content in violations:
        print(f"  {file_path}:{lineno}  {content}")
    print()
    print("Fix: replace hardcoded paths with dynamic resolution:")
    print("  Python:  Path(__file__).resolve().parent.parent")
    print('  Shell:   $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)')
    print("  Systemd: generate from *.service.template via scripts/install-service.sh")
    return 1


if __name__ == "__main__":
    sys.exit(main())
