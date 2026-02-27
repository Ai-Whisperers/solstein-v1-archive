#!/usr/bin/env python3
"""Database integrity verification script.

Checks for:
- Orphaned records (records with invalid foreign keys)
- NULL violations in required fields
- Data consistency issues
- Missing indexes
"""

import asyncio
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from solstein.database_config import get_test_database_url


async def verify_database():
    """Run database integrity checks."""
    db_url = get_test_database_url()
    # Convert to async URL
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # Handle SSL
    connect_args = {}
    if '?sslmode=' in async_url:
        url_parts = async_url.split('?sslmode=')
        async_url = url_parts[0]
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context
    
    engine = create_async_engine(async_url, echo=False, connect_args=connect_args)
    print("=" * 80)
    print("DATABASE INTEGRITY VERIFICATION")
    print("=" * 80)
    print()

    async with engine.connect() as conn:
        # 1. Count records in each table
        print("📊 Table Record Counts:")
        print("-" * 40)
        tables = [
            "companies",
            "scoring_records",
            "signal_records",
            "enrichment_audit_trail",
            "enrichment_cache",
            "enrichment_jobs",
            "market_snapshots",
            "audit_trails",
            "research_runs",
            "research_stages",
            "research_artifacts",
            "source_documents",
        ]

        for table in tables:
            try:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar_one()
                print(f"  {table:30s}: {count:6d} records")
            except Exception as e:
                print(f"  {table:30s}: ERROR - {e}")
        print()

        # 2. Check for orphaned signal records (no parent scoring_record)
        print("🔍 Checking Foreign Key Integrity:")
        print("-" * 40)
        try:
            result = await conn.execute(
                text("""
                SELECT COUNT(*) FROM signal_records sr
                LEFT JOIN scoring_records scr ON sr.scoring_record_id = scr.id
                WHERE scr.id IS NULL
            """)
            )
            orphaned = result.scalar_one()
            if orphaned == 0:
                print("  ✅ No orphaned signal records")
            else:
                print(f"  ⚠️  {orphaned} orphaned signal records found")
        except Exception as e:
            print(f"  ⚠️  Could not check signal records: {e}")
        print()

        # 3. Check for companies without required fields
        print("🔍 Checking Data Completeness:")
        print("-" * 40)
        try:
            result = await conn.execute(
                text("""
                SELECT COUNT(*) FROM companies 
                WHERE name IS NULL OR industry IS NULL
            """)
            )
            incomplete = result.scalar_one()
            if incomplete == 0:
                print("  ✅ All companies have required fields")
            else:
                print(f"  ⚠️  {incomplete} companies missing required fields")
        except Exception as e:
            print(f"  ⚠️  Could not check data completeness: {e}")
        print()

        # 4. Check index usage
        print("📈 Index Statistics:")
        print("-" * 40)
        try:
            result = await conn.execute(
                text("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                ORDER BY tablename, indexname
            """)
            )
            indexes = result.fetchall()
            print(f"  Total indexes: {len(indexes)}")

            # Count indexes per table
            tables_with_indexes = set()
            for idx in indexes:
                tables_with_indexes.add(idx[1])
            print(f"  Tables with indexes: {len(tables_with_indexes)}")
            print()

            # Show sample indexes
            print("  Sample indexes:")
            for idx in indexes[:5]:
                print(f"    - {idx[0]} on {idx[1]}")
        except Exception as e:
            print(f"  ⚠️  Could not check indexes: {e}")
        print()

    await engine.dispose()

    print("=" * 80)
    print("✅ Database integrity verification complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify_database())
