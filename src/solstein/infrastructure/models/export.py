"""Export job database model.

STORY-111: Async export pipeline — tracks export job lifecycle from
queued through processing to completed/failed.

This table is the single source of truth for export job status. The API
creates a row with status='queued', the Celery task updates it to
'processing' then 'completed' or 'failed', and the GET endpoint reads it.

The table is append-friendly: rows are never deleted by application code.
Cleanup should be handled by a scheduled retention job.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExportJobRecord(Base):
    """Tracks async export jobs through their lifecycle.

    Status transitions: queued -> processing -> completed | failed
    """

    __tablename__ = "export_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True,
    )
    company_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )
    format: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
        index=True,
    )
    file_url: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    __table_args__ = (
        Index("ix_export_jobs_tenant_created", "tenant_id", "created_at"),
        Index("ix_export_jobs_status_created", "status", "created_at"),
    )

    def to_dict(self) -> dict[str, str | int | None]:
        """Serialize to dictionary for API responses."""
        return {
            "job_id": str(self.id),
            "tenant_id": self.tenant_id,
            "company_id": self.company_id,
            "format": self.format,
            "status": self.status,
            "file_url": self.file_url,
            "error_message": self.error_message,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
        }
