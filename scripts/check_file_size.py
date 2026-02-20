#!/usr/bin/env python3
"""
Script to check for 'God Files' that exceed line count limits.
"""
import os
import sys
from pathlib import Path

# Configuration
MAX_LINES = 400
EXCLUDE_DIRS = ["venv", ".git", "__pycache__", ".ruff_cache", "migrations"]
EXCLUDE_FILES = []

def count_lines(filepath: Path) -> int:
    """Count lines in file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return len(f.readlines())
    except Exception:
        return 0

def check_files(root_dir: Path) -> list[tuple[Path, int]]:
    """Recursively check files in directory."""
    violations = []

    for root, dirs, files in os.walk(root_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            if file in EXCLUDE_FILES:
                continue

            filepath = Path(root) / file
            lines = count_lines(filepath)

            if lines > MAX_LINES:
                violations.append((filepath, lines))

    return violations

def main():
    """Main execution."""
    root_dir = Path("src")
    if not root_dir.exists():
        print("Error: 'src' directory not found.")
        sys.exit(1)

    print(f"Checking for files exceeding {MAX_LINES} lines in {root_dir}...")
    violations = check_files(root_dir)

    if violations:
        print(f"\nFAILURE: Found {len(violations)} files exceeding limit:")
        for path, lines in sorted(violations, key=lambda x: x[1], reverse=True):
            print(f"  {path}: {lines} lines")
        print("\nPlease modularize these files.")
        sys.exit(1)
    else:
        print("\nSUCCESS: No God Files found! All files are modular.")
        sys.exit(0)

if __name__ == "__main__":
    main()
