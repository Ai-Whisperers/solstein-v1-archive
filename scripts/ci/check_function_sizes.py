"""Check function sizes in Python files."""

import argparse
import ast
import sys
from pathlib import Path


def check_function_sizes(filepath: Path, max_lines: int = 100) -> list[dict]:
    """Check for functions exceeding size limit."""
    violations = []

    try:
        content = filepath.read_text()
        tree = ast.parse(content)
    except Exception:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = node.end_lineno - node.lineno if node.end_lineno else 0
            if lines > max_lines:
                violations.append({"file": str(filepath), "name": node.name, "line": node.lineno, "lines": lines})

    return violations


def main():
    parser = argparse.ArgumentParser(description="Check Python function sizes")
    parser.add_argument("--max-lines", type=int, default=100, help="Maximum allowed lines per function")
    parser.add_argument("--fail-on-violation", action="store_true", help="Exit with error if violations found")
    parser.add_argument("files", nargs="*", help="Files to check (default: all in src/)")
    args = parser.parse_args()

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = list(Path("src").rglob("*.py"))

    all_violations = []

    for file in files:
        if "__pycache__" not in str(file):
            violations = check_function_sizes(file, args.max_lines)
            all_violations.extend(violations)

    if all_violations:
        print(f"\n🔴 FUNCTIONS EXCEEDING {args.max_lines} LINES ({len(all_violations)} found):")
        for v in sorted(all_violations, key=lambda x: x["lines"], reverse=True):
            print(f"  {v['lines']:4d} lines | {v['file']}:{v['line']} | {v['name']}")

        if args.fail_on_violation:
            print(f"\n❌ Found {len(all_violations)} functions exceeding {args.max_lines} lines")
            sys.exit(1)
    else:
        print(f"✅ All functions are within {args.max_lines} lines")

    sys.exit(0)


if __name__ == "__main__":
    main()
