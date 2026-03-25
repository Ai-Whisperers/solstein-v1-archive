"""Base utilities for Celery worker tasks.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides database helpers and dead letter queue for failed jobs.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy import select

from solstein.config import get_settings
from solstein.domain.facts import Fact, GatheringBatch
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord


class FactIngestionPayload(BaseModel):
    """Validated boundary schema for fact ingestion into worker persistence."""

    company_id: str = Field(min_length=1)
    fact_type: str = Field(min_length=1)
    value: Any = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def normalize_fact_type_alias(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if not data.get("fact_type") and data.get("type"):
            normalized = dict(data)
            normalized["fact_type"] = data["type"]
            return normalized
        return data


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
    """Store fetched facts in database using the Fact repository pattern.

    Creates a GatheringBatch, then persists each fact as a proper Fact ORM
    record in the ``facts`` table.  Also updates the legacy
    ``CompanyRecord.raw_data`` blob so downstream code that reads from it
    continues to work.

    Args:
        db_manager: Initialised DatabaseManager.
        facts: List of fact dicts.  Each dict must contain at least
            ``company_id``; ``fact_type``/``type`` and ``value`` are used
            when present.
        source: Name of the data source (e.g. ``"sec_edgar"``).

    Returns:
        Number of facts successfully stored.
    """
    if not facts:
        return 0

    stored_count = 0
    batch_id = str(uuid.uuid4())

    async with db_manager.get_session() as session:
        # Determine the company_id for the batch (use first fact's company)
        first_company_id = next(
            (f.get("company_id") for f in facts if f.get("company_id")),
            None,
        )
        if first_company_id is None:
            logger.warning(f"[store_facts] No company_id found in any fact from {source}, nothing to store")
            return 0

        # Create a GatheringBatch to group these facts
        batch = GatheringBatch(
            batch_id=batch_id,
            company_id=first_company_id,
            status="in_progress",
        )
        session.add(batch)
        await session.flush()  # ensure batch_id is available for FK

        for fact_dict in facts:
            try:
                try:
                    payload = FactIngestionPayload.model_validate(fact_dict)
                except ValidationError as e:
                    logger.warning(f"[store_facts] Invalid fact payload from {source}: {e}")
                    continue

                company_id = payload.company_id
                fact_type = payload.fact_type
                fact_value = payload.value

                # Verify the company exists before writing
                result = await session.execute(
                    select(CompanyRecord).where(CompanyRecord.company_id == company_id)
                )
                record = result.scalar_one_or_none()

                if record is None:
                    logger.debug(f"[store_facts] No company record found for {company_id}, skipping fact from {source}")
                    continue

                # --- Persist as a proper Fact record ---
                if fact_type:
                    numeric_value = None
                    value_str = None
                    if isinstance(fact_value, (int, float)):
                        numeric_value = float(fact_value)
                    elif fact_value is not None:
                        value_str = str(fact_value)

                    fact_record = Fact(
                        company_id=company_id,
                        batch_id=batch_id,
                        fact_type=fact_type,
                        value=numeric_value,
                        value_str=value_str,
                        confidence=payload.confidence,
                        extracted_at=datetime.now(timezone.utc),
                    )
                    session.add(fact_record)

                # --- Also update legacy raw_data on CompanyRecord ---
                if fact_type and fact_value is not None:
                    if not record.raw_data:
                        record.raw_data = {}
                    if source not in record.raw_data:
                        record.raw_data[source] = {}
                    record.raw_data[source][fact_type] = fact_value

                record.last_updated = datetime.now(timezone.utc)
                stored_count += 1

            except Exception as e:
                logger.warning(f"[store_facts] Failed to store fact from {source} for company {fact_dict.get('company_id', '?')}: {e}")
                continue

        # Mark batch as completed (or failed if nothing stored)
        batch.status = "completed" if stored_count > 0 else "failed"
        await session.commit()

    logger.info(f"[store_facts] Stored {stored_count}/{len(facts)} facts from {source} in batch {batch_id}")
    return stored_count


# ============================================================================
# PHASE 13.4: DEAD LETTER QUEUE FOR PERMANENTLY FAILED JOBS
# ============================================================================


class DeadLetterQueue:
    """Track permanently failed jobs after max retries exceeded.

    WARNING: This implementation stores failed jobs in-memory only.
    All recorded failures are lost on process restart.  In production
    this should be backed by persistent storage (e.g. a database table
    or a durable message queue) so that permanently-failed jobs can be
    reviewed and retried after a worker restart.
    """

    def __init__(self):
        self.failed_jobs = []

    def record_failure(self, task_name: str, task_id: str, error: str, attempt: int):
        """Record a permanently failed job."""
        logger.error(f"[RETRY-FAILED] {task_name} (task_id={task_id}) permanently failed after {attempt} attempts: {error}")
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
