"""Data access audit trail models.

STORY-086: Universal audit trail for all authenticated data access.
Records who accessed what, when, and the response status.

The audit table is append-only by design: application code must never
DELETE or UPDATE rows. Retention cleanup should use a scheduled admin
procedure with explicit authorization.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from .base import Base


class DataAccessAuditRecord(Base):
    """Append-only audit record for authenticated data access.

    Every authenticated request to a data-returning endpoint generates
    one row in this table via the audit middleware.
    """

    __tablename__ = "data_access_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Who
    tenant_id = Column(String(255), nullable=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)

    # What
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500), nullable=False)
    resource_id = Column(String(255), nullable=True)

    # When
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc),
    )

    # Outcome
    status_code = Column(Integer, nullable=False)

    # Context
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_data_access_audit_tenant_ts", "tenant_id", "timestamp"),
        Index("ix_data_access_audit_user_ts", "user_id", "timestamp"),
        Index("ix_data_access_audit_endpoint_ts", "endpoint", "timestamp"),
    )

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "method": self.method,
            "endpoint": self.endpoint,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status_code": self.status_code,
            "client_ip": self.client_ip,
        }
