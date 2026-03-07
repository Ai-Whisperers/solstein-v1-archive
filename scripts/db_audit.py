#!/usr/bin/env python3
"""Database Query Performance Auditor for EPIC-023 Story 2.

Usage:
    python scripts/db_audit.py --check-indexes
    python scripts/db_audit.py --analyze-queries
    python scripts/db_audit.py --suggest-optimizations
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger


class DatabaseAuditor:
    """Audits database performance and suggests optimizations."""

    # Common indexes that should exist
    RECOMMENDED_INDEXES = {
        "companies": [
            ("ticker",),  # Lookups by ticker
            ("name",),  # Search by name
            ("industry", "region"),  # Market analysis queries
            ("created_at",),  # Recent companies
        ],
        "company_records": [
            ("ticker",),  # Lookups by ticker
            ("name",),  # Search by name
            ("industry", "region"),  # Market analysis
            ("scoring_record_id",),  # Join with scoring
            ("enriched_at",),  # Enrichment queries
        ],
        "scoring_records": [
            ("company_id", "created_at"),  # Latest scoring per company
            ("classification",),  # Filter by classification
            ("growth_score",),  # Score range queries
            ("composite_score",),  # Sort by score
        ],
        "enrichment_cache": [
            ("company_id", "source"),  # Cache lookups
            ("expires_at",),  # TTL queries
            ("company_id", "expires_at"),  # Combined
        ],
        "research_runs": [
            ("status", "created_at"),  # Active runs
            ("market_region", "industry"),  # Market analysis
        ],
    }

    def __init__(self):
        self.findings: list[dict] = []

    async def check_existing_indexes(self) -> list[dict]:
        """Check existing indexes on tables."""
        from solstein.infrastructure.database import get_async_session
        from sqlalchemy import text

        indexes = []

        async with get_async_session() as session:
            # Query for existing indexes
            query = text("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)

            result = await session.execute(query)
            for row in result.mappings():
                indexes.append(
                    {
                        "schema": row["schemaname"],
                        "table": row["tablename"],
                        "index": row["indexname"],
                        "definition": row["indexdef"],
                    }
                )

        return indexes

    def analyze_missing_indexes(self, existing_indexes: list[dict]) -> list[dict]:
        """Identify missing recommended indexes."""
        missing = []

        existing_by_table: dict[str, set] = {}
        for idx in existing_indexes:
            table = idx["table"]
            if table not in existing_by_table:
                existing_by_table[table] = set()
            # Extract columns from index definition (simplified)
            existing_by_table[table].add(idx["index"])

        for table, recommended in self.RECOMMENDED_INDEXES.items():
            existing = existing_by_table.get(table, set())

            for columns in recommended:
                index_name = f"idx_{table}_{'_'.join(columns)}"

                # Check if similar index exists (simplified check)
                if not any(index_name in idx for idx in existing):
                    missing.append(
                        {
                            "table": table,
                            "columns": columns,
                            "suggested_name": index_name,
                            "sql": self._generate_create_index(table, columns, index_name),
                        }
                    )

        return missing

    def _generate_create_index(self, table: str, columns: tuple[str, ...], name: str) -> str:
        """Generate CREATE INDEX SQL."""
        columns_str = ", ".join(columns)
        return f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({columns_str});"

    async def analyze_slow_queries(self) -> list[dict]:
        """Analyze slow queries from pg_stat_statements (if available)."""
        from solstein.infrastructure.database import get_async_session
        from sqlalchemy import text

        slow_queries = []

        try:
            async with get_async_session() as session:
                query = text("""
                    SELECT
                        query,
                        mean_exec_time,
                        calls,
                        total_exec_time
                    FROM pg_stat_statements
                    WHERE mean_exec_time > 50  -- >50ms average
                    ORDER BY mean_exec_time DESC
                    LIMIT 20
                """)

                result = await session.execute(query)
                for row in result.mappings():
                    slow_queries.append(
                        {
                            "query": row["query"][:200] + "..." if len(row["query"]) > 200 else row["query"],
                            "mean_time_ms": round(row["mean_exec_time"], 2),
                            "calls": row["calls"],
                            "total_time_ms": round(row["total_exec_time"], 2),
                        }
                    )
        except Exception as e:
            logger.warning(f"Could not analyze slow queries (pg_stat_statements may not be enabled): {e}")

        return slow_queries

    def suggest_optimizations(self) -> list[dict]:
        """Generate optimization suggestions."""
        suggestions = []

        # Connection pool settings
        suggestions.append(
            {
                "category": "Connection Pool",
                "issue": "Default connection pool may be too small",
                "recommendation": "Increase pool_size to 20, max_overflow to 30",
                "sql": "-- Update in database.py or settings\n-- pool_size=20, max_overflow=30",
            }
        )

        # Query batching
        suggestions.append(
            {
                "category": "Query Pattern",
                "issue": "N+1 queries may exist in enrichment code",
                "recommendation": "Use joinedload() for relationships",
                "code_example": """
# Before (N+1)
for company in companies:
    metrics = await db.fetch(company.metrics)  # N queries

# After (single query)
companies = await db.fetch(
    select(Company).options(joinedload(Company.metrics))
)
""",
            }
        )

        # Index usage
        suggestions.append(
            {
                "category": "Indexing",
                "issue": "Foreign key columns may be missing indexes",
                "recommendation": "Add indexes to all foreign key columns",
                "sql": "-- Run: CREATE INDEX ON table(column_id) for all FKs",
            }
        )

        return suggestions

    async def run_audit(self) -> dict:
        """Run complete database audit."""
        logger.info("Starting database performance audit...")

        # Check existing indexes
        existing = await self.check_existing_indexes()
        logger.info(f"Found {len(existing)} existing indexes")

        # Find missing indexes
        missing = self.analyze_missing_indexes(existing)
        logger.info(f"Found {len(missing)} missing recommended indexes")

        # Analyze slow queries
        slow = await self.analyze_slow_queries()
        logger.info(f"Found {len(slow)} slow queries")

        # Get optimization suggestions
        suggestions = self.suggest_optimizations()

        return {
            "existing_indexes": existing,
            "missing_indexes": missing,
            "slow_queries": slow,
            "suggestions": suggestions,
        }


def print_report(results: dict) -> None:
    """Print audit report."""
    print("\n" + "=" * 70)
    print("DATABASE PERFORMANCE AUDIT REPORT")
    print("=" * 70)

    # Missing indexes
    if results["missing_indexes"]:
        print("\n📋 MISSING RECOMMENDED INDEXES:")
        print("-" * 40)
        for idx in results["missing_indexes"]:
            print(f"\nTable: {idx['table']}")
            print(f"Columns: {', '.join(idx['columns'])}")
            print(f"SQL: {idx['sql']}")

    # Slow queries
    if results["slow_queries"]:
        print("\n🐌 SLOW QUERIES (>50ms average):")
        print("-" * 40)
        for q in results["slow_queries"]:
            print(f"\nMean: {q['mean_time_ms']}ms | Calls: {q['calls']}")
            print(f"Query: {q['query'][:100]}...")

    # General suggestions
    print("\n💡 OPTIMIZATION SUGGESTIONS:")
    print("-" * 40)
    for s in results["suggestions"]:
        print(f"\n[{s['category']}] {s['issue']}")
        print(f"Recommendation: {s['recommendation']}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Existing indexes: {len(results['existing_indexes'])}")
    print(f"Missing recommended indexes: {len(results['missing_indexes'])}")
    print(f"Slow queries detected: {len(results['slow_queries'])}")


async def main():
    parser = argparse.ArgumentParser(description="Database Performance Auditor")
    parser.add_argument("--check-indexes", action="store_true", help="Check existing indexes")
    parser.add_argument("--analyze-queries", action="store_true", help="Analyze slow queries")
    parser.add_argument("--suggest-optimizations", action="store_true", help="Suggest optimizations")
    parser.add_argument("--full-audit", action="store_true", help="Run complete audit")

    args = parser.parse_args()

    auditor = DatabaseAuditor()

    if args.full_audit or not any([args.check_indexes, args.analyze_queries, args.suggest_optimizations]):
        results = await auditor.run_audit()
        print_report(results)
    else:
        if args.check_indexes:
            existing = await auditor.check_existing_indexes()
            print(f"Found {len(existing)} existing indexes")

        if args.analyze_queries:
            slow = await auditor.analyze_slow_queries()
            print(f"Found {len(slow)} slow queries")

        if args.suggest_optimizations:
            suggestions = auditor.suggest_optimizations()
            for s in suggestions:
                print(f"[{s['category']}] {s['recommendation']}")


if __name__ == "__main__":
    asyncio.run(main())
