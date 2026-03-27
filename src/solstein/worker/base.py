"""Base utilities for Celery worker tasks.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides database helpers and dead letter queue for failed jobs.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select

from solstein.config import get_settings
from solstein.domain.facts import Fact, GatheringBatch
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord
from solstein.infrastructure.fact_payloads import ConnectorFactPayload
from solstein.monitoring.errors import global_error_tracker


class FactIngestionPayload(ConnectorFactPayload):
    """Validated boundary schema for fact ingestion into worker persistence."""


def get_db_manager():
    """Get initialized database manager."""
    settings = get_settings()
    db_manager = DatabaseManager(settings)
    db_manager.init_async()
    return db_manager


async def get_tracked_company_ids(db_manager, *, tenant_id: str | None = None) -> list[str]:
    """Get list of tracked company IDs from database.

    STORY-066: When tenant_id is provided, only returns companies
    belonging to that tenant.

    Args:
        db_manager: Database manager instance.
        tenant_id: Optional tenant ID to scope the query.

    Returns:
        List of company IDs.
    """
    async with db_manager.get_session() as session:
        query = select(CompanyRecord.company_id)
        if tenant_id:
            query = query.where(CompanyRecord.tenant_id == tenant_id)
        result = await session.execute(query)
        return [row[0] for row in result.fetchall()]


async def store_facts(
    db_manager: DatabaseManager,
    facts: list[dict[str, Any]],
    source: str,
    *,
    tenant_id: str | None = None,
) -> int:
    """Store fetched facts in database using the Fact repository pattern.

    Creates a GatheringBatch, then persists each fact as a proper Fact ORM
    record in the ``facts`` table.  Also updates the legacy
    ``CompanyRecord.raw_data`` blob so downstream code that reads from it
    continues to work.

    STORY-066: When tenant_id is provided, validates that each fact's
    company belongs to the specified tenant before writing.

    Args:
        db_manager: Initialised DatabaseManager.
        facts: List of fact dicts.  Each dict must contain at least
            ``company_id``; ``fact_type``/``type`` and ``value`` are used
            when present.
        source: Name of the data source (e.g. ``"sec_edgar"``).
        tenant_id: Optional tenant ID. When set, only writes to companies
            belonging to this tenant.

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
                result = await session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
                record = result.scalar_one_or_none()

                if record is None:
                    logger.debug(f"[store_facts] No company record found for {company_id}, skipping fact from {source}")
                    continue

                # STORY-066: Enforce tenant isolation on writes
                if tenant_id and hasattr(record, "tenant_id") and record.tenant_id != tenant_id:
                    logger.warning(
                        f"[store_facts] Tenant mismatch: task tenant={tenant_id[:8]}... "
                        f"but company {company_id} belongs to tenant={record.tenant_id[:8] if record.tenant_id else 'None'}. "
                        f"Skipping write from {source}."
                    )
                    continue

                # --- Persist as a proper Fact record ---
                if fact_type:
                    numeric_value = None
                    value_str = None
                    if isinstance(fact_value, (int, float)) and not isinstance(fact_value, bool):
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
                legacy_record = cast(Any, record)
                if fact_type and fact_value is not None:
                    raw_data = cast(dict[str, Any], legacy_record.raw_data or {})
                    source_bucket = cast(dict[str, Any], raw_data.setdefault(source, {}))
                    source_bucket[fact_type] = fact_value
                    legacy_record.raw_data = raw_data

                legacy_record.last_updated = datetime.now(timezone.utc)
                stored_count += 1

            except Exception as e:  # noqa: BLE001 — per-fact isolation; log and continue
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

    Persists structured failure records to an append-only JSONL audit
    trail while preserving the in-memory list for backward compatibility.
    """

    def __init__(self, audit_path: Path | None = None):
        self.failed_jobs: list[dict[str, Any]] = []
        self.audit_path = audit_path or Path("data/output/dead_letter_queue.jsonl")

    def record_failure(
        self,
        task_name: str,
        task_id: str,
        error: Exception | str,
        attempt: int,
        **metadata: Any,
    ) -> dict[str, Any]:
        """Record a permanently failed job with durable structured metadata.

        Args:
            task_name: Name of the failed task.
            task_id: Celery task ID.
            error: The exception or error message.
            attempt: Final attempt number before giving up.
            **metadata: Optional keys: ``traceback_text``, ``context``.
        """
        timestamp = datetime.now(timezone.utc)
        error_message = str(error)
        error_type = type(error).__name__ if isinstance(error, Exception) else "TaskFailure"
        record = {
            "task_name": task_name,
            "task_id": task_id,
            "error": error_message,
            "error_type": error_type,
            "traceback": metadata.get("traceback_text"),
            "final_attempt": attempt,
            "timestamp": timestamp,
            "context": metadata.get("context") or {},
        }

        logger.error(
            f"[RETRY-FAILED] {task_name} (task_id={task_id}) permanently failed after {attempt} attempts: {error_type}: {error_message}"
        )
        self.failed_jobs.append(record)
        self._persist_record(record)
        self._track_record(error, record)
        return record

    def _persist_record(self, record: dict[str, Any]) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = dict(record)
        timestamp = serializable.get("timestamp")
        if isinstance(timestamp, datetime):
            serializable["timestamp"] = timestamp.isoformat()
        try:
            with self.audit_path.open("a", encoding="utf-8") as handle:
                _ = handle.write(json.dumps(serializable, default=str) + "\n")
        except Exception as exc:
            logger.error(f"[RETRY-FAILED] Failed to persist DLQ record to {self.audit_path}: {exc}")

    def _track_record(self, error: Exception | str, record: dict[str, Any]) -> None:
        context = {
            "task_name": record["task_name"],
            "task_id": record["task_id"],
            "final_attempt": record["final_attempt"],
            **(record.get("context") or {}),
        }
        if isinstance(error, Exception):
            global_error_tracker.track_error(error, context=context)
            return
        global_error_tracker.track_error(RuntimeError(str(error)), context=context)


# Global Dead Letter Queue instance
dead_letter_queue = DeadLetterQueue()
