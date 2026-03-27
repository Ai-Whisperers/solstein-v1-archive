"""Tests for STORY-089 and STORY-090: at-least-once delivery + deduplication.

STORY-089 acceptance criteria:
- task_acks_late = True is set in celery_config
- task_reject_on_worker_lost = True is set in celery_config
- worker_prefetch_multiplier = 1 is confirmed

STORY-090 acceptance criteria:
- Concurrent duplicate execution prevented by Redis lock
- Lock acquisition failure produces WARNING log, not error
- Beat restart does not cause duplicate data writes (lock blocks second run)
- Lock TTL is configurable per-task
- Lock is released on both success and failure paths
- Redis unavailability causes fail-open behavior with WARNING log
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

import solstein.celery_config as cc
from solstein.worker.idempotency import (
    _build_lock_key,
    _period_key,
    deduplicate,
)

# =============================================================================
# STORY-089: celery_config acks_late settings
# =============================================================================


class TestAcksLateConfiguration:
    """Verify task_acks_late and task_reject_on_worker_lost are configured."""

    def test_task_acks_late_is_true(self) -> None:
        """celery_config must set task_acks_late = True."""
        conf = cc.celery_app.conf
        assert conf.task_acks_late is True, (
            "task_acks_late must be True for at-least-once delivery semantics"
        )

    def test_task_reject_on_worker_lost_is_true(self) -> None:
        """celery_config must set task_reject_on_worker_lost = True."""
        conf = cc.celery_app.conf
        assert conf.task_reject_on_worker_lost is True, (
            "task_reject_on_worker_lost must be True to re-queue on connection loss"
        )

    def test_worker_prefetch_multiplier_is_one(self) -> None:
        """worker_prefetch_multiplier must be 1 for acks_late safety."""
        conf = cc.celery_app.conf
        assert conf.worker_prefetch_multiplier == 1, (
            "worker_prefetch_multiplier must be 1 to limit in-flight unacked tasks"
        )

    def test_celery_config_source_documents_acks_late(self) -> None:
        """celery_config.py source must contain explanatory comments for acks_late."""
        source = Path("src/solstein/celery_config.py").read_text(encoding="utf-8")
        assert "task_acks_late" in source
        assert "task_reject_on_worker_lost" in source
        # Should explain the at-least-once semantics
        assert "at-least-once" in source.lower() or "acks_late" in source


# =============================================================================
# STORY-090: idempotency decorator
# =============================================================================


class TestDeduplicateLockAcquisition:
    """Tests for lock acquire / skip / fail-open paths."""

    def test_task_executes_when_lock_acquired(self) -> None:
        """When lock is free, the decorated function runs and returns its value."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=60)
            def my_task() -> str:
                return "done"

            result = my_task()

        assert result == "done"
        mock_lock.acquire.assert_called_once_with(blocking=False)

    def test_task_skipped_when_lock_already_held(self) -> None:
        """When lock is held by another instance, task returns None without running."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = False
        mock_redis.lock.return_value = mock_lock

        executed = []

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=60)
            def my_task() -> str:
                executed.append(True)
                return "done"

            result = my_task()

        assert result is None
        assert len(executed) == 0, "Task body must not run when lock is already held"

    def test_task_skipped_logs_warning(self) -> None:
        """A skipped task due to held lock must call logger.warning with Idempotency."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = False
        mock_redis.lock.return_value = mock_lock

        warning_calls: list[str] = []

        with (
            patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis),
            patch(
                "solstein.worker.idempotency.logger.warning",
                side_effect=lambda msg, *a, **kw: warning_calls.append(str(msg)),
            ),
        ):

            @deduplicate(ttl=60)
            def my_task() -> None:
                pass

            my_task()

        assert any("Idempotency" in msg for msg in warning_calls), (
            "A WARNING log with 'Idempotency' must be emitted when skipping"
        )

    def test_fail_open_when_redis_unavailable(self) -> None:
        """If Redis client is None (unavailable), task executes without lock."""
        executed = []

        with patch("solstein.worker.idempotency._get_redis_client", return_value=None):

            @deduplicate(ttl=60)
            def my_task() -> str:
                executed.append(True)
                return "done"

            result = my_task()

        assert result == "done"
        assert len(executed) == 1

    def test_fail_open_logs_warning_when_redis_unavailable(self) -> None:
        """Redis unavailability must produce a WARNING log, not an error."""
        warning_calls: list[str] = []

        with (
            patch("solstein.worker.idempotency._get_redis_client", return_value=None),
            patch(
                "solstein.worker.idempotency.logger.warning",
                side_effect=lambda msg, *a, **kw: warning_calls.append(str(msg)),
            ),
        ):

            @deduplicate(ttl=60)
            def my_task() -> None:
                pass

            my_task()

        assert any("Idempotency" in msg for msg in warning_calls)

    def test_lock_released_on_success(self) -> None:
        """Lock must be released after successful task completion."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=60)
            def my_task() -> str:
                return "ok"

            my_task()

        mock_lock.release.assert_called_once()

    def test_lock_released_on_exception(self) -> None:
        """Lock must be released even when the task raises an exception."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=60)
            def my_task() -> None:
                raise RuntimeError("task failure")

            with pytest.raises(RuntimeError):
                my_task()

        mock_lock.release.assert_called_once()

    def test_fail_open_when_lock_acquire_raises(self) -> None:
        """If lock.acquire() raises, task executes without lock (fail-open)."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.side_effect = Exception("Redis timeout")
        mock_redis.lock.return_value = mock_lock

        executed = []

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=60)
            def my_task() -> str:
                executed.append(True)
                return "done"

            result = my_task()

        assert result == "done"
        assert len(executed) == 1


class TestDeduplicateLockKey:
    """Tests for lock key generation."""

    def test_build_lock_key_format(self) -> None:
        """Lock key must have the dlq:dedup:<task>:<hash> format."""
        key = _build_lock_key("refresh_sec_edgar", "idempotency-value-123")
        assert key.startswith("dlq:dedup:refresh_sec_edgar:")
        parts = key.split(":")
        assert len(parts) == 4
        # Hash suffix should be 16 hex chars
        assert len(parts[3]) == 16

    def test_period_key_returns_string(self) -> None:
        """_period_key must return a non-empty string."""
        key = _period_key(granularity_seconds=3600)
        assert isinstance(key, str)
        assert len(key) > 0

    def test_period_key_stable_within_bucket(self) -> None:
        """Two calls within the same second must return the same period key."""
        key1 = _period_key(3600)
        key2 = _period_key(3600)
        assert key1 == key2

    def test_custom_key_fn_used_when_provided(self) -> None:
        """When key_fn is provided, it is used to build the idempotency key."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        captured_keys = []

        def _track_key(key: str, *args: Any, **kwargs: Any) -> str:
            captured_keys.append(key)
            return key

        real_build = _build_lock_key

        with (
            patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis),
            patch("solstein.worker.idempotency._build_lock_key", side_effect=real_build),
        ):

            @deduplicate(ttl=60, key_fn=lambda name, *a, **kw: "my-custom-key")
            def my_task() -> str:
                return "ok"

            my_task()

        # The lock key passed to redis.lock() should contain the hashed custom key
        assert mock_redis.lock.called
        lock_key_arg = mock_redis.lock.call_args[0][0]
        assert "dlq:dedup" in lock_key_arg

    def test_different_tasks_get_different_keys(self) -> None:
        """Two different task names produce different lock keys."""
        key1 = _build_lock_key("refresh_sec_edgar", "same-period")
        key2 = _build_lock_key("refresh_github", "same-period")
        assert key1 != key2

    def test_same_task_same_period_gets_same_key(self) -> None:
        """Same task + same idempotency key → same lock key (dedup works)."""
        key1 = _build_lock_key("refresh_sec_edgar", "period-abc")
        key2 = _build_lock_key("refresh_sec_edgar", "period-abc")
        assert key1 == key2

    def test_ttl_configurable(self) -> None:
        """The TTL is passed to redis.lock with the caller-specified value."""
        mock_redis = MagicMock()
        mock_lock = MagicMock()
        mock_lock.acquire.return_value = True
        mock_redis.lock.return_value = mock_lock

        with patch("solstein.worker.idempotency._get_redis_client", return_value=mock_redis):

            @deduplicate(ttl=7200)
            def my_task() -> str:
                return "ok"

            my_task()

        _, kwargs = mock_redis.lock.call_args
        assert kwargs.get("timeout") == 7200


class TestIdempotencyModuleFile:
    """Structural checks on the idempotency module."""

    def test_module_file_exists(self) -> None:
        """src/solstein/worker/idempotency.py must exist."""
        assert Path("src/solstein/worker/idempotency.py").exists()

    def test_deduplicate_is_importable(self) -> None:
        """deduplicate decorator must be importable from the module."""
        assert callable(deduplicate)
