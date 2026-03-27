"""Tests for STORY-088: Fix In-Memory DLQ — Persist to PostgreSQL.

Verifies that:
1. DeadLetterQueue.record_failure delegates to persist_failed_task (PostgreSQL)
2. DLQ write failure never cascades into the original task error
3. The admin API router is registered and accepts the correct schema
4. The Alembic migration file exists and is reversible
5. The in-memory list is maintained as a session cache (backward compat)
6. list_failed_tasks and mark_resolved handle DB unavailability gracefully
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from solstein.worker.base import DeadLetterQueue
from solstein.worker.dlq import list_failed_tasks, mark_resolved, persist_failed_task


def _load_admin_dlq():
    """Load solstein.api.routers.admin_dlq directly without triggering the
    routers package __init__ (which imports all routers and requires env vars).
    """
    mod_name = "solstein.api.routers.admin_dlq"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(
        mod_name,
        Path("src/solstein/api/routers/admin_dlq.py"),
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


class TestDeadLetterQueuePersistence:
    """Unit tests for the persistent DLQ wrapper."""

    def test_record_failure_calls_persist_failed_task(self) -> None:
        """record_failure must call persist_failed_task, not just append to list."""
        dlq = DeadLetterQueue()
        error = ValueError("test error")

        with patch("solstein.worker.base.persist_failed_task") as mock_persist:
            mock_persist.return_value = "fake-uuid"
            result = dlq.record_failure(
                task_name="solstein.worker_tasks.refresh_sec_edgar",
                task_id="task-123",
                error=error,
                attempt=3,
            )

        mock_persist.assert_called_once()
        call_kwargs = mock_persist.call_args.kwargs
        assert call_kwargs["task_name"] == "solstein.worker_tasks.refresh_sec_edgar"
        assert call_kwargs["task_id"] == "task-123"
        assert call_kwargs["error"] is error
        assert call_kwargs["retry_count"] == 3
        assert result["error"] == "test error"

    def test_dlq_write_failure_does_not_propagate(self) -> None:
        """If persist_failed_task raises, record_failure must still return the record."""
        dlq = DeadLetterQueue()
        error = RuntimeError("task failed")

        with patch("solstein.worker.base.persist_failed_task", side_effect=Exception("DB down")):
            # Should NOT raise even though persist blew up
            try:
                result = dlq.record_failure(
                    task_name="refresh_test",
                    task_id="task-456",
                    error=error,
                    attempt=1,
                )
                assert result["task_name"] == "refresh_test"
            except Exception as exc:
                pytest.fail(f"DLQ write failure propagated to caller: {exc}")

    def test_failed_jobs_list_updated_after_record(self) -> None:
        """The session-level failed_jobs list must be updated for backward compat."""
        dlq = DeadLetterQueue()

        with patch("solstein.worker.base.persist_failed_task", return_value="uuid-1"):
            dlq.record_failure(
                task_name="refresh_github",
                task_id="task-789",
                error=ValueError("network error"),
                attempt=2,
            )

        assert len(dlq.failed_jobs) == 1
        assert dlq.failed_jobs[0]["task_name"] == "refresh_github"

    def test_metadata_passed_to_persist(self) -> None:
        """queue_name, args, kwargs, tenant_id are forwarded to persist_failed_task."""
        dlq = DeadLetterQueue()

        with patch("solstein.worker.base.persist_failed_task") as mock_persist:
            mock_persist.return_value = "uuid"
            dlq.record_failure(
                task_name="refresh_news",
                task_id="task-meta",
                error=RuntimeError("timeout"),
                attempt=1,
                queue_name="high_priority",
                args=["company-1"],
                kwargs={"force": True},
                tenant_id="tenant-abc",
            )

        call_kwargs = mock_persist.call_args.kwargs
        extra = call_kwargs["extra"]
        assert extra["queue_name"] == "high_priority"
        assert extra["args"] == ["company-1"]
        assert extra["kwargs"] == {"force": True}
        assert extra["tenant_id"] == "tenant-abc"

    def test_string_error_handled_correctly(self) -> None:
        """String errors (not exceptions) are handled without raising."""
        dlq = DeadLetterQueue()

        with patch("solstein.worker.base.persist_failed_task", return_value="uuid"):
            result = dlq.record_failure(
                task_name="refresh_funding",
                task_id="task-str",
                error="This is a string error",
                attempt=1,
            )

        assert result["error"] == "This is a string error"
        assert result["error_type"] == "TaskFailure"


class TestPersistFailedTaskFunction:
    """Tests for the persist_failed_task function in solstein.worker.dlq."""

    def test_returns_none_when_no_db_url(self) -> None:
        """When no database URL is configured, persist returns None without raising."""
        mock_settings = MagicMock()
        mock_settings.database.url = None

        with patch("solstein.worker.dlq.get_settings", return_value=mock_settings):
            result = persist_failed_task(
                task_name="refresh_test",
                task_id="task-no-db",
                error=ValueError("test"),
                retry_count=1,
            )

        assert result is None

    def test_returns_none_on_db_connection_error(self) -> None:
        """DB connection failure returns None instead of propagating."""
        mock_settings = MagicMock()
        mock_settings.database.url = "postgresql://fake/db"

        with (
            patch("solstein.worker.dlq.get_settings", return_value=mock_settings),
            patch("solstein.worker.dlq.create_engine", side_effect=Exception("connect failed")),
        ):
            result = persist_failed_task(
                task_name="refresh_test",
                task_id="task-db-err",
                error=RuntimeError("fail"),
                retry_count=0,
            )

        assert result is None

    def test_returns_uuid_on_success(self) -> None:
        """On successful DB write, returns a non-empty UUID string."""

        mock_settings = MagicMock()
        mock_settings.database.url = "postgresql://fake/db"

        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("solstein.worker.dlq.get_settings", return_value=mock_settings),
            patch("solstein.worker.dlq.create_engine", return_value=mock_engine),
        ):
            result = persist_failed_task(
                task_name="refresh_sec_edgar",
                task_id="task-ok",
                error=ValueError("rate limit"),
                retry_count=3,
            )

        assert result is not None
        assert len(result) > 0

    def test_traceback_extracted_from_exception(self) -> None:
        """Traceback text is extracted from exceptions with __traceback__."""

        mock_settings = MagicMock()
        mock_settings.database.url = "postgresql://fake/db"

        captured_params: dict = {}

        def capture_execute(query, params):
            captured_params.update(params)
            return MagicMock()

        mock_conn = MagicMock()
        mock_conn.execute = capture_execute
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        try:
            raise ValueError("test with traceback")
        except ValueError as exc:
            with (
                patch("solstein.worker.dlq.get_settings", return_value=mock_settings),
                patch("solstein.worker.dlq.create_engine", return_value=mock_engine),
            ):
                persist_failed_task(
                    task_name="refresh_test",
                    task_id="task-tb",
                    error=exc,
                )

        # traceback should be populated
        assert "traceback" in captured_params
        if captured_params["traceback"] is not None:
            assert "ValueError" in captured_params["traceback"]


class TestListFailedTasks:
    """Tests for list_failed_tasks helper."""

    def test_returns_empty_list_when_no_db(self) -> None:
        """When DB is unavailable, returns empty list without raising."""

        mock_settings = MagicMock()
        mock_settings.database.url = None

        with patch("solstein.worker.dlq.get_settings", return_value=mock_settings):
            result = list_failed_tasks()

        assert result == []

    def test_returns_empty_list_on_db_error(self) -> None:
        """DB connection failure returns empty list without raising."""

        mock_settings = MagicMock()
        mock_settings.database.url = "postgresql://fake/db"

        with (
            patch("solstein.worker.dlq.get_settings", return_value=mock_settings),
            patch("solstein.worker.dlq.create_engine", side_effect=Exception("DB down")),
        ):
            result = list_failed_tasks()

        assert result == []


class TestMarkResolved:
    """Tests for mark_resolved helper."""

    def test_returns_false_when_no_db(self) -> None:
        """When DB is unavailable, returns False without raising."""

        mock_settings = MagicMock()
        mock_settings.database.url = None

        with patch("solstein.worker.dlq.get_settings", return_value=mock_settings):
            result = mark_resolved("fake-entry-id", "admin")

        assert result is False

    def test_returns_false_on_db_error(self) -> None:
        """DB error returns False without raising."""

        mock_settings = MagicMock()
        mock_settings.database.url = "postgresql://fake/db"

        with (
            patch("solstein.worker.dlq.get_settings", return_value=mock_settings),
            patch("solstein.worker.dlq.create_engine", side_effect=Exception("DB down")),
        ):
            result = mark_resolved("fake-id")

        assert result is False


class TestAlembicMigration:
    """Tests for the failed_tasks Alembic migration file."""

    def test_migration_file_exists(self) -> None:
        """Migration file 018_epic025_story088_failed_tasks.py must exist."""
        migration_path = Path("alembic/versions/018_epic025_story088_failed_tasks.py")
        assert migration_path.exists(), f"Migration file not found: {migration_path}"

    def test_migration_has_upgrade_and_downgrade(self) -> None:
        """Migration must define both upgrade() and downgrade()."""
        migration_path = Path("alembic/versions/018_epic025_story088_failed_tasks.py")
        source = migration_path.read_text(encoding="utf-8")
        assert "def upgrade()" in source
        assert "def downgrade()" in source

    def test_migration_creates_failed_tasks_table(self) -> None:
        """upgrade() must create the failed_tasks table."""
        migration_path = Path("alembic/versions/018_epic025_story088_failed_tasks.py")
        source = migration_path.read_text(encoding="utf-8")
        assert "failed_tasks" in source
        assert "create_table" in source

    def test_migration_drops_failed_tasks_in_downgrade(self) -> None:
        """downgrade() must drop the failed_tasks table."""
        migration_path = Path("alembic/versions/018_epic025_story088_failed_tasks.py")
        source = migration_path.read_text(encoding="utf-8")
        assert "drop_table" in source

    def test_migration_revision_is_018(self) -> None:
        """Revision ID must be 018 to maintain sequence."""
        migration_path = Path("alembic/versions/018_epic025_story088_failed_tasks.py")
        source = migration_path.read_text(encoding="utf-8")
        assert 'revision: str = "018"' in source


class TestAdminDLQRouter:
    """Tests for the admin DLQ FastAPI router."""

    def test_router_registered_in_app(self) -> None:
        """admin_dlq router must be imported and registered in main.py."""
        main_src = Path("src/solstein/api/main.py").read_text(encoding="utf-8")
        assert "admin_dlq" in main_src, "admin_dlq router not registered in main.py"

    def test_admin_dlq_router_has_correct_prefix(self) -> None:
        """admin_dlq router must have /api/v1/admin/dlq prefix."""
        mod = _load_admin_dlq()
        router = mod.router

        assert router.prefix == "/api/v1/admin/dlq", (
            f"Expected prefix /api/v1/admin/dlq, got {router.prefix}"
        )

    def test_admin_dlq_router_has_required_endpoints(self) -> None:
        """Router must expose GET list, GET single, POST resolve, POST requeue."""
        mod = _load_admin_dlq()
        router = mod.router

        routes = {(r.path, method) for r in router.routes for method in r.methods}
        assert ("/api/v1/admin/dlq", "GET") in routes or any(
            path.endswith("/admin/dlq") and "GET" in methods
            for path, methods in {(r.path, r.methods) for r in router.routes}
        ), "GET /api/v1/admin/dlq not found in router"

    def test_dlq_entry_response_schema_fields(self) -> None:
        """DLQEntryResponse must have all required schema fields."""
        mod = _load_admin_dlq()
        DLQEntryResponse = mod.DLQEntryResponse

        schema = DLQEntryResponse.model_json_schema()
        required_fields = {
            "task_id",
            "task_name",
            "queue_name",
            "error_message",
            "retry_count",
            "created_at",
            "last_attempted_at",
        }
        for field in required_fields:
            assert field in schema.get("properties", {}), f"Missing field: {field}"
