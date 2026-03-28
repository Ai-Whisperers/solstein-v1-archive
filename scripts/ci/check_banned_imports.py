#!/usr/bin/env python3
"""CI check: ban `import requests` in adapter and agent code.

STORY-136 (EPIC-035): After migrating to httpx, the `requests` library
must not be imported in any adapter or agent module.  This script scans
all Python files under the given directory (default: src/solstein) and
fails if any file imports `requests` at module level.

Allowed exceptions:
- Files in tests/ (test code may mock requests)
- Files explicitly listed in ALLOWLIST below

Usage:
    python scripts/ci/check_banned_imports.py [--path src/solstein]
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

# Files that are explicitly allowed to import requests
# Legacy data layer files pending future migration
ALLOWLIST: set[str] = {
    "src/solstein/data/sources/news.py",
    "src/solstein/data/sources/funding.py",
    "src/solstein/data/sources/web.py",
    "src/solstein/data/sources/patents.py",
    # These adapters are migrated in STORY-134/135 PRs (pending merge)
    # Remove from allowlist once PRs #183 and #184 are merged
    "src/solstein/adapters/enrichment/news_unified.py",
    "src/solstein/adapters/enrichment/funding_unified.py",
    "src/solstein/adapters/enrichment/website_unified.py",
    "src/solstein/agents/website_agent.py",
}

BANNED_MODULES = {"requests"}


def check_file(filepath: Path, root: Path) -> list[str]:
    """Check a single file for banned imports. Returns list of violation strings."""
    relative = str(filepath.relative_to(root))

    if relative in ALLOWLIST:
        return []

    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in BANNED_MODULES:
                    violations.append(
                        f"  {filepath}:{node.lineno}: `import {alias.name}` is banned "
                        f"(use httpx instead)"
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in BANNED_MODULES:
                violations.append(
                    f"  {filepath}:{node.lineno}: `from {node.module} import ...` is banned "
                    f"(use httpx instead)"
                )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for banned imports")
    parser.add_argument("--path", default="src/solstein", help="Root path to scan")
    args = parser.parse_args()

    root = Path.cwd()
    scan_path = root / args.path

    if not scan_path.exists():
        print(f"Path {scan_path} does not exist")
        return 1

    all_violations: list[str] = []
    file_count = 0

    for py_file in sorted(scan_path.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        file_count += 1
        violations = check_file(py_file, root)
        all_violations.extend(violations)

    if all_violations:
        print(f"Banned import check: scanned {file_count} files, {len(all_violations)} violation(s)")
        print()
        print("The following files import banned libraries:")
        for v in all_violations:
            print(v)
        print()
        print("After EPIC-035, use `httpx` instead of `requests`.")
        print("See docs/developers/async-http-guidelines.md for details.")
        return 1

    print(f"Banned import check: scanned {file_count} files, 0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
