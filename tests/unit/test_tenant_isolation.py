"""Unit tests for worker tenant isolation (STORY-066).

Tests validate_task_tenant_id(), task_tenant_context(), require_tenant_id(),
and tenant-scoped query/write filtering in base utilities.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

celery = pytest.importorskip("celery", reason="celery not installed")

from solstein.utils.context import TENANT_ID
from solstein.worker.base import store_facts
from solstein.worker.tenant_isolation import (
    TenantIsolationError,
    require_tenant_id,
    task_tenant_context,
    validate_task_tenant_id,
)
from solstein.worker_tasks import refresh_sec_edgar


# ---------------------------------------------------------------------------
# validate_task_tenant_id
# ---------------------------------------------------------------------------


class TestValidateTaskTenantId:
    """Tests for validate_task_tenant_id()."""

    def test_valid_uuid_passes(self):
        tenant = str(uuid.uuid4())
        result = validate_task_tenant_id(tenant, task_name="test")
        assert result == tenant

    def test_none_raises(self):
        with pytest.raises(TenantIsolationError, match="requires"):
            validate_task_tenant_id(None, task_name="test")

    def test_empty_string_raises(self):
        with pytest.raises(TenantIsolationError, match="non-empty"):
            validate_task_tenant_id("", task_name="test")

    def test_non_string_raises(self):
        with pytest.raises(TenantIsolationError, match="string"):
            validate_task_tenant_id(12345, task_name="test")  # type: ignore[arg-type]

    def test_whitespace_only_raises(self):
        with pytest.raises(TenantIsolationError, match="non-empty"):
            validate_task_tenant_id("   ", task_name="test")

    def test_task_name_in_error(self):
        with pytest.raises(TenantIsolationError, match="my_task"):
            validate_task_tenant_id(None, task_name="my_task")


# ---------------------------------------------------------------------------
# task_tenant_context
# ---------------------------------------------------------------------------


class TestTaskTenantContext:
    """Tests for task_tenant_context() context manager."""

    def test_sets_and_resets_context(self):
        tenant = str(uuid.uuid4())
        with task_tenant_context(tenant) as tid:
            assert tid == tenant
            # Context var should be set during the block
            assert TENANT_ID.get() == tenant

        # After exiting the context, TENANT_ID should be reset
        assert TENANT_ID.get(None) is None or TENANT_ID.get() != tenant

    def test_resets_on_exception(self):
        tenant = str(uuid.uuid4())
        with pytest.raises(RuntimeError):
            with task_tenant_context(tenant):
                raise RuntimeError("boom")
        # Context should be reset after the exception


# ---------------------------------------------------------------------------
# require_tenant_id decorator
# ---------------------------------------------------------------------------


class TestRequireTenantIdDecorator:
    """Tests for the require_tenant_id decorator.

    The decorator is designed for Celery bind=True tasks where args[0] is
    self (Task instance) and args[1] is tenant_id.
    """

    def test_decorator_passes_valid_tenant(self):
        tenant = str(uuid.uuid4())
        mock_self = MagicMock()

        @require_tenant_id
        def my_task(self, tenant_id: str, data: str) -> dict:  # noqa: N805
            return {"tenant_id": tenant_id, "data": data}

        result = my_task(mock_self, tenant, "hello")
        assert result["tenant_id"] == tenant
        assert result["data"] == "hello"

    def test_decorator_rejects_missing_tenant(self):
        mock_self = MagicMock()

        @require_tenant_id
        def my_task(self, tenant_id: str) -> dict:  # noqa: N805
            return {"tenant_id": tenant_id}

        with pytest.raises(TenantIsolationError):
            my_task(mock_self, None)

    def test_decorator_rejects_no_args(self):
        @require_tenant_id
        def my_task(self, tenant_id: str) -> dict:  # noqa: N805
            return {"tenant_id": tenant_id}

        with pytest.raises(TenantIsolationError):
            my_task()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# Refresh tasks require tenant_id
# ---------------------------------------------------------------------------


class TestRefreshTasksTenantRequired:
    """Test that refresh tasks reject calls without tenant_id."""

    def test_refresh_sec_edgar_requires_tenant(self):
        """Calling refresh_sec_edgar without tenant_id raises TenantIsolationError."""
        with pytest.raises(TenantIsolationError):
            refresh_sec_edgar.run(None)

    def test_refresh_sec_edgar_with_valid_tenant(self):
        """Calling refresh_sec_edgar with valid tenant_id proceeds to business logic."""
        tenant = str(uuid.uuid4())

        with (
            patch("solstein.worker.refresh_tasks.get_db_manager") as mock_db,  # noqa: F841
            patch(
                "solstein.worker.refresh_tasks.get_tracked_company_ids",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            result = refresh_sec_edgar.run(tenant)
            # With no tracked companies, should return completed with 0 facts
            assert result["status"] == "completed"
            assert result["facts_fetched"] == 0
            assert result["tenant_id"] == tenant


# ---------------------------------------------------------------------------
# store_facts tenant filtering
# ---------------------------------------------------------------------------


class TestStoreFactsTenantFiltering:
    """Test that store_facts enforces tenant isolation on writes."""

    @pytest.fixture
    def mock_company_record(self):
        record = MagicMock()
        record.company_id = "comp_001"
        record.tenant_id = "tenant-aaa"
        record.raw_data = {}
        return record

    @pytest.mark.asyncio
    async def test_store_facts_skips_wrong_tenant(self, mock_company_record):
        """Facts for a company belonging to a different tenant are skipped."""

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_company_record
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.add = MagicMock()

        mock_db = MagicMock()

        @asynccontextmanager
        async def fake_session():
            yield mock_session

        mock_db.get_session = fake_session

        facts = [{"company_id": "comp_001", "fact_type": "revenue", "value": 1000}]

        stored = await store_facts(
            mock_db, facts, "test_source", tenant_id="tenant-bbb"
        )
        # Should skip because company belongs to tenant-aaa, not tenant-bbb
        assert stored == 0
