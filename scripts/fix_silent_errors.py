#!/usr/bin/env python3
"""Batch fix common silent exception patterns.

This script fixes the most common silent exception patterns:
1. except Exception: pass -> except Exception as e: logger.debug(...)
2. except Exception: return default -> except Exception as e: logger.debug(...); return default

Usage:
    python scripts/fix_silent_errors.py [--dry-run]

Options:
    --dry-run    Show changes without applying them
"""

import argparse
import re
from pathlib import Path

# Common patterns to fix
PATTERNS = [
    # Pattern 1: except Exception: pass (with various whitespace)
    (
        r"except\s+(\w+)\s*:\s*\n\s*pass",
        r'except \1 as e:\n            logger.debug(f"Exception suppressed: {e}")',
        "except Exception: pass",
    ),
    # Pattern 2: except Exception: return None
    (
        r"except\s+(\w+)\s*:\s*\n\s*return\s+(\w+)",
        r'except \1 as e:\n            logger.debug(f"Exception suppressed: {e}")\n            return \2',
        "except Exception: return value",
    ),
]

# Files to skip (test files, generated files, etc.)
SKIP_FILES = {
    "test_",
    "__pycache__",
    ".pyc",
    "migrations",
}

# Critical paths to prioritize
CRITICAL_PATHS = [
    "src/solstein/api/",
    "src/solstein/data/",
    "src/solstein/llm/",
    "src/solstein/research/",
    "src/solstein/infrastructure/",
]


def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    if filepath.suffix != ".py":
        return False

    for skip in SKIP_FILES:
        if skip in str(filepath):
            return False

    return True


def fix_file(filepath: Path, dry_run: bool = False) -> int:
    """Fix silent errors in a file. Returns number of fixes."""
    content = filepath.read_text()
    original = content
    fixes = 0

    # Check if file has loguru import
    has_loguru = "from loguru import logger" in content

    for pattern, replacement, desc in PATTERNS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        if matches:
            if not dry_run:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            fixes += len(matches)

    # Add loguru import if needed and we made changes
    if fixes > 0 and not has_loguru and not dry_run:
        # Add import after other imports
        lines = content.split("\n")
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_idx = i + 1
        lines.insert(import_idx, "from loguru import logger")
        content = "\n".join(lines)

    if not dry_run and content != original:
        filepath.write_text(content)

    return fixes


def main():
    parser = argparse.ArgumentParser(description="Fix silent exception handlers")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--path", default="src/solstein", help="Path to process")
    args = parser.parse_args()

    base_path = Path(args.path)
    total_fixes = 0
    files_fixed = 0

    # Process critical paths first
    for critical_path in CRITICAL_PATHS:
        path = base_path / critical_path.replace("src/solstein/", "")
        if not path.exists():
            continue

        for py_file in path.rglob("*.py"):
            if not should_process_file(py_file):
                continue

            fixes = fix_file(py_file, args.dry_run)
            if fixes > 0:
                print(f"{'Would fix' if args.dry_run else 'Fixed'} {fixes} handlers in {py_file}")
                total_fixes += fixes
                files_fixed += 1

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {total_fixes} silent handlers in {files_fixed} files")


if __name__ == "__main__":
    main()
