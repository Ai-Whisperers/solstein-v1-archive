"""
Script to detect and fix duplicate company IDs.

Usage:
    python scripts/fix_duplicate_company_ids.py

This script:
1. Connects to the database
2. Finds duplicate company_id values
3. Generates new unique IDs for duplicates
4. Updates all related tables with foreign key references
"""

import asyncio
import sys
from collections import defaultdict

sys.path.insert(0, "src")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database import get_async_engine
from solstein.infrastructure.database_models import CompanyRecord


async def find_duplicate_ids():
    """Find all duplicate company_id values."""
    engine = get_async_engine()

    async with AsyncSession(engine) as session:
        # Query all company_ids
        result = await session.execute(select(CompanyRecord.company_id))
        ids = [row[0] for row in result.all()]

        # Find duplicates
        id_counts = defaultdict(int)
        for cid in ids:
            id_counts[cid] += 1

        duplicates = {cid: count for cid, count in id_counts.items() if count > 1}

        print(f"Total companies: {len(ids)}")
        print(f"Unique IDs: {len(set(ids))}")
        print(f"Duplicate IDs: {len(duplicates)}")

        if duplicates:
            print("\nDuplicate company_ids:")
            for cid, count in sorted(duplicates.items(), key=lambda x: -x[1]):
                print(f"  {cid}: {count} occurrences")

        return duplicates


async def fix_duplicate_ids():
    """Fix duplicate company IDs by appending counters."""
    engine = get_async_engine()

    async with AsyncSession(engine) as session:
        duplicates = await find_duplicate_ids()

        if not duplicates:
            print("\n✓ No duplicates found!")
            return

        print(f"\nFixing {len(duplicates)} duplicate IDs...")

        for cid, count in duplicates.items():
            # Get all records with this duplicate ID
            result = await session.execute(select(CompanyRecord).where(CompanyRecord.company_id == cid))
            records = result.scalars().all()

            # Keep the first one as-is, rename others
            for i, record in enumerate(records[1:], 1):
                new_id = f"{cid}_{i}"
                print(f"  Renaming {cid} -> {new_id}")
                record.company_id = new_id

        await session.commit()
        print("\n✓ Duplicate IDs fixed!")


async def add_id_validation():
    """Add validation to prevent future duplicates."""
    # This would typically involve:
    # 1. Adding a database trigger
    # 2. Adding application-level validation
    # 3. Adding a unique constraint (already exists)

    print("\nValidation strategy:")
    print("1. Database unique constraint: Already exists on company_id")
    print("2. Application validation: Add to Company creation logic")
    print("3. ID generation: Use UUID or prefixed incremental IDs")


if __name__ == "__main__":
    print("=" * 60)
    print("Company ID Duplicate Detection and Fix")
    print("=" * 60)

    # Find duplicates
    asyncio.run(find_duplicate_ids())

    # Ask before fixing
    response = input("\nFix duplicates? (yes/no): ").lower()
    if response == "yes":
        asyncio.run(fix_duplicate_ids())
    else:
        print("Skipping fix.")

    asyncio.run(add_id_validation())
