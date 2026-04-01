"""Repository for research job status operations (STORY-083, EPIC-024).

Provides async methods for creating, updating, and querying research job
status records. Designed to work with Supabase Realtime — every row update
triggers a broadcast to subscribed clients.

Status state machine:
    queued -> running -> completed | failed | cancelled
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.research import ResearchJobRecord


class JobStatusError(Exception):
    """Raised when a job status operation fails.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable description.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class ResearchJobRepository:
    """Repository for research job status CRUD operations.

    Each method flushes changes so Supabase Realtime picks up the
    row change immediately via WAL replication.
    """

    def __init__(self, session: AsyncSession):
        """Initialize repository with async database session.

        Args:
            session: AsyncSession instance for database operations.
        """
        self.session = session

    async def create_job(
        self,
        tenant_id: str,
        company_id: str,
        company_name: str | None = None,
    ) -> ResearchJobRecord:
        """Create a new research job record with status 'queued'.

        Args:
            tenant_id: Owning tenant ID.
            company_id: Target company ID.
            company_name: Optional cached company name.

        Returns:
            The created ResearchJobRecord.
        """
        job = ResearchJobRecord(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            company_id=company_id,
            company_name=company_name,
            status="queued",
            progress_pct=0,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(job)
        await self.session.flush()
        logger.info(
            f"[ResearchJob] Created job {job.id} for company {company_id} "
            f"(tenant={tenant_id[:8]}...)"
        )
        return job

    async def update_status(
        self,
        job_id: uuid.UUID,
        new_status: str,
        progress_pct: int | None = None,
        current_stage: str | None = None,
        error_message: str | None = None,
    ) -> ResearchJobRecord | None:
        """Update a job's status with state machine validation.

        Args:
            job_id: The job's UUID.
            new_status: Target status (queued/running/completed/failed/cancelled).
            progress_pct: Updated progress percentage (0-100).
            current_stage: Name of the current pipeline stage.
            error_message: Error details (for failed status).

        Returns:
            The updated record, or None if job not found.

        Raises:
            JobStatusError: If the transition is invalid.
        """
        result = await self.session.execute(
            select(ResearchJobRecord).where(ResearchJobRecord.id == job_id)
        )
        job = result.scalar_one_or_none()

        if job is None:
            logger.warning(f"[ResearchJob] Job {job_id} not found for status update")
            return None

        if not job.can_transition_to(new_status):
            raise JobStatusError(
                code="INVALID_TRANSITION",
                message=(
                    f"Cannot transition job {job_id} from '{job.status}' to "
                    f"'{new_status}'. Valid transitions: "
                    f"{job.VALID_TRANSITIONS.get(job.status, set())}"
                ),
            )

        now = datetime.now(timezone.utc)
        job.status = new_status

        if progress_pct is not None:
            job.progress_pct = max(0, min(100, progress_pct))
        if current_stage is not None:
            job.current_stage = current_stage
        if error_message is not None:
            job.error_message = error_message

        # Set timestamps based on status
        if new_status == "running" and job.started_at is None:
            job.started_at = now
        if new_status in ("completed", "failed", "cancelled"):
            job.completed_at = now
            if new_status == "completed":
                job.progress_pct = 100

        self.session.add(job)
        await self.session.flush()

        logger.info(
            f"[ResearchJob] Job {job_id} -> {new_status} "
            f"(progress={job.progress_pct}%, stage={current_stage})"
        )
        return job

    async def get_job(self, job_id: uuid.UUID) -> ResearchJobRecord | None:
        """Retrieve a single job by ID.

        Args:
            job_id: The job's UUID.

        Returns:
            ResearchJobRecord or None if not found.
        """
        result = await self.session.execute(
            select(ResearchJobRecord).where(ResearchJobRecord.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_jobs_for_tenant(
        self,
        tenant_id: str,
        status_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResearchJobRecord]:
        """List jobs for a tenant with optional status filtering.

        Args:
            tenant_id: The tenant's ID.
            status_filter: Optional status to filter by.
            limit: Maximum results per page.
            offset: Pagination offset.

        Returns:
            List of ResearchJobRecord instances.
        """
        query = (
            select(ResearchJobRecord)
            .where(ResearchJobRecord.tenant_id == tenant_id)
            .order_by(ResearchJobRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if status_filter is not None:
            query = query.where(ResearchJobRecord.status == status_filter)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_jobs_for_company(
        self,
        company_id: str,
        tenant_id: str,
    ) -> list[ResearchJobRecord]:
        """Get active (queued/running) jobs for a specific company.

        Args:
            company_id: The company's ID.
            tenant_id: The tenant's ID.

        Returns:
            List of active job records.
        """
        result = await self.session.execute(
            select(ResearchJobRecord)
            .where(
                ResearchJobRecord.company_id == company_id,
                ResearchJobRecord.tenant_id == tenant_id,
                ResearchJobRecord.status.in_(["queued", "running"]),
            )
            .order_by(ResearchJobRecord.created_at.desc())
        )
        return list(result.scalars().all())
