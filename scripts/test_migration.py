#!/usr/bin/env python3
"""Database migration testing and validation script.

EPIC-025 Story 5: Migration Strategy & Tooling

This script provides utilities for:
- Testing migrations against a staging database
- Validating migration rollbacks
- Checking migration timing
- Generating migration reports

Usage:
    # Test a specific migration
    python scripts/test_migration.py test 012

    # Test all pending migrations
    python scripts/test_migration.py test-all

    # Check migration timing
    python scripts/test_migration.py timing

    # Generate migration report
    python scripts/test_migration.py report
"""

import argparse
import asyncio
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from solstein.config import Settings


class MigrationTester:
    """Test database migrations for correctness and performance."""

    def __init__(self, database_url: str):
        """Initialize migration tester.

        Args:
            database_url: PostgreSQL connection URL.
        """
        self.database_url = database_url
        self.engine = None

    async def connect(self):
        """Create database engine."""
        # Convert to async URL
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.engine = create_async_engine(url, pool_size=5, max_overflow=10)

    async def disconnect(self):
        """Close database engine."""
        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def session(self):
        """Get database session."""
        async with AsyncSession(self.engine) as session:
            yield session

    async def get_current_revision(self) -> str | None:
        """Get current Alembic revision."""
        async with self.session() as session:
            try:
                result = await session.execute(text("SELECT version_num FROM alembic_version"))
                row = result.fetchone()
                return row[0] if row else None
            except Exception:
                return None

    async def get_pending_migrations(self) -> list[str]:
        """Get list of pending migrations."""
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        if "head" in result.stdout:
            return []

        # Get history to find pending
        result = subprocess.run(
            ["alembic", "history", "--verbose"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        migrations = []
        for line in result.stdout.split("\n"):
            if line.strip() and ">" in line:
                parts = line.split()
                if len(parts) >= 1:
                    migrations.append(parts[0])

        return migrations

    async def test_migration_upgrade(self, revision: str) -> dict[str, Any]:
        """Test a migration upgrade.

        Args:
            revision: Migration revision to test.

        Returns:
            Test results dictionary.
        """
        print(f"Testing migration {revision}...")

        start_time = time.time()

        try:
            # Run upgrade
            result = subprocess.run(
                ["alembic", "upgrade", revision],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=300,  # 5 minute timeout
            )

            elapsed = time.time() - start_time

            success = result.returncode == 0

            return {
                "revision": revision,
                "success": success,
                "duration_seconds": round(elapsed, 2),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None if success else result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "revision": revision,
                "success": False,
                "duration_seconds": 300,
                "error": "Migration timed out after 5 minutes",
            }
        except Exception as e:
            return {
                "revision": revision,
                "success": False,
                "duration_seconds": time.time() - start_time,
                "error": str(e),
            }

    async def test_migration_rollback(self, revision: str) -> dict[str, Any]:
        """Test a migration rollback.

        Args:
            revision: Migration revision to roll back.

        Returns:
            Test results dictionary.
        """
        print(f"Testing rollback of {revision}...")

        start_time = time.time()

        try:
            # Run downgrade
            result = subprocess.run(
                ["alembic", "downgrade", f"{revision}-1"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=300,
            )

            elapsed = time.time() - start_time

            success = result.returncode == 0

            return {
                "revision": revision,
                "success": success,
                "duration_seconds": round(elapsed, 2),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": None if success else result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "revision": revision,
                "success": False,
                "duration_seconds": 300,
                "error": "Rollback timed out after 5 minutes",
            }
        except Exception as e:
            return {
                "revision": revision,
                "success": False,
                "duration_seconds": time.time() - start_time,
                "error": str(e),
            }

    async def check_tables_exist(self, table_names: list[str]) -> dict[str, bool]:
        """Check if tables exist in database.

        Args:
            table_names: List of table names to check.

        Returns:
            Dictionary mapping table names to existence status.
        """
        async with self.session() as session:
            results = {}
            for table in table_names:
                result = await session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = :table
                        )
                    """),
                    {"table": table},
                )
                results[table] = result.scalar()
            return results

    async def check_indexes_exist(self, index_names: list[str]) -> dict[str, bool]:
        """Check if indexes exist in database.

        Args:
            index_names: List of index names to check.

        Returns:
            Dictionary mapping index names to existence status.
        """
        async with self.session() as session:
            results = {}
            for index in index_names:
                result = await session.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes
                            WHERE indexname = :index
                        )
                    """),
                    {"index": index},
                )
                results[index] = result.scalar()
            return results


def print_report(results: list[dict[str, Any]]):
    """Print formatted test report.

    Args:
        results: List of test results.
    """
    print("\n" + "=" * 60)
    print("MIGRATION TEST REPORT")
    print("=" * 60)

    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"\n{status} - {result['revision']}")
        print(f"  Duration: {result['duration_seconds']:.2f}s")
        if result.get("error"):
            print(f"  Error: {result['error'][:200]}")

    total = len(results)
    passed = sum(1 for r in results if r["success"])
    print(f"\n{'=' * 60}")
    print(f"Total: {passed}/{total} passed")
    print("=" * 60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Database Migration Testing")
    parser.add_argument(
        "command",
        choices=["test", "test-all", "timing", "report"],
        help="Command to execute",
    )
    parser.add_argument("--revision", "-r", help="Specific revision to test")
    parser.add_argument("--database", "-d", help="Database URL (or use DATABASE__URL env)")

    args = parser.parse_args()

    # Get database URL
    database_url = args.database or Settings.load().get_database_url()
    if not database_url:
        print("Error: Database URL not provided")
        sys.exit(1)

    tester = MigrationTester(database_url)
    await tester.connect()

    try:
        if args.command == "test":
            if not args.revision:
                print("Error: --revision required for test command")
                sys.exit(1)

            results = []

            # Test upgrade
            upgrade_result = await tester.test_migration_upgrade(args.revision)
            results.append(upgrade_result)

            if upgrade_result["success"]:
                # Test rollback
                rollback_result = await tester.test_migration_rollback(args.revision)
                results.append(rollback_result)

                # Re-apply migration
                await tester.test_migration_upgrade(args.revision)

            print_report(results)

        elif args.command == "test-all":
            pending = await tester.get_pending_migrations()
            if not pending:
                print("No pending migrations")
                return

            print(f"Testing {len(pending)} pending migrations...")
            results = []

            for migration in pending:
                result = await tester.test_migration_upgrade(migration)
                results.append(result)

            print_report(results)

        elif args.command == "timing":
            current = await tester.get_current_revision()
            print(f"Current revision: {current}")

            pending = await tester.get_pending_migrations()
            print(f"Pending migrations: {len(pending)}")

        elif args.command == "report":
            current = await tester.get_current_revision()
            pending = await tester.get_pending_migrations()

            print("\nMIGRATION STATUS REPORT")
            print("=" * 60)
            print(f"Current Revision: {current or 'None'}")
            print(f"Pending Migrations: {len(pending)}")
            if pending:
                print("\nPending:")
                for m in pending:
                    print(f"  - {m}")

    finally:
        await tester.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
