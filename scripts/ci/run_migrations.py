"""Run Alembic migrations with structured logging, timeout, and idempotency.

This is the canonical migration runner for all environments (local, CI, staging,
production). It wraps `alembic upgrade head` with:

- Structured log output (revision, direction, duration)
- Configurable timeout (default: 5 minutes)
- Idempotency: running on an already-current database is a no-op
- Non-zero exit on failure (blocks deploy)

Usage:
    python scripts/ci/run_migrations.py [--timeout SECONDS] [--dry-run]

Environment:
    DATABASE__URL or SUPABASE__DB_URL must be set (read by alembic/env.py via Settings)
"""

from __future__ import annotations

import argparse
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("migrate")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class MigrationTimeoutError(Exception):
    """Raised when migration exceeds the configured timeout."""


def _timeout_handler(signum: int, frame: object) -> None:
    raise MigrationTimeoutError("Migration exceeded timeout")


def get_current_revision() -> str | None:
    """Get the current Alembic revision of the database."""
    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        # Parse output: lines like "abc123def456 (head)" or "(head)"
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("INFO"):
                # Extract revision hash (first word before space or parenthesis)
                parts = line.split()
                if parts:
                    return parts[0]
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.warning("Could not determine current revision: %s", exc)
    return None


def get_head_revision() -> str | None:
    """Get the latest Alembic head revision from migration files."""
    try:
        result = subprocess.run(
            ["alembic", "heads"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("INFO"):
                parts = line.split()
                if parts:
                    return parts[0]
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.warning("Could not determine head revision: %s", exc)
    return None


def run_migration(timeout_seconds: int = 300, dry_run: bool = False) -> int:
    """Run alembic upgrade head with structured logging.

    Args:
        timeout_seconds: Maximum time in seconds before migration is killed.
        dry_run: If True, show what would be done without applying.

    Returns:
        0 on success, 1 on failure.
    """
    logger.info("Migration started")
    logger.info("  Project root: %s", PROJECT_ROOT)
    logger.info("  Timeout: %ds", timeout_seconds)

    # Check current state
    current = get_current_revision()
    head = get_head_revision()
    logger.info("  Current revision: %s", current or "(none)")
    logger.info("  Head revision: %s", head or "(unknown)")

    if current and head and current == head:
        logger.info("Database is already at head revision — no-op")
        return 0

    if dry_run:
        logger.info("DRY RUN — would run: alembic upgrade head")
        return 0

    # Set timeout via SIGALRM (Unix only)
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout_seconds)

    start_time = time.monotonic()
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        duration = time.monotonic() - start_time

        if result.returncode != 0:
            logger.error("Migration FAILED (exit code %d)", result.returncode)
            logger.error("STDOUT: %s", result.stdout)
            logger.error("STDERR: %s", result.stderr)
            return 1

        # Log applied revisions from alembic output
        for line in result.stderr.split("\n"):
            if "Running upgrade" in line or "Running downgrade" in line:
                logger.info("  %s", line.strip())

        new_revision = get_current_revision()
        logger.info("Migration completed successfully")
        logger.info("  New revision: %s", new_revision or "(unknown)")
        logger.info("  Duration: %.2fs", duration)
        return 0

    except MigrationTimeoutError:
        logger.error("Migration TIMED OUT after %ds — killed", timeout_seconds)
        return 1
    except subprocess.TimeoutExpired:
        logger.error("Migration TIMED OUT after %ds — process killed", timeout_seconds)
        return 1
    except FileNotFoundError:
        logger.error("alembic command not found — ensure alembic is installed")
        return 1
    except Exception as exc:
        logger.error("Migration failed with unexpected error: %s", exc)
        return 1
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)  # Cancel alarm


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run Alembic migrations")
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without applying",
    )
    args = parser.parse_args()
    return run_migration(timeout_seconds=args.timeout, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
