"""Persistent Dead Letter Queue (DLQ) backed by PostgreSQL.

STORY-088: Replaces the in-memory DeadLetterQueue class which evaporated on every
worker restart with no recovery path. Failed tasks are now written to the
`failed_tasks` PostgreSQL table before the task terminates, so they survive
worker crashes, pod evictions, and deployments.

Design decisions:
- Short-lived connection: DLQ writes use a separate short-lived connection (not
  the main application pool) to avoid coupling DLQ durability to application DB health.
- Fail-open: a DLQ write failure never causes the original task to fail with a
  different error. If the write fails, we log at ERROR and continue with the
  original error propagation.
- Admin API: see api/routers/admin_dlq.py for list/inspect/re-queue endpoints.
- Alerting: callers should monitor unresolved DLQ count; alert at > 10 in 1 hour.
"""

from __future__ import annotations

import traceback as tb_module
import uuid
from datetime import datetime, timezone
from typing import Any

from loguru import logger
from sqlalchemy import create_engine, text

from solstein.config import get_settings

_INSERT_SQL = text(
    """
    INSERT INTO failed_tasks (
        task_id, task_name, queue_name, args, kwargs,
        error_message, traceback, retry_count, tenant_id,
        created_at, last_attempted_at
    ) VALUES (
        :task_id, :task_name, :queue_name, :args, :kwargs,
        :error_message, :traceback, :retry_count, :tenant_id,
        :created_at, :last_attempted_at
    )
    """
)


def _get_db_url() -> str | None:
    """Return the configured database URL, or None if not set."""
    settings = get_settings()
    return settings.database.url if hasattr(settings.database, "url") else None


def _build_insert_params(
    task_name: str,
    task_id: str,
    error: Exception | str,
    retry_count: int,
    extra: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Build (entry_id, params_dict) for the failed_tasks INSERT.

    Generates a new UUID for the DLQ entry and returns it alongside the
    full parameter dict ready to pass to SQLAlchemy text().
    """
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    traceback_text = (
        "".join(tb_module.format_exception(type(error), error, error.__traceback__))
        if isinstance(error, Exception) and error.__traceback__ is not None
        else None
    )
    params: dict[str, Any] = {
        "task_id": entry_id,
        "task_name": task_name,
        "queue_name": extra.get("queue_name", "default"),
        "args": extra.get("args") or [],
        "kwargs": extra.get("kwargs") or {},
        "error_message": str(error),
        "traceback": traceback_text,
        "retry_count": retry_count,
        "tenant_id": extra.get("tenant_id"),
        "created_at": now,
        "last_attempted_at": now,
    }
    return entry_id, params


def persist_failed_task(
    task_name: str,
    task_id: str,
    error: Exception | str,
    retry_count: int = 0,
    extra: dict[str, Any] | None = None,
) -> str | None:
    """Write a failed task record to the failed_tasks PostgreSQL table.

    This function is intentionally synchronous so it can be called from both
    sync and async task contexts without executor overhead.

    DLQ write failures do NOT propagate — they are logged at ERROR and the
    function returns None. Never let a DLQ write mask the original task error.

    Args:
        task_name: Celery task name (e.g. 'solstein.worker_tasks.refresh_sec_edgar').
        task_id: Celery task ID (UUID string).
        error: The exception that caused permanent failure, or a string message.
        retry_count: Number of retries attempted before giving up.
        extra: Optional metadata dict with keys: queue_name, args, kwargs, tenant_id.
               Polling contract: callers must not rely on in-memory state; read DB.

    Returns:
        The new DLQ entry UUID (str) if write succeeded, else None.
    """
    extra = extra or {}

    try:
        db_url = _get_db_url()
        if not db_url:
            logger.warning(
                "[DLQ] No database URL configured — cannot persist failed task. "
                "task_name=%s task_id=%s error=%s",
                task_name,
                task_id,
                str(error)[:200],
            )
            return None

        entry_id, params = _build_insert_params(task_name, task_id, error, retry_count, extra)
        engine = create_engine(db_url, pool_size=1, max_overflow=0, pool_timeout=5)
        with engine.connect() as conn:
            conn.execute(_INSERT_SQL, params)
            conn.commit()
        engine.dispose()

        logger.error(
            "[DLQ] Persisted failed task to PostgreSQL. "
            "entry_id=%s task_name=%s task_id=%s retry_count=%d error=%s",
            entry_id,
            task_name,
            task_id,
            retry_count,
            str(error)[:200],
        )
        return entry_id

    except Exception as dlq_exc:
        # DLQ write failure must NEVER cascade into the original error path.
        logger.error(
            "[DLQ] Failed to persist failed task record. "
            "task_name=%s task_id=%s dlq_error=%s",
            task_name,
            task_id,
            str(dlq_exc)[:500],
        )
        return None


def mark_resolved(entry_id: str, resolved_by: str = "system") -> bool:
    """Mark a DLQ entry as resolved (after manual re-queue or fix).

    Args:
        entry_id: The DLQ entry UUID to resolve.
        resolved_by: Who resolved it (user email or 'system' for automated re-queue).

    Returns:
        True if the entry was found and updated, False otherwise.
    """
    now = datetime.now(timezone.utc)
    try:
        db_url = _get_db_url()
        if not db_url:
            return False

        engine = create_engine(db_url, pool_size=1, max_overflow=0, pool_timeout=5)
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    UPDATE failed_tasks
                    SET resolved_at = :resolved_at, resolved_by = :resolved_by
                    WHERE task_id = :task_id AND resolved_at IS NULL
                    RETURNING task_id
                    """
                ),
                {"task_id": entry_id, "resolved_at": now, "resolved_by": resolved_by},
            )
            updated = result.fetchone() is not None
            conn.commit()
        engine.dispose()
        return updated

    except Exception as exc:
        logger.error("[DLQ] Failed to mark entry %s as resolved: %s", entry_id, exc)
        return False


def list_failed_tasks(
    *,
    queue_name: str | None = None,
    task_name: str | None = None,
    resolved: bool | None = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List DLQ entries with optional filters.

    Args:
        queue_name: Filter by queue name.
        task_name: Filter by task name (prefix match).
        resolved: None = all, True = resolved only, False = unresolved only.
        limit: Maximum rows to return.
        offset: Pagination offset.

    Returns:
        List of DLQ entry dicts.
    """
    try:
        db_url = _get_db_url()
        if not db_url:
            return []

        filters: list[str] = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if queue_name:
            filters.append("queue_name = :queue_name")
            params["queue_name"] = queue_name
        if task_name:
            filters.append("task_name LIKE :task_name_pat")
            params["task_name_pat"] = f"{task_name}%"
        if resolved is True:
            filters.append("resolved_at IS NOT NULL")
        elif resolved is False:
            filters.append("resolved_at IS NULL")

        where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""
        query = text(
            f"""
            SELECT task_id, task_name, queue_name, error_message, traceback,
                   retry_count, tenant_id, created_at, last_attempted_at,
                   resolved_at, resolved_by
            FROM failed_tasks
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """
        )

        engine = create_engine(db_url, pool_size=1, max_overflow=0, pool_timeout=5)
        rows: list[dict[str, Any]] = []
        with engine.connect() as conn:
            result = conn.execute(query, params)
            for row in result:
                rows.append(dict(row._mapping))
        engine.dispose()
        return rows

    except Exception as exc:
        logger.error("[DLQ] Failed to list failed tasks: %s", exc)
        return []
