"""Check file sizes in Python codebase."""

import argparse
import sys
from pathlib import Path


def check_file_sizes(max_lines: int = 500, warn_lines: int = 400) -> tuple[list[Path], list[Path]]:
    """Check for files exceeding size limits."""
    violations = []
    warnings = []

    for file in Path("src").rglob("*.py"):
        if "__pycache__" in str(file):
            continue

        try:
            lines = len(file.read_text().split("\n"))
            if lines > max_lines:
                violations.append((file, lines))
            elif lines > warn_lines:
                warnings.append((file, lines))
        except Exception:
            pass

    return violations, warnings


def main():
    parser = argparse.ArgumentParser(description="Check Python file sizes")
    parser.add_argument("--max-lines", type=int, default=500, help="Maximum allowed lines per file")
    parser.add_argument("--warn-lines", type=int, default=400, help="Warning threshold for file size")
    args = parser.parse_args()

    violations, warnings = check_file_sizes(args.max_lines, args.warn_lines)

    has_error = False

    if violations:
        print(f"\n🔴 FILES EXCEEDING {args.max_lines} LINES ({len(violations)} found):")
        for file, lines in sorted(violations, key=lambda x: x[1], reverse=True):
            print(f"  {lines:5d} lines | {file}")
        has_error = True

    if warnings:
        print(f"\n🟡 FILES APPROACHING LIMIT ({len(warnings)} found):")
        for file, lines in sorted(warnings, key=lambda x: x[1], reverse=True):
            print(f"  {lines:5d} lines | {file}")

    if not violations and not warnings:
        print(f"✅ All files are within {args.max_lines} lines")

    if has_error:
        print("\n⚠️  Consider splitting large files into smaller modules")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
