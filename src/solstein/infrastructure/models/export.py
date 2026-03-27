"""Export job database model.

STORY-111: Async export pipeline — tracks export job lifecycle from
queued through processing to completed/failed.

STORY-112: Added progress_pct field for streaming export progress tracking.

STORY-113: Added user_id, file_size_bytes, expires_at fields for status
tracking and download link management. Added expiry and cancellation logic.

This table is the single source of truth for export job status. The API
creates a row with status='queued', the Celery task updates it to
'processing' then 'completed' or 'failed', and the GET endpoint reads it.

The table is append-friendly: rows are never deleted by application code.
Cleanup should be handled by a scheduled retention job.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import BigInteger, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# Default expiry for completed exports (7 days)
EXPORT_EXPIRY_DAYS = 7


class ExportJobRecord(Base):
    """Tracks async export jobs through their lifecycle.

    Status transitions:
        queued -> processing -> completed | failed
        queued -> cancelled  (user-initiated via DELETE)
        completed -> expired (when expires_at < now)
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
    user_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True,
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
    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    progress_pct: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
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
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    __table_args__ = (
        Index("ix_export_jobs_tenant_created", "tenant_id", "created_at"),
        Index("ix_export_jobs_status_created", "status", "created_at"),
        Index("ix_export_jobs_expires_at", "expires_at"),
    )

    @property
    def is_expired(self) -> bool:
        """Check if a completed export has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def mark_completed(self, file_url: str, file_size_bytes: int | None = None) -> None:
        """Mark the job as completed with download URL and expiry."""
        self.status = "completed"
        self.file_url = file_url
        self.file_size_bytes = file_size_bytes
        self.progress_pct = 100
        self.completed_at = datetime.now(timezone.utc)
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=EXPORT_EXPIRY_DAYS)

    def mark_cancelled(self) -> None:
        """Mark the job as cancelled (user-initiated)."""
        self.status = "cancelled"
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self, *, check_expiry: bool = True) -> dict[str, str | int | None]:
        """Serialize to dictionary for API responses.

        When check_expiry is True (default), completed exports past their
        expires_at will have status='expired' and file_url=None.
        """
        status = self.status
        file_url = self.file_url

        if check_expiry and status == "completed" and self.is_expired:
            status = "expired"
            file_url = None

        return {
            "job_id": str(self.id),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "format": self.format,
            "status": status,
            "file_url": file_url,
            "file_size_bytes": self.file_size_bytes,
            "error_message": self.error_message,
            "progress_pct": self.progress_pct,
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
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at
                else None
            ),
        }
