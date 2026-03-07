#!/usr/bin/env python3
"""Check folder structure and identify directories with too many items.

Part of CI/CD code quality guardrails to ensure proper code organization.
"""

import sys
from pathlib import Path
import argparse
from dataclasses import dataclass

# Configuration
DEFAULT_FILE_THRESHOLD = 15
DEFAULT_FOLDER_THRESHOLD = 10
DEFAULT_TOTAL_THRESHOLD = 25
EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "node_modules",
    ".opencode",
    "site",
    "migrations",
}


@dataclass
class DirectoryStats:
    """Statistics for a single directory."""

    path: Path
    file_count: int
    folder_count: int

    @property
    def total_items(self) -> int:
        return self.file_count + self.folder_count


def should_exclude_dir(dirname: str) -> bool:
    """Check if directory should be excluded from analysis."""
    if dirname in EXCLUDE_DIRS:
        return True
    if dirname.startswith("."):
        return True
    return False


def analyze_directory(dir_path: Path) -> DirectoryStats:
    """Analyze a single directory."""
    files = 0
    subdirs = 0

    try:
        for item in dir_path.iterdir():
            if item.is_file() and not item.name.startswith("."):
                files += 1
            elif item.is_dir() and not should_exclude_dir(item.name):
                subdirs += 1
    except (PermissionError, OSError):
        pass

    return DirectoryStats(path=dir_path, file_count=files, folder_count=subdirs)


def scan_directory(root_dir: Path, max_depth: int = 5, current_depth: int = 0) -> list[DirectoryStats]:
    """Recursively scan directory and collect statistics."""
    if current_depth > max_depth:
        return []

    results = []
    stats = analyze_directory(root_dir)
    results.append(stats)

    for subdir in [d for d in root_dir.iterdir() if d.is_dir() and not should_exclude_dir(d.name)]:
        results.extend(scan_directory(subdir, max_depth, current_depth + 1))

    return results


def check_folder_structure(
    root_dir: Path = Path("src"),
    file_threshold: int = DEFAULT_FILE_THRESHOLD,
    folder_threshold: int = DEFAULT_FOLDER_THRESHOLD,
    total_threshold: int = DEFAULT_TOTAL_THRESHOLD,
) -> tuple[list[DirectoryStats], list[DirectoryStats], list[DirectoryStats]]:
    """Check folder structure and return violations by severity."""
    stats_list = scan_directory(root_dir)

    critical = []
    warnings = []
    notices = []

    for stats in stats_list:
        if stats.file_count > 30 or stats.total_items > 50:
            critical.append(stats)
        elif (
            stats.file_count > file_threshold
            or stats.folder_count > folder_threshold
            or stats.total_items > total_threshold
        ):
            warnings.append(stats)
        elif stats.total_items > 15:
            notices.append(stats)

    return critical, warnings, notices


def main():
    parser = argparse.ArgumentParser(description="Check folder structure organization")
    parser.add_argument("--path", type=str, default="src", help="Root directory to analyze (default: src)")
    parser.add_argument(
        "--file-threshold",
        type=int,
        default=DEFAULT_FILE_THRESHOLD,
        help=f"File count threshold (default: {DEFAULT_FILE_THRESHOLD})",
    )
    parser.add_argument(
        "--folder-threshold",
        type=int,
        default=DEFAULT_FOLDER_THRESHOLD,
        help=f"Folder count threshold (default: {DEFAULT_FOLDER_THRESHOLD})",
    )
    parser.add_argument(
        "--total-threshold",
        type=int,
        default=DEFAULT_TOTAL_THRESHOLD,
        help=f"Total items threshold (default: {DEFAULT_TOTAL_THRESHOLD})",
    )
    parser.add_argument(
        "--fail-on-violation",
        action="store_true",
        help="Exit with error code if violations found",
    )

    args = parser.parse_args()

    root_dir = Path(args.path)
    if not root_dir.exists():
        print(f"Error: Directory '{args.path}' not found.")
        sys.exit(1)

    critical, warnings, notices = check_folder_structure(
        root_dir=root_dir,
        file_threshold=args.file_threshold,
        folder_threshold=args.folder_threshold,
        total_threshold=args.total_threshold,
    )

    has_error = False

    if critical:
        print(f"\n🔴 CRITICAL: {len(critical)} directories severely overcrowded:")
        for stats in sorted(critical, key=lambda x: -x.total_items):
            print(f"  {stats.file_count:3d} files, {stats.folder_count:3d} folders | {stats.path}")
        has_error = True

    if warnings:
        print(f"\n🟡 WARNING: {len(warnings)} directories need reorganization:")
        for stats in sorted(warnings, key=lambda x: -x.total_items):
            print(f"  {stats.file_count:3d} files, {stats.folder_count:3d} folders | {stats.path}")
        has_error = True

    if notices:
        print(f"\n🟢 NOTICE: {len(notices)} directories approaching limits:")
        for stats in sorted(notices, key=lambda x: -x.total_items)[:5]:
            print(f"  {stats.file_count:3d} files, {stats.folder_count:3d} folders | {stats.path}")

    if not critical and not warnings and not notices:
        print(f"✅ All directories in '{args.path}' are well organized")

    if has_error:
        print("\n⚠️  Consider:")
        print("   - Grouping related files into subdirectories")
        print("   - Separating tests from source code")
        print("   - Using feature-based organization")

    if has_error and args.fail_on_violation:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
