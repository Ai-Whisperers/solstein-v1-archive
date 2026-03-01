#!/usr/bin/env python3
"""
Export cleanup utility — removes old Excel/JSON files from the exports directory.

Usage:
    python scripts/cleanup_exports.py --dry-run
    python scripts/cleanup_exports.py --keep-last 10
    python scripts/cleanup_exports.py --older-than-days 30
    python scripts/cleanup_exports.py --directory data/output/exports --keep-last 5
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)  # type: ignore[assignment]


def get_export_files(directory: Path) -> list[Path]:
    """Get all export files sorted by modification time (newest first).

    Args:
        directory: Directory to scan for export files.

    Returns:
        List of file paths sorted newest-first.
    """
    patterns = ["*.xlsx", "*.json", "*.csv"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    # Sort newest first
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files


def format_size(size_bytes: float) -> str:
    """Format byte size to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes:.0f} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 / 1024:.1f} MB"


def cleanup_exports(
    directory: Path,
    keep_last: int = 10,
    dry_run: bool = False,
    older_than_days: int | None = None,
) -> tuple[int, float]:
    """Clean up old export files.

    Args:
        directory: Target directory to clean.
        keep_last: Number of most recent files to keep (used if older_than_days is None).
        dry_run: If True, show what would be deleted without deleting.
        older_than_days: Delete files older than this many days (overrides keep_last).

    Returns:
        Tuple of (files_deleted_count, bytes_freed).
    """
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return 0, 0.0

    files = get_export_files(directory)
    total = len(files)
    total_size = sum(f.stat().st_size for f in files)
    logger.info(f"Found {total} export files in {directory} ({format_size(total_size)})")

    to_delete: list[Path] = []

    if older_than_days is not None:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        to_delete = [f for f in files if datetime.fromtimestamp(f.stat().st_mtime) < cutoff]
        logger.info(f"Files older than {older_than_days} days: {len(to_delete)}")
    else:
        to_keep = files[:keep_last]
        to_delete = files[keep_last:]
        logger.info(f"Keeping {len(to_keep)} most recent files, deleting {len(to_delete)}")

    if not to_delete:
        logger.success("Nothing to clean up — all files within retention policy!")
        return 0, 0.0

    bytes_to_free = sum(f.stat().st_size for f in to_delete)

    for f in to_delete:
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        size_str = format_size(f.stat().st_size)
        if dry_run:
            logger.info(f"[DRY RUN] Would delete: {f.name} ({size_str}, {age_days}d old)")
        else:
            f.unlink()
            logger.info(f"Deleted: {f.name} ({size_str}, {age_days}d old)")

    verb = "Would free" if dry_run else "Freed"
    logger.success(f"{verb} {format_size(bytes_to_free)} from {len(to_delete)} files")
    return len(to_delete), bytes_to_free


def main() -> None:
    """Entry point for the cleanup utility."""
    parser = argparse.ArgumentParser(
        description="Clean up old export files from the exports directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--keep-last",
        type=int,
        default=10,
        metavar="N",
        help="Keep this many most-recent files per type (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--older-than-days",
        type=int,
        default=None,
        metavar="N",
        help="Delete files older than N days (overrides --keep-last)",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="data/output/exports",
        help="Target directory (default: data/output/exports)",
    )

    args = parser.parse_args()
    directory = Path(args.directory)

    deleted, freed = cleanup_exports(
        directory=directory,
        keep_last=args.keep_last,
        dry_run=args.dry_run,
        older_than_days=args.older_than_days,
    )

    if not args.dry_run and deleted > 0:
        logger.info(f"Cleanup complete: removed {deleted} files, freed {format_size(freed)}")


if __name__ == "__main__":
    main()
