"""Infrastructure database models.

Contains ORM models for:
- Transactional outbox
- Tenant management
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    pass


class OutboxRecord(Base):
    """Transactional outbox for event reliability."""

    __tablename__ = "outbox_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    payload: Mapped[object] = mapped_column(JSON, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_error: Mapped[object | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (Index("ix_outbox_status_available_at", "status", "available_at"),)


class TenantRecord(Base):
    """ORM model for API tenants.

    Each tenant has a unique API key (stored as SHA-256 hash) and owns
    its own set of enrichment jobs and analysis results.
    """

    __tablename__ = "tenants"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    api_key_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 hex
    is_active = Column(Boolean, nullable=False, default=True)
    plan = Column(String(64), nullable=False, default="standard")  # free|standard|enterprise
    rate_limit_per_min = Column(Integer, nullable=False, default=60)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_tenants_api_key_hash", "api_key_hash"),
        Index("ix_tenants_is_active", "is_active"),
    )

    def to_dict(self) -> dict[str, object]:
        from typing import Optional, cast

        created_at = cast(Optional[datetime], cast(object, self.created_at))
        created_at_value = created_at.isoformat() if created_at is not None else None
        return {
            "id": str(self.id),
            "name": self.name,
            "plan": self.plan,
            "is_active": self.is_active,
            "rate_limit_per_min": self.rate_limit_per_min,
            "created_at": created_at_value,
        }
