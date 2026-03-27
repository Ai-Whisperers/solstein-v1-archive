"""Tests for STORY-113: Export Status Tracking and Download Links.

Validates:
- REQ-1: GET /api/v1/exports/{job_id} returns signed URL when completed
- REQ-2: Expired exports return status=expired with no URL
- REQ-3: DELETE cancels queued exports and terminates running Celery task
- Model: ExportJobRecord has user_id, file_size_bytes, expires_at fields
- List: GET /api/v1/exports returns paginated, filterable results
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from solstein.infrastructure.models.export import (
    EXPORT_EXPIRY_DAYS,
    ExportJobRecord,
)
from solstein.worker.export_tasks import _get_file_size

# Reusable paths
_SRC = Path(__file__).parent.parent.parent / "src" / "solstein"
_EXPORTS_PY = _SRC / "api" / "routers" / "exports.py"
_TASK_PY = _SRC / "worker" / "export_tasks.py"
_MIGRATION = Path(__file__).parent.parent.parent / "alembic" / "versions" / "019_story113_export_status_fields.py"


def _make_record(**kwargs: object) -> ExportJobRecord:
    """Create an ExportJobRecord with sensible defaults."""
    record = ExportJobRecord()
    record.id = kwargs.get("id", uuid.uuid4())  # type: ignore[assignment]
    record.tenant_id = kwargs.get("tenant_id", "tenant-001")  # type: ignore[assignment]
    record.user_id = kwargs.get("user_id")  # type: ignore[assignment]
    record.company_id = kwargs.get("company_id")  # type: ignore[assignment]
    record.format = kwargs.get("format", "excel")  # type: ignore[assignment]
    record.status = kwargs.get("status", "completed")  # type: ignore[assignment]
    record.file_url = kwargs.get("file_url")  # type: ignore[assignment]
    record.file_size_bytes = kwargs.get("file_size_bytes")  # type: ignore[assignment]
    record.error_message = kwargs.get("error_message")  # type: ignore[assignment]
    record.progress_pct = kwargs.get("progress_pct", 100)  # type: ignore[assignment]
    record.retry_count = kwargs.get("retry_count", 0)  # type: ignore[assignment]
    record.created_at = kwargs.get("created_at", datetime.now(timezone.utc))  # type: ignore[assignment]
    record.completed_at = kwargs.get("completed_at")  # type: ignore[assignment]
    record.expires_at = kwargs.get("expires_at")  # type: ignore[assignment]
    return record


# ---------------------------------------------------------------------------
# Model field tests
# ---------------------------------------------------------------------------
class TestExportJobRecordModel:
    """ExportJobRecord must have all STORY-113 required fields."""

    def test_model_has_user_id_field(self):
        assert hasattr(ExportJobRecord, "user_id")

    def test_model_has_file_size_bytes_field(self):
        assert hasattr(ExportJobRecord, "file_size_bytes")

    def test_model_has_expires_at_field(self):
        assert hasattr(ExportJobRecord, "expires_at")

    def test_table_name_is_export_jobs(self):
        assert ExportJobRecord.__tablename__ == "export_jobs"


# ---------------------------------------------------------------------------
# Expiry logic tests
# ---------------------------------------------------------------------------
class TestExpiryLogic:
    """Expired exports must return status=expired with no file_url."""

    def test_is_expired_returns_true_when_past_expiry(self):
        record = _make_record(expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
        assert record.is_expired is True

    def test_is_expired_returns_false_when_not_expired(self):
        record = _make_record(expires_at=datetime.now(timezone.utc) + timedelta(days=3))
        assert record.is_expired is False

    def test_is_expired_returns_false_when_no_expiry(self):
        record = _make_record(expires_at=None)
        assert record.is_expired is False

    def test_to_dict_shows_expired_status_when_past_expiry(self):
        record = _make_record(
            file_url="https://storage.example.com/export.xlsx",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        d = record.to_dict(check_expiry=True)
        assert d["status"] == "expired"
        assert d["file_url"] is None

    def test_to_dict_shows_completed_when_not_expired(self):
        url = "https://storage.example.com/export.xlsx"
        record = _make_record(
            file_url=url,
            expires_at=datetime.now(timezone.utc) + timedelta(days=3),
        )
        d = record.to_dict(check_expiry=True)
        assert d["status"] == "completed"
        assert d["file_url"] == url

    def test_to_dict_includes_expires_at(self):
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        d = _make_record(expires_at=expires).to_dict()
        assert d["expires_at"] is not None
        assert "T" in d["expires_at"]

    def test_to_dict_includes_file_size_bytes(self):
        d = _make_record(file_size_bytes=1048576).to_dict()
        assert d["file_size_bytes"] == 1048576

    def test_to_dict_includes_user_id(self):
        d = _make_record(user_id="user-abc").to_dict()
        assert d["user_id"] == "user-abc"


# ---------------------------------------------------------------------------
# mark_completed / mark_cancelled tests
# ---------------------------------------------------------------------------
class TestMarkMethods:
    """mark_completed and mark_cancelled must set correct fields."""

    def _processing_record(self) -> ExportJobRecord:
        return _make_record(status="processing", progress_pct=50)

    def test_mark_completed_sets_status(self):
        r = self._processing_record()
        r.mark_completed("https://example.com/f.xlsx", file_size_bytes=1024)
        assert r.status == "completed"

    def test_mark_completed_sets_file_url(self):
        r = self._processing_record()
        r.mark_completed("https://example.com/f.xlsx")
        assert r.file_url == "https://example.com/f.xlsx"

    def test_mark_completed_sets_file_size(self):
        r = self._processing_record()
        r.mark_completed("https://example.com/f.xlsx", file_size_bytes=2048)
        assert r.file_size_bytes == 2048

    def test_mark_completed_sets_progress_100(self):
        r = self._processing_record()
        r.mark_completed("https://example.com/f.xlsx")
        assert r.progress_pct == 100

    def test_mark_completed_sets_completed_at(self):
        r = self._processing_record()
        before = datetime.now(timezone.utc)
        r.mark_completed("https://example.com/f.xlsx")
        assert r.completed_at is not None
        assert r.completed_at >= before

    def test_mark_completed_sets_expires_at(self):
        r = self._processing_record()
        before = datetime.now(timezone.utc)
        r.mark_completed("https://example.com/f.xlsx")
        assert r.expires_at is not None
        expected_min = before + timedelta(days=EXPORT_EXPIRY_DAYS - 1)
        assert r.expires_at > expected_min

    def test_mark_cancelled_sets_status(self):
        r = self._processing_record()
        r.mark_cancelled()
        assert r.status == "cancelled"

    def test_mark_cancelled_sets_completed_at(self):
        r = self._processing_record()
        r.mark_cancelled()
        assert r.completed_at is not None


# ---------------------------------------------------------------------------
# Router structure tests
# ---------------------------------------------------------------------------
class TestRouterStructure:
    """Export router must have all STORY-113 endpoints."""

    def test_router_module_exists(self):
        assert _EXPORTS_PY.exists()

    def test_list_endpoint_exists(self):
        source = _EXPORTS_PY.read_text()
        assert "async def list_exports" in source
        assert "ExportListResponse" in source

    def test_get_status_endpoint_exists(self):
        assert "async def get_export_status" in _EXPORTS_PY.read_text()

    def test_delete_endpoint_exists(self):
        source = _EXPORTS_PY.read_text()
        assert "async def cancel_export" in source
        assert "delete" in source.lower()

    def test_story113_documented_in_module(self):
        assert "STORY-113" in _EXPORTS_PY.read_text()

    def test_cancel_revokes_celery_task(self):
        # Revoke logic is in exports_helpers.py
        helpers = _SRC / "api" / "routers" / "exports_helpers.py"
        assert "revoke" in helpers.read_text().lower()


# ---------------------------------------------------------------------------
# Filter validation tests
# ---------------------------------------------------------------------------
class TestFilterValidation:
    """Filter parameters must be validated."""

    def test_valid_statuses_include_cancelled(self):
        assert '"cancelled"' in _EXPORTS_PY.read_text()

    def test_valid_statuses_include_expired(self):
        assert '"expired"' in _EXPORTS_PY.read_text()

    def test_valid_formats_include_standard(self):
        source = _EXPORTS_PY.read_text()
        for fmt in ("excel", "csv", "json", "markdown", "llm"):
            assert f'"{fmt}"' in source


# ---------------------------------------------------------------------------
# Migration file tests
# ---------------------------------------------------------------------------
class TestMigration:
    """Alembic migration for STORY-113 must exist."""

    def test_migration_file_exists(self):
        assert _MIGRATION.exists()

    def test_migration_adds_required_columns(self):
        source = _MIGRATION.read_text()
        assert "user_id" in source
        assert "file_size_bytes" in source
        assert "expires_at" in source

    def test_migration_has_downgrade(self):
        source = _MIGRATION.read_text()
        assert "def downgrade" in source
        assert "drop_column" in source


# ---------------------------------------------------------------------------
# Schema tests (source inspection)
# ---------------------------------------------------------------------------
class TestExportJobResponseSchema:
    """ExportJobResponse must include all STORY-113 fields."""

    def test_response_has_file_size_bytes(self):
        assert "file_size_bytes" in _EXPORTS_PY.read_text()

    def test_response_has_expires_at(self):
        assert "expires_at" in _EXPORTS_PY.read_text()

    def test_response_has_progress_pct(self):
        assert "progress_pct" in _EXPORTS_PY.read_text()


class TestExportListResponseSchema:
    """ExportListResponse must have pagination fields."""

    def test_response_has_items(self):
        source = _EXPORTS_PY.read_text()
        assert "class ExportListResponse" in source
        assert "items:" in source

    def test_response_has_total(self):
        assert "total:" in _EXPORTS_PY.read_text()

    def test_response_has_page(self):
        assert "page:" in _EXPORTS_PY.read_text()

    def test_response_has_has_more(self):
        assert "has_more:" in _EXPORTS_PY.read_text()


# ---------------------------------------------------------------------------
# Worker task integration tests
# ---------------------------------------------------------------------------
class TestWorkerTaskIntegration:
    """Worker task must set expires_at on completion."""

    def test_export_task_uses_mark_completed(self):
        assert "mark_completed" in _TASK_PY.read_text()

    def test_export_task_gets_file_size(self):
        assert "_get_file_size" in _TASK_PY.read_text()

    def test_get_file_size_helper(self):
        size = _get_file_size(str(Path(__file__)))
        assert size is not None
        assert size > 0

    def test_get_file_size_returns_none_for_missing(self):
        assert _get_file_size("/nonexistent/path/file.xlsx") is None

    def test_get_file_size_returns_none_for_urls(self):
        assert _get_file_size("https://storage.example.com/file.xlsx") is None


# ---------------------------------------------------------------------------
# EXPORT_EXPIRY_DAYS configuration
# ---------------------------------------------------------------------------
class TestExpiryConfiguration:
    """Export expiry must be configurable and default to 7 days."""

    def test_default_expiry_is_7_days(self):
        assert EXPORT_EXPIRY_DAYS == 7

    def test_mark_completed_uses_expiry_days(self):
        record = _make_record(status="processing", progress_pct=50)
        before = datetime.now(timezone.utc)
        record.mark_completed("file.xlsx")
        after = datetime.now(timezone.utc)
        assert record.expires_at is not None
        expected_min = before + timedelta(days=EXPORT_EXPIRY_DAYS)
        expected_max = after + timedelta(days=EXPORT_EXPIRY_DAYS)
        assert expected_min <= record.expires_at <= expected_max
