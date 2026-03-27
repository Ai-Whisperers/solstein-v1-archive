"""Enrichment database models.

Contains ORM models for:
- Enrichment audit trail
- Enrichment cache
- Enrichment jobs
- Release gate audit
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import cast

from sqlalchemy import JSON, Column, DateTime, Float, Index, Integer, String, Text

from .base import Base


class EnrichmentAuditRecord(Base):
    """Stores audit trail for enrichment operations (Phase 11).

    Tracks all enrichment requests, successes, failures, and cache hits.
    """

    __tablename__ = "enrichment_audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=True)  # EPIC-019
    company_id = Column(String(255), index=True, nullable=False)
    company_name = Column(String(500), nullable=True)

    # Operation details
    operation = Column(
        String(50), nullable=False, index=True
    )  # 'enrich_start', 'enrich_success', 'enrich_failure', 'cache_hit', 'cache_miss'
    source = Column(String(255), nullable=True)  # 'SEC_EDGAR', 'Companies_House', 'News_Signals'
    status = Column(String(50), nullable=False)  # 'SUCCESS', 'FAILURE', 'SKIPPED'

    # Performance tracking
    duration_ms = Column(Float, nullable=True)

    # Results
    fields_enriched = Column(JSON, nullable=True)  # List of fields that were enriched
    error_message = Column(Text, nullable=True)

    # User/API context
    user_id = Column(String(255), nullable=True)
    client_id = Column(String(255), nullable=True)

    # Metadata
    timestamp = Column(DateTime, nullable=False, index=True, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_enrichment_audit_company_timestamp", "company_id", "timestamp"),
        Index("ix_enrichment_audit_operation", "operation", "timestamp"),
    )

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "operation": self.operation,
            "source": self.source,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "fields_enriched": self.fields_enriched,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "timestamp": (self.timestamp.isoformat() if self.timestamp is not None else None),
        }


class EnrichmentCacheRecord(Base):
    """Stores enriched company data cache (Phase 11).

    Caches enrichment results with TTL for performance.
    """

    __tablename__ = "enrichment_cache"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(255), index=True, nullable=True)  # EPIC-019
    company_id = Column(String(255), unique=True, index=True, nullable=False)

    # Cached enrichment data
    enriched_data = Column(JSON, nullable=False)  # Full UnifiedCompany serialized as JSON
    sources_used = Column(JSON, nullable=True)  # List of sources used for enrichment
    fields_enriched = Column(JSON, nullable=True)  # List of fields that were enriched

    # Cache metadata
    cached_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    ttl_seconds = Column(Integer, default=86400)  # 24 hours default
    expires_at = Column(DateTime, nullable=False, index=True)

    # Hit tracking
    hits = Column(Integer, default=0)  # Number of cache hits
    last_accessed_at = Column(DateTime, nullable=True)

    __table_args__ = (Index("ix_enrichment_cache_expires", "expires_at"),)

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        expires_at = cast(datetime | None, cast(object, self.expires_at))
        if expires_at is None:
            return False
        comparison = datetime.now(timezone.utc) > expires_at
        return cast(bool, comparison)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "enriched_data": self.enriched_data,
            "sources_used": self.sources_used,
            "fields_enriched": self.fields_enriched,
            "cached_at": (self.cached_at.isoformat() if self.cached_at is not None else None),
            "expires_at": (self.expires_at.isoformat() if self.expires_at is not None else None),
            "hits": self.hits,
            "last_accessed_at": (self.last_accessed_at.isoformat() if self.last_accessed_at is not None else None),
            "is_expired": self.is_expired(),
        }


class EnrichmentJobRecord(Base):
    """Stores async enrichment job tracking (Phase 12).

    Tracks the status and results of async enrichment tasks.
    """

    __tablename__ = "enrichment_jobs"

    id = Column(String(255), primary_key=True, index=True)  # Celery task_id
    tenant_id = Column(String(255), index=True, nullable=True)  # EPIC-019

    # Job details
    company_id = Column(String(255), index=True, nullable=False)
    company_name = Column(String(500), nullable=True)
    job_type = Column(String(50), nullable=False)  # 'single', 'batch'

    # Status tracking
    status = Column(String(50), nullable=False, index=True)  # 'PENDING', 'RUNNING', 'SUCCESS', 'FAILED'
    progress = Column(Integer, default=0)  # 0-100 for batch jobs

    # Job parameters
    sources = Column(JSON, nullable=True)
    batch_size = Column(Integer, nullable=True)

    # Results
    result_data = Column(JSON, nullable=True)  # Full result
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)

    # User context
    user_id = Column(String(255), nullable=True)

    __table_args__ = (
        Index("ix_enrichment_job_status_created", "status", "created_at"),
        Index("ix_enrichment_job_company_created", "company_id", "created_at"),
    )

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "job_type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "sources": self.sources,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "created_at": (self.created_at.isoformat() if self.created_at is not None else None),
            "started_at": (self.started_at.isoformat() if self.started_at is not None else None),
            "completed_at": (self.completed_at.isoformat() if self.completed_at is not None else None),
            "duration_ms": self.duration_ms,
            "user_id": self.user_id,
        }


class ReleaseGateAuditRecord(Base):
    """Release gate audit record."""

    __tablename__ = "release_gate_audit"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    company_ids = Column(JSON, nullable=False)
    company_names = Column(JSON, nullable=False)
    reason_codes = Column(JSON, nullable=False)
    reason_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (Index("ix_release_gate_operation_status", "operation", "status"),)
