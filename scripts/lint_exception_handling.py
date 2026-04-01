#!/usr/bin/env python3
"""Policy lint check for broad exception handling.

F4: CI fails on new untyped broad catches in critical modules.
Scans Python files for prohibited exception handling patterns.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    """Represents a policy violation."""

    file: Path
    line: int
    column: int
    pattern: str
    message: str
    severity: str = "error"


class ExceptionHandlingChecker(ast.NodeVisitor):
    """AST visitor to check for broad exception handling."""

    # Prohibited patterns
    BARE_EXCEPT = "bare_except"
    EXCEPT_EXCEPTION = "except_exception"
    EXCEPT_BASE_EXCEPTION = "except_base_exception"

    # Severity levels
    CRITICAL_MODULES = {
        "worker_tasks.py",
        "github_agent.py",
        "enrichment.py",
        "unified_loader.py",
        "scoring.py",
        "classification_service.py",
        "export.py",
        "celery_config.py",
    }

    def __init__(self, file_path: Path, critical_only: bool = False) -> None:
        self.file_path = file_path
        self.violations: list[Violation] = []
        self.critical_only = critical_only
        self.is_critical = file_path.name in self.CRITICAL_MODULES

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        """Check exception handler for broad catches."""
        # Skip if not critical and we're in critical-only mode
        if self.critical_only and not self.is_critical:
            return

        if node.type is None:
            # Bare except:
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    pattern=self.BARE_EXCEPT,
                    message="Bare 'except:' is prohibited. Use specific exceptions.",
                    severity="error" if self.is_critical else "warning",
                )
            )
        elif isinstance(node.type, ast.Name):
            if node.type.id == "Exception":
                self.violations.append(
                    Violation(
                        file=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        pattern=self.EXCEPT_EXCEPTION,
                        message="'except Exception:' is too broad. Use specific exceptions.",
                        severity="error" if self.is_critical else "warning",
                    )
                )
            elif node.type.id == "BaseException":
                self.violations.append(
                    Violation(
                        file=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        pattern=self.EXCEPT_BASE_EXCEPTION,
                        message="'except BaseException:' is too broad. Use specific exceptions.",
                        severity="error",
                    )
                )
        elif isinstance(node.type, ast.Tuple):
            # Check for (Exception, ...) patterns
            for elt in node.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                    self.violations.append(
                        Violation(
                            file=self.file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            pattern=self.EXCEPT_EXCEPTION,
                            message=f"'except ... {elt.id} ...:' is too broad. Use specific exceptions.",
                            severity="error" if self.is_critical else "warning",
                        )
                    )

        # Continue visiting child nodes
        self.generic_visit(node)


def check_file(file_path: Path, critical_only: bool = False) -> list[Violation]:
    """Check a single Python file for violations.

    Args:
        file_path: Path to the Python file
        critical_only: Only check critical modules

    Returns:
        List of violations found
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except SyntaxError as e:
        return [
            Violation(
                file=file_path,
                line=e.lineno or 1,
                column=e.offset or 0,
                pattern="syntax_error",
                message=f"Syntax error: {e}",
                severity="error",
            )
        ]
    except Exception as e:
        return [
            Violation(
                file=file_path,
                line=1,
                column=0,
                pattern="read_error",
                message=f"Could not read file: {e}",
                severity="error",
            )
        ]

    checker = ExceptionHandlingChecker(file_path, critical_only)
    checker.visit(tree)
    return checker.violations


def check_directory(
    directory: Path,
    exclude_patterns: set[str] | None = None,
    critical_only: bool = False,
) -> list[Violation]:
    """Check all Python files in a directory.

    Args:
        directory: Directory to scan
        exclude_patterns: Patterns to exclude (e.g., {"test_", "__pycache__"})
        critical_only: Only check critical modules

    Returns:
        List of all violations found
    """
    if exclude_patterns is None:
        exclude_patterns = {"__pycache__", ".git", ".venv", "venv", "node_modules"}

    violations: list[Violation] = []

    for file_path in directory.rglob("*.py"):
        # Skip excluded directories
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue

        file_violations = check_file(file_path, critical_only)
        violations.extend(file_violations)

    return violations


def format_violation(violation: Violation) -> str:
    """Format a violation for display."""
    return f"{violation.file}:{violation.line}:{violation.column} [{violation.severity.upper()}] {violation.message}"


def main() -> int:
    """Main entry point for the lint check.

    Returns:
        Exit code (0 for success, 1 for violations found)
    """
    parser = argparse.ArgumentParser(
        description="Lint check for broad exception handling patterns",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Files or directories to check",
    )
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Only check critical modules",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=["__pycache__", ".git", ".venv", "venv"],
        help="Patterns to exclude",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "github"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat warnings as failures",
    )

    args = parser.parse_args()

    all_violations: list[Violation] = []
    exclude_set = set(args.exclude)

    for path in args.paths:
        if path.is_file():
            all_violations.extend(check_file(path, args.critical_only))
        elif path.is_dir():
            all_violations.extend(check_directory(path, exclude_set, args.critical_only))
        else:
            print(f"Warning: {path} does not exist", file=sys.stderr)

    # Sort by file and line
    all_violations.sort(key=lambda v: (str(v.file), v.line, v.column))

    # Output results
    if args.format == "json":
        import json

        output = [
            {
                "file": str(v.file),
                "line": v.line,
                "column": v.column,
                "pattern": v.pattern,
                "message": v.message,
                "severity": v.severity,
            }
            for v in all_violations
        ]
        print(json.dumps(output, indent=2))
    elif args.format == "github":
        # GitHub Actions annotation format
        for v in all_violations:
            level = "error" if v.severity == "error" else "warning"
            print(f"::{level} file={v.file},line={v.line},col={v.column}::{v.message} ({v.pattern})")
    else:
        # Text format
        if all_violations:
            print(f"Found {len(all_violations)} violation(s):\n")
            for v in all_violations:
                print(format_violation(v))
        else:
            print("No violations found!")

    # Determine exit code
    errors = [v for v in all_violations if v.severity == "error"]
    warnings = [v for v in all_violations if v.severity == "warning"]

    if errors:
        return 1
    if args.fail_on_warning and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
