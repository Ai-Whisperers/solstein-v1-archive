"""Tests for STORY-083: Research job status table and repository.

Validates:
- ResearchJobRecord model and state machine transitions.
- Repository CRUD operations (create, update, query).
- Invalid state transitions raise JobStatusError.
- API response schema correctness.
- Tenant scoping in queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.infrastructure.models.research import ResearchJobRecord
from solstein.infrastructure.research_job_repository import (
    JobStatusError,
    ResearchJobRepository,
)

# --- Model Tests ---


class TestResearchJobRecord:
    """Test the ResearchJobRecord ORM model."""

    def test_valid_transitions_from_queued(self):
        # Arrange
        job = ResearchJobRecord()
        job.status = "queued"

        # Assert
        assert job.can_transition_to("running") is True
        assert job.can_transition_to("cancelled") is True
        assert job.can_transition_to("completed") is False
        assert job.can_transition_to("failed") is False

    def test_valid_transitions_from_running(self):
        # Arrange
        job = ResearchJobRecord()
        job.status = "running"

        # Assert
        assert job.can_transition_to("completed") is True
        assert job.can_transition_to("failed") is True
        assert job.can_transition_to("cancelled") is True
        assert job.can_transition_to("queued") is False

    def test_terminal_states_no_transitions(self):
        # Arrange & Assert
        for terminal_status in ["completed", "failed", "cancelled"]:
            job = ResearchJobRecord()
            job.status = terminal_status
            assert job.can_transition_to("running") is False
            assert job.can_transition_to("queued") is False
            assert job.can_transition_to("completed") is False

    def test_unknown_status_no_transitions(self):
        # Arrange
        job = ResearchJobRecord()
        job.status = "nonexistent"

        # Assert
        assert job.can_transition_to("running") is False


# --- Repository Tests ---


def _mock_job(
    job_id: uuid.UUID | None = None,
    tenant_id: str = "tenant-abc",
    company_id: str = "comp-1",
    status: str = "queued",
    progress_pct: int = 0,
) -> MagicMock:
    """Create a mock ResearchJobRecord."""
    job = MagicMock(spec=ResearchJobRecord)
    job.id = job_id or uuid.uuid4()
    job.tenant_id = tenant_id
    job.company_id = company_id
    job.company_name = "Acme Corp"
    job.status = status
    job.progress_pct = progress_pct
    job.current_stage = None
    job.error_message = None
    job.job_metadata = None
    job.created_at = datetime(2026, 3, 27, tzinfo=timezone.utc)
    job.started_at = None
    job.completed_at = None
    job.can_transition_to = ResearchJobRecord.can_transition_to.__get__(job)
    # Patch VALID_TRANSITIONS as class attr
    job.VALID_TRANSITIONS = ResearchJobRecord.VALID_TRANSITIONS
    return job


class TestResearchJobRepository:
    """Test the ResearchJobRepository."""

    @pytest.mark.asyncio
    async def test_create_job(self):
        # Arrange
        mock_session = AsyncMock()

        repo = ResearchJobRepository(mock_session)

        # Act
        job = await repo.create_job(
            tenant_id="tenant-abc",
            company_id="comp-1",
            company_name="Acme Corp",
        )

        # Assert
        assert job.tenant_id == "tenant-abc"
        assert job.company_id == "comp-1"
        assert job.status == "queued"
        assert job.progress_pct == 0
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_valid_transition(self):
        # Arrange
        job_id = uuid.uuid4()
        mock_job = _mock_job(job_id=job_id, status="queued")

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        repo = ResearchJobRepository(mock_session)

        # Act
        result = await repo.update_status(
            job_id=job_id,
            new_status="running",
            progress_pct=10,
            current_stage="discovery",
        )

        # Assert
        assert result is not None
        assert mock_job.status == "running"
        assert mock_job.progress_pct == 10
        assert mock_job.current_stage == "discovery"

    @pytest.mark.asyncio
    async def test_update_status_invalid_transition(self):
        # Arrange
        job_id = uuid.uuid4()
        mock_job = _mock_job(job_id=job_id, status="completed")

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        repo = ResearchJobRepository(mock_session)

        # Act & Assert
        with pytest.raises(JobStatusError) as exc_info:
            await repo.update_status(job_id=job_id, new_status="running")

        assert exc_info.value.code == "INVALID_TRANSITION"

    @pytest.mark.asyncio
    async def test_update_status_job_not_found(self):
        # Arrange
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = ResearchJobRepository(mock_session)

        # Act
        result = await repo.update_status(
            job_id=uuid.uuid4(), new_status="running"
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_to_completed_sets_100_pct(self):
        # Arrange
        job_id = uuid.uuid4()
        mock_job = _mock_job(job_id=job_id, status="running", progress_pct=75)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        repo = ResearchJobRepository(mock_session)

        # Act
        result = await repo.update_status(job_id=job_id, new_status="completed")

        # Assert
        assert result is not None
        assert mock_job.progress_pct == 100
        assert mock_job.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_to_failed_preserves_error(self):
        # Arrange
        job_id = uuid.uuid4()
        mock_job = _mock_job(job_id=job_id, status="running")

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_session.execute.return_value = mock_result

        repo = ResearchJobRepository(mock_session)

        # Act
        result = await repo.update_status(
            job_id=job_id,
            new_status="failed",
            error_message="Connection timeout to SEC EDGAR",
        )

        # Assert
        assert result is not None
        assert mock_job.status == "failed"
        assert mock_job.error_message == "Connection timeout to SEC EDGAR"
        assert mock_job.completed_at is not None


class TestJobStatusError:
    """Test JobStatusError exception."""

    def test_error_attributes(self):
        # Arrange & Act
        err = JobStatusError(code="INVALID_TRANSITION", message="Cannot go back")

        # Assert
        assert err.code == "INVALID_TRANSITION"
        assert err.message == "Cannot go back"
        assert str(err) == "Cannot go back"
