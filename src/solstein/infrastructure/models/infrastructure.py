"""Infrastructure database models.

Contains ORM models for:
- Transactional outbox
- Tenant management
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


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
        from typing import cast

        created_at = cast(datetime | None, cast(object, self.created_at))
        created_at_value = created_at.isoformat() if created_at is not None else None
        return {
            "id": str(self.id),
            "name": self.name,
            "plan": self.plan,
            "is_active": self.is_active,
            "rate_limit_per_min": self.rate_limit_per_min,
            "created_at": created_at_value,
        }


class ApiKeyRecord(Base):
    """ORM model for tenant API keys (EPIC-019 STORY-065).

    Stores hashed API keys with scope and lifecycle state.
    The full plaintext key is never stored — only the SHA-256 hash.
    """

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
    )  # index covered by ix_api_keys_tenant_id in __table_args__
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    # ix_api_keys_key_hash index is declared in __table_args__ — do not add index=True here
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    scope: Mapped[str] = mapped_column(String(50), nullable=False, default="read_only")  # read_only|read_write|admin
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_api_keys_tenant_id", "tenant_id"),
        Index("ix_api_keys_key_hash", "key_hash"),
        Index("ix_api_keys_tenant_active", "tenant_id", "is_active"),
    )

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary (never exposes key_hash)."""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "key_prefix": self.key_prefix,
            "scope": self.scope,
            "is_active": self.is_active,
            "last_used_at": (self.last_used_at.isoformat() if self.last_used_at else None),
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "expires_at": (self.expires_at.isoformat() if self.expires_at else None),
            "revoked_at": (self.revoked_at.isoformat() if self.revoked_at else None),
        }


class ApiKeyUsageRecord(Base):
    """ORM model for API key usage logging (EPIC-019 STORY-065 REQ-5).

    Logs every authenticated API request for audit purposes.
    """

    __tablename__ = "api_key_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("api_keys.id"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    __table_args__ = (
        Index("ix_api_key_usage_key_timestamp", "api_key_id", "timestamp"),
        Index("ix_api_key_usage_tenant_timestamp", "tenant_id", "timestamp"),
    )
