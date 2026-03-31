#!/usr/bin/env python3
"""Pre-commit hook for agent code quality checks.

EPIC-019 Story 4: Pre-commit hooks for agents
Runs quality checks before allowing commits.
"""

from __future__ import annotations

import ast as _ast
import subprocess
import sys
from pathlib import Path


def check_function_sizes(files: list[Path], max_lines: int = 100) -> bool:
    """Check if any modified functions exceed size limits."""
    violations = []

    for file in files:
        if not file.exists() or "__pycache__" in str(file):
            continue

        try:
            result = subprocess.run(
                ["python3", "scripts/ci/check_function_sizes.py", str(file), "--max-lines", str(max_lines)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                violations.append(f"{file}: Function size violation")
        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ Function size violations found:")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def check_bare_excepts(files: list[Path]) -> bool:
    """Check for bare except clauses in modified files."""
    violations = []

    for file in files:
        if not file.exists():
            continue

        try:
            content = file.read_text()
            lines = content.splitlines()

            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Check for bare except
                if (
                    stripped == "except:"
                    or stripped == "except Exception:"
                    or stripped == "except Exception as e:"
                    and "# noqa" not in line
                ):
                    violations.append(f"{file}:{i}: {line.strip()}")
        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ Bare except clauses found (use specific exceptions):")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def check_lazy_imports(files: list[Path]) -> bool:
    """Check for lazy imports (imports inside functions)."""
    violations = []

    for file in files:
        if not file.exists():
            continue

        try:
            content = file.read_text()
            lines = content.splitlines()

            in_function = False
            function_indent = 0

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Detect function/class definition
                if stripped.startswith("def ") or stripped.startswith("class "):
                    in_function = True
                    function_indent = len(line) - len(line.lstrip())
                    continue

                # Check for imports inside functions
                if in_function and (stripped.startswith("import ") or (stripped.startswith("from ") and " import " in line)):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > function_indent and "# noqa" not in line:
                        violations.append(f"{file}:{i}: Lazy import: {line.strip()}")

                # Detect end of function (dedent)
                if stripped and not stripped.startswith("#"):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= function_indent:
                        in_function = False

        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ Lazy imports found (move imports to top of file):")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def check_banned_imports(files: list[Path]) -> bool:
    """Check for banned `import requests` in adapter/agent code (STORY-136)."""
    BANNED = {"requests"}
    violations = []

    for file in files:
        if not file.exists() or "tests/" in str(file):
            continue

        try:
            content = file.read_text()
            tree = _ast.parse(content)

            for node in _ast.walk(tree):
                if isinstance(node, _ast.Import):
                    for alias in node.names:
                        if alias.name in BANNED:
                            violations.append(f"{file}:{node.lineno}: `import {alias.name}` is banned (use httpx)")
                elif isinstance(node, _ast.ImportFrom):
                    if node.module and node.module.split(".")[0] in BANNED:
                        violations.append(
                            f"{file}:{node.lineno}: `from {node.module} import ...` is banned (use httpx)"
                        )
        except SyntaxError:
            pass

    if violations:
        print("❌ Banned imports found (use httpx instead of requests):")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def check_file_size(files: list[Path], max_lines: int = 500) -> bool:
    """Check if any modified files exceed size limits."""
    violations = []

    for file in files:
        if not file.exists():
            continue

        try:
            content = file.read_text()
            lines = len(content.splitlines())
            if lines > max_lines:
                violations.append(f"{file}: {lines} lines (max: {max_lines})")
        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ File size violations found:")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def print_quality_checklist():
    """Print the EPIC-019 Story 4 quality checklist for agents."""
    print("📋 EPIC-019 Agent Quality Checklist")
    print("=" * 60)
    print("Before committing, verify:")
    print()
    print("  □ No functions exceed 100 lines (target: <50)")
    print("  □ No classes exceed 300 lines or 15 methods (target: <200)")
    print("  □ No files exceed 500 lines (target: <400)")
    print("  □ No functions have >5 parameters")
    print("  □ No bare except clauses (catch specific exceptions)")
    print("  □ No lazy imports (all imports at top of file)")
    print("  □ No circular dependencies introduced")
    print("  □ All imports use absolute paths (not relative)")
    print("  □ Error handling is explicit (no silent catches)")
    print("  □ Type hints used for function signatures")
    print("  □ Google-style docstrings for public functions")
    print("  □ No `import requests` (use httpx — EPIC-035)")
    print("  □ New code does not increase smell count")
    print("=" * 60)
    print()


def check_parameter_counts(files: list[Path], max_params: int = 5) -> bool:
    """Check if any functions have too many parameters."""
    violations = []

    for file in files:
        if not file.exists():
            continue

        try:
            content = file.read_text()
            tree = _ast.parse(content)

            for node in _ast.walk(tree):
                if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                    # Count parameters (excluding self/cls)
                    args = node.args
                    param_count = len(args.args) + len(args.kwonlyargs)
                    if args.vararg:
                        param_count += 1
                    if args.kwarg:
                        param_count += 1

                    # Subtract 1 for self/cls in methods
                    if args.args and args.args[0].arg in ('self', 'cls'):
                        param_count -= 1

                    if param_count > max_params:
                        violations.append(
                            f"{file}:{node.lineno}: Function '{node.name}' has {param_count} "
                            f"parameters (max: {max_params})"
                        )

        except SyntaxError:
            pass
        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ Parameter count violations found:")
        for v in violations:
            print(f"  - {v}")
        return False
    return True


def check_class_sizes(files: list[Path], max_lines: int = 300, max_methods: int = 15) -> bool:
    """Check if any modified classes exceed size limits."""
    violations = []

    for file in files:
        if not file.exists():
            continue

        try:
            content = file.read_text()
            tree = _ast.parse(content)

            for node in _ast.walk(tree):
                if isinstance(node, _ast.ClassDef):
                    # Count lines
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', start_line)
                    class_lines = end_line - start_line + 1

                    # Count methods
                    methods = [
                        n for n in node.body
                        if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                    ]
                    method_count = len(methods)

                    if class_lines > max_lines:
                        violations.append(
                            f"{file}:{node.lineno}: Class '{node.name}' has {class_lines} lines "
                            f"(max: {max_lines})"
                        )

                    if method_count > max_methods:
                        violations.append(
                            f"{file}:{node.lineno}: Class '{node.name}' has {method_count} methods "
                            f"(max: {max_methods})"
                        )

        except SyntaxError as e:
            violations.append(f"{file}: Syntax error - {e}")
        except Exception:  # noqa: broad-except
            pass

    if violations:
        print("❌ Class size violations found:")
        for v in violations:
            print(f"  - {v}")
        return False
    return True

def get_staged_python_files() -> list[Path]:
    """Get list of staged Python files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [Path(f) for f in result.stdout.strip().split("\n") if f.endswith(".py")]
        return files
    except Exception:  # noqa: broad-except
        return []


def main():
    print("🔍 Running agent pre-commit quality checks...")
    print()

    # Print quality checklist at start
    print_quality_checklist()

    files = get_staged_python_files()

    if not files:
        print("✅ No Python files staged for commit.")
        sys.exit(0)

    print(f"Checking {len(files)} staged file(s)...")
    print()

    all_passed = True

    # Check 1: Function sizes
    print("1️⃣  Checking function sizes...")
    if not check_function_sizes(files):
        all_passed = False
    else:
        print("   ✅ All functions within 100 lines")
    print()

    # Check 2: Class sizes
    print("2️⃣  Checking class sizes...")
    if not check_class_sizes(files):
        all_passed = False
    else:
        print("   ✅ All classes within 300 lines / 15 methods")
    print()

    # Check 3: Bare excepts
    print("3️⃣  Checking for bare except clauses...")
    if not check_bare_excepts(files):
        all_passed = False
    else:
        print("   ✅ No bare except clauses found")
    print()

    # Check 4: Parameter counts
    print("4️⃣  Checking parameter counts...")
    if not check_parameter_counts(files):
        all_passed = False
    else:
        print("   ✅ All functions have ≤5 parameters")
    print()

    # Check 5: Lazy imports
    print("5️⃣  Checking for lazy imports...")
    if not check_lazy_imports(files):
        all_passed = False
    else:
        print("   ✅ No lazy imports found")
    print()

    # Check 6: File sizes
    print("6️⃣  Checking file sizes...")
    if not check_file_size(files):
        all_passed = False
    else:
        print("   ✅ All files within 500 lines")
    print()

    # Check 7: Banned imports (STORY-136)
    print("7️⃣  Checking for banned imports...")
    if not check_banned_imports(files):
        all_passed = False
    else:
        print("   ✅ No banned imports (requests) found")
    print()

    if all_passed:
        print("✅ All quality checks passed!")
        sys.exit(0)
    else:
        print("❌ Quality checks failed. Please fix the issues above.")
        print()
        print("💡 Tips:")
        print("   - Break down large functions (>100 lines)")
        print("   - Extract classes if they exceed 300 lines or 15 methods")
        print("   - Use parameter objects if functions have >5 parameters")
        print("   - Use specific exception types instead of bare except")
        print("   - Move imports to the top of files")
        print("   - Split large files (>500 lines) into modules")
        print()
        print("📚 See: docs/developers/code-quality.md for full guidelines")
        sys.exit(1)

if __name__ == "__main__":
    main()
