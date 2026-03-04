"""Database cleanup utilities for test isolation.

Provides functions to clean test data between test suites while respecting
foreign key constraints and maintaining database integrity.
"""

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.facts import Fact, FactSource, GatheringBatch


async def cleanup_test_database(session: AsyncSession) -> None:
    """Delete all test data while respecting foreign key constraints.

    Deletes data in the correct order to avoid FK constraint violations:
    1. FactSource (depends on Fact)
    2. Fact (depends on GatheringBatch)
    3. GatheringBatch (depends on Company)

    Args:
        session: AsyncSession for database operations

    Raises:
        Exception: If cleanup fails, session is rolled back
    """
    try:
        # Delete in reverse dependency order
        await session.execute(delete(FactSource))
        await session.execute(delete(Fact))
        await session.execute(delete(GatheringBatch))
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def cleanup_specific_table(session: AsyncSession, table_name: str) -> None:
    """Delete all rows from a specific table.

    Args:
        session: AsyncSession for database operations
        table_name: Name of the table to clean (e.g., "facts", "gathering_batches")

    Raises:
        Exception: If cleanup fails, session is rolled back
    """
    try:
        await session.execute(text(f"DELETE FROM {table_name}"))
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def cleanup_company_data(session: AsyncSession, company_id: str) -> None:
    """Delete all data for a specific company.

    Deletes all facts, batches, and sources associated with a company.

    Args:
        session: AsyncSession for database operations
        company_id: ID of the company to clean

    Raises:
        Exception: If cleanup fails, session is rolled back
    """
    try:
        # Delete fact sources for this company's facts
        await session.execute(
            delete(FactSource).where(
                FactSource.fact_id.in_(session.query(Fact.fact_id).filter(Fact.company_id == company_id))
            )
        )
        # Delete facts for this company
        await session.execute(delete(Fact).where(Fact.company_id == company_id))
        # Delete batches for this company
        await session.execute(delete(GatheringBatch).where(GatheringBatch.company_id == company_id))
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def cleanup_batch_data(session: AsyncSession, batch_id: str) -> None:
    """Delete all data for a specific gathering batch.

    Deletes all facts and sources associated with a batch.

    Args:
        session: AsyncSession for database operations
        batch_id: ID of the batch to clean

    Raises:
        Exception: If cleanup fails, session is rolled back
    """
    try:
        # Delete fact sources for this batch's facts
        await session.execute(
            delete(FactSource).where(
                FactSource.fact_id.in_(session.query(Fact.fact_id).filter(Fact.batch_id == batch_id))
            )
        )
        # Delete facts for this batch
        await session.execute(delete(Fact).where(Fact.batch_id == batch_id))
        # Delete the batch itself
        await session.execute(delete(GatheringBatch).where(GatheringBatch.batch_id == batch_id))
        await session.commit()
    except Exception:
        await session.rollback()
        raise


__all__ = [
    "cleanup_test_database",
    "cleanup_specific_table",
    "cleanup_company_data",
    "cleanup_batch_data",
]
