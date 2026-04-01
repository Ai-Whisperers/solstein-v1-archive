#!/usr/bin/env python3
"""Check that shared/ package has zero imports from application layers.

STORY-117: Enforces the import graph rule that shared/ must only
import from the standard library and third-party packages.

Exit code 0 = clean, 1 = violations found.
"""

import ast
import sys
from pathlib import Path

SRC = Path("src/solstein")
SHARED_DIR = SRC / "shared"

# Application-layer packages that shared/ must NOT import from
FORBIDDEN_LAYERS = {
    "api",
    "application",
    "domain",
    "analytics",
    "infrastructure",
    "research",
    "intelligence",
    "data",
    "connectors",
    "evidence",
    "exporters",
    "extractors",
    "validation",
    "worker",
    "core",
    "llm",
    "monitoring",
    "observability",
    "notifications",
    "security",
    "tenant",
    "agents",
    "adapters",
}


def _check_import_from(node: ast.ImportFrom, rel: Path) -> str | None:
    """Check a 'from X import Y' node for forbidden imports."""
    if not node.module or not node.module.startswith("solstein."):
        return None
    target = node.module.split(".")[1]
    if target in FORBIDDEN_LAYERS:
        return f"{rel}:{node.lineno} imports from solstein.{target} (forbidden)"
    return None


def _check_import(node: ast.Import, rel: Path) -> list[str]:
    """Check an 'import X' node for forbidden imports."""
    violations = []
    for alias in node.names:
        if alias.name.startswith("solstein."):
            target = alias.name.split(".")[1]
            if target in FORBIDDEN_LAYERS:
                violations.append(
                    f"{rel}:{node.lineno} imports solstein.{target} (forbidden)"
                )
    return violations


def _scan_file(py_file: Path, src_root: Path) -> list[str]:
    """Scan a single Python file for forbidden imports."""
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    violations = []
    rel = py_file.relative_to(src_root)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            violation = _check_import_from(node, rel)
            if violation:
                violations.append(violation)
        elif isinstance(node, ast.Import):
            violations.extend(_check_import(node, rel))
    return violations


def check_shared_purity() -> list[str]:
    """Return list of violations (empty = clean)."""
    if not SHARED_DIR.exists():
        return [f"shared/ directory not found at {SHARED_DIR}"]

    violations = []
    for py_file in sorted(SHARED_DIR.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        violations.extend(_scan_file(py_file, SRC))
    return violations


def main() -> int:
    """Run purity check and print results."""
    violations = check_shared_purity()
    if violations:
        print("SHARED PURITY VIOLATIONS:")
        for v in violations:
            print(f"  {v}")
        print(f"\n{len(violations)} violation(s) found.")
        return 1

    print("shared/ package: clean (zero application-layer imports)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
