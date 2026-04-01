"""Redis-based task deduplication lock for at-least-once Celery delivery.

STORY-090: With task_acks_late=True (STORY-089) tasks become at-least-once.
Beat scheduler restarts and worker evictions can cause the same task to execute
more than once within the same schedule period. This module provides a
distributed lock that prevents concurrent duplicate execution while allowing
the same task to run again in its next scheduled period.

Usage
-----
Wrap a Celery task with ``@deduplicate`` to acquire the lock before execution:

    from solstein.worker.idempotency import deduplicate

    @celery_app.task
    @deduplicate(ttl=3600)
    def refresh_sec_edgar():
        ...

The lock key is: ``dlq:dedup:<task_name>:<idempotency_key>``
The idempotency key defaults to the current UTC hour-period so the same task
can run again in the next scheduled window without being blocked.

Design decisions
----------------
- **Fail-open**: if Redis is unreachable the task executes (data collection
  is preferable to silent skips). Log WARNING on lock-acquire failure.
- **Blocking=False**: we never wait for the lock. If already held, we skip
  and log WARNING — the original execution is still in progress.
- **redis-py Lock**: uses the built-in Lock with owner verification and
  atomic release (Lua script) rather than a hand-rolled SETNX.
- **TTL >= task time_limit**: callers must pass a TTL that covers the maximum
  expected task duration. If the task runs longer than TTL the lock expires
  and a concurrent duplicate is allowed (prefer stale lock expiry over
  indefinite blocking).
"""

from __future__ import annotations

import functools
import hashlib
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from loguru import logger

try:
    import redis as redis_lib
except ImportError:  # pragma: no cover
    redis_lib = None  # type: ignore[assignment]

from solstein.config import get_settings

_LOCK_PREFIX = "dlq:dedup"
_DEFAULT_TTL = 3600  # seconds — 1 hour; override per task via ttl=


def _get_redis_client():
    """Return a synchronous Redis client from settings, or None if unavailable."""
    try:
        if redis_lib is None:
            return None

        settings = get_settings()
        redis_url: str | None = None
        if hasattr(settings, "celery_result_backend") and settings.celery_result_backend:
            redis_url = settings.celery_result_backend
        elif hasattr(settings, "celery_broker_url") and settings.celery_broker_url:
            redis_url = settings.celery_broker_url

        if not redis_url or not redis_url.startswith("redis"):
            return None

        return redis_lib.from_url(redis_url, decode_responses=True, socket_timeout=2)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[Idempotency] Cannot connect to Redis for lock: %s", exc)
        return None


def _period_key(granularity_seconds: int = 3600) -> str:
    """Return a time-bucketed key string so the same task reruns in the next period.

    Default: 1-hour buckets (3600 s). Override granularity for finer or coarser
    deduplication windows.
    """
    now = datetime.now(timezone.utc)
    epoch = int(now.timestamp())
    bucket = epoch // granularity_seconds
    return str(bucket)


def _build_lock_key(task_name: str, idempotency_key: str) -> str:
    """Build a Redis key for the deduplication lock."""
    hashed = hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
    return f"{_LOCK_PREFIX}:{task_name}:{hashed}"


def deduplicate(
    ttl: int = _DEFAULT_TTL,
    key_fn: Callable[..., str] | None = None,
    granularity: int = 3600,
    task_name_override: str | None = None,
) -> Callable:
    """Decorator that prevents concurrent duplicate Celery task execution.

    Acquires a Redis lock before the task runs. If the lock is already held
    (meaning an identical task is already running), logs WARNING and returns
    None immediately without running the task body.

    On Redis unavailability: fail-open — the task executes without the lock
    (data collection is preferable to silent skips).

    Args:
        ttl: Lock TTL in seconds. Must be >= the task's time_limit. Default 3600.
        key_fn: Optional callable(task_name, *args, **kwargs) -> str that returns
                the idempotency key. Defaults to time-bucketed period key.
        granularity: Period bucket size in seconds (default 3600 = 1 hour).
                     Used only when key_fn is None.
        task_name_override: Explicit task name for the lock key. Required when
                            applying to factory-generated closures where
                            ``func.__name__`` is generic (e.g. "refresh_task").
                            Uses ``func.__name__`` if not provided.

    Returns:
        Decorator that wraps the task function with deduplication logic.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            task_name = task_name_override or func.__name__
            if key_fn is not None:
                idempotency_key = key_fn(task_name, *args, **kwargs)
            else:
                idempotency_key = _period_key(granularity)

            lock_key = _build_lock_key(task_name, idempotency_key)
            client = _get_redis_client()

            if client is None:
                logger.warning(
                    "[Idempotency] Redis unavailable — executing %s without dedup lock "
                    "(fail-open). Duplicate execution possible during Redis downtime.",
                    task_name,
                )
                return func(*args, **kwargs)

            try:
                lock = client.lock(lock_key, timeout=ttl, blocking_timeout=0)
                acquired = lock.acquire(blocking=False)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[Idempotency] Lock acquire error for %s — executing without lock "
                    "(fail-open): %s",
                    task_name,
                    exc,
                )
                return func(*args, **kwargs)

            if not acquired:
                logger.warning(
                    "[Idempotency] Lock already held for %s (key=%s) — "
                    "skipping duplicate execution. Another instance is in progress.",
                    task_name,
                    lock_key,
                )
                return None

            try:
                return func(*args, **kwargs)
            finally:
                _safe_release(lock, task_name, lock_key)

        return wrapper

    return decorator


def _safe_release(lock: Any, task_name: str, lock_key: str) -> None:
    """Release a Redis lock, logging on error but never raising."""
    try:
        lock.release()
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "[Idempotency] Failed to release lock for %s (key=%s): %s",
            task_name,
            lock_key,
            exc,
        )
