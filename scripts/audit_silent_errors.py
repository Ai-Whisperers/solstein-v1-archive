#!/usr/bin/env python3
"""Audit codebase for silent exception handling.

This script scans the codebase for patterns that silently swallow exceptions:
- bare `except:`
- `except Exception: pass`
- `except Exception:` with no logging

Usage:
    python scripts/audit_silent_errors.py

Exit codes:
    0 - No silent exception handlers found
    1 - Silent exception handlers detected
"""

import ast
import sys
from pathlib import Path


class SilentExceptionVisitor(ast.NodeVisitor):
    """Find silent exception handlers."""

    def __init__(self):
        self.silent_handlers: list[tuple[int, str]] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # Check for bare 'except:' or 'except Exception:'
        is_broad = (
            node.type is None  # bare except
            or (isinstance(node.type, ast.Name) and node.type.id == "Exception")
            or (
                isinstance(node.type, ast.Tuple)
                and any(isinstance(elt, ast.Name) and elt.id == "Exception" for elt in node.type.elts)
            )
        )

        if is_broad:
            # Check if body is empty, pass, or just returns None
            body = node.body
            is_silent = (
                len(body) == 0
                or (len(body) == 1 and isinstance(body[0], ast.Pass))
                or (
                    len(body) == 1
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and body[0].value.value is None
                )
                or (
                    len(body) == 1
                    and isinstance(body[0], ast.Return)
                    and (
                        body[0].value is None
                        or (isinstance(body[0].value, ast.Constant) and body[0].value.value is None)
                    )
                )
            )

            if is_silent:
                self.silent_handlers.append((node.lineno, "silent"))
            else:
                # Check if there's any logging in the handler
                has_logging = any(
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and stmt.value.func.attr in ("debug", "info", "warning", "error", "exception", "critical")
                    for stmt in body
                )
                if not has_logging:
                    self.silent_handlers.append((node.lineno, "no-log"))

        self.generic_visit(node)


def audit_file(filepath: Path) -> list[tuple[int, str]]:
    """Audit a single file for silent exception handling."""
    try:
        tree = ast.parse(filepath.read_text())
    except SyntaxError:
        return []

    visitor = SilentExceptionVisitor()
    visitor.visit(tree)
    return visitor.silent_handlers


def main():
    """Run audit on src directory."""
    src_dir = Path("src/solstein")
    if not src_dir.exists():
        print(f"Error: {src_dir} not found")
        sys.exit(1)

    issues = []

    for py_file in src_dir.rglob("*.py"):
        if "test" in py_file.name or "__pycache__" in str(py_file):
            continue

        findings = audit_file(py_file)
        for lineno, issue_type in findings:
            issues.append((py_file, lineno, issue_type))

    if issues:
        print(f"Found {len(issues)} potential silent exception handlers:")
        print()
        for filepath, lineno, issue_type in issues:
            print(f"  {filepath}:{lineno} ({issue_type})")
        print()
        print("Fix these by adding proper logging or using specific exceptions.")
        print("See docs/epics/EPIC-018-OBSERVABILITY-REFACTOR/exception-handling-guide.md")
        sys.exit(1)
    else:
        print("✓ No silent exception handlers found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
