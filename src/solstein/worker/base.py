"""Base utilities for Celery worker tasks.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides database helpers and dead letter queue for failed jobs.
"""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select

from solstein.config import get_settings
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord


def get_db_manager():
    """Get initialized database manager."""
    settings = get_settings()
    db_manager = DatabaseManager(settings)
    db_manager.init_async()
    return db_manager


async def get_tracked_company_ids(db_manager) -> list[str]:
    """Get list of tracked company IDs from database."""
    async with db_manager.get_session() as session:
        result = await session.execute(select(CompanyRecord.company_id))
        return [row[0] for row in result.fetchall()]


async def store_facts(db_manager, facts: list[dict], source: str) -> int:
    """Store fetched facts in database.

    Returns:
        Number of facts stored
    """
    stored_count = 0
    async with db_manager.get_session() as session:
        for fact in facts:
            try:
                company_id = fact.get("company_id")
                if not company_id:
                    continue

                result = await session.execute(
                    select(CompanyRecord).where(CompanyRecord.company_id == company_id)
                )
                record = result.scalar_one_or_none()

                if record is None:
                    logger.debug(f"[store_facts] No company record found for {company_id}, skipping fact from {source}")
                    continue

                # Write source-specific fields into the record
                fact_type = fact.get("fact_type") or fact.get("type")
                fact_value = fact.get("value")

                if fact_type and fact_value is not None:
                    if not record.raw_data:
                        record.raw_data = {}
                    if source not in record.raw_data:
                        record.raw_data[source] = {}
                    record.raw_data[source][fact_type] = fact_value

                record.last_updated = datetime.now(timezone.utc)
                stored_count += 1

            except Exception as e:
                logger.warning(f"Failed to store fact from {source}: {e}")
                continue

        await session.commit()

    return stored_count


# ============================================================================
# PHASE 13.4: DEAD LETTER QUEUE FOR PERMANENTLY FAILED JOBS
# ============================================================================


class DeadLetterQueue:
    """Track permanently failed jobs after max retries exceeded."""

    def __init__(self):
        self.failed_jobs = []

    def record_failure(self, task_name: str, task_id: str, error: str, attempt: int):
        """Record a permanently failed job."""
        logger.info(f"[RETRY-FAILED] {task_name} (task_id={task_id}): {error} after {attempt} attempts")
        self.failed_jobs.append(
            {
                "task_name": task_name,
                "task_id": task_id,
                "error": error,
                "final_attempt": attempt,
                "timestamp": datetime.now(timezone.utc),
            }
        )


# Global Dead Letter Queue instance
dead_letter_queue = DeadLetterQueue()
