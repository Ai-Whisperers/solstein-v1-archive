"""Research pipeline database models.

Contains ORM models for:
- Research runs and stages
- Artifacts and sources
- Metric observations
- Evidence readiness
- Contradictions
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    pass


class ResearchRunRecord(Base):
    """Top-level research run metadata."""

    __tablename__ = "research_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    market: Mapped[str] = mapped_column(String(255), nullable=False)
    seed_company: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")

    strict_provenance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    min_readiness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_contradictions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_total_sources: Mapped[int | None] = mapped_column(Integer, nullable=True)

    summary: Mapped[object | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    stages: Mapped[list["ResearchStageRecord"]] = relationship(
        "ResearchStageRecord", back_populates="run", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["ResearchArtifactRecord"]] = relationship(
        "ResearchArtifactRecord", back_populates="run", cascade="all, delete-orphan"
    )
    sources: Mapped[list["SourceDocumentRecord"]] = relationship(
        "SourceDocumentRecord", back_populates="run", cascade="all, delete-orphan"
    )


class ResearchStageRecord(Base):
    """Per-stage execution tracking."""

    __tablename__ = "research_stages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metrics: Mapped[object | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    run: Mapped["ResearchRunRecord"] = relationship("ResearchRunRecord", back_populates="stages")

    __table_args__ = (
        UniqueConstraint("run_id", "stage_name", name="uq_research_stage_run_name"),
        Index("ix_research_stage_run_order", "run_id", "stage_order"),
    )


class ResearchArtifactRecord(Base):
    """Artifacts produced by research runs."""

    __tablename__ = "research_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    artifact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    payload: Mapped[object | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    run: Mapped["ResearchRunRecord"] = relationship("ResearchRunRecord", back_populates="artifacts")

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "artifact_name",
            name="uq_research_artifact_run_name",
        ),
    )


class SourceDocumentRecord(Base):
    """Source URLs observed per company."""

    __tablename__ = "source_documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    source_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="observed")
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    extract_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    run: Mapped["ResearchRunRecord"] = relationship("ResearchRunRecord", back_populates="sources")

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "company_id",
            "source_url",
            name="uq_source_document_run_company_url",
        ),
    )


class MetricObservationRecord(Base):
    """Individual metric values from sources."""

    __tablename__ = "metric_observations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    metric_value_raw: Mapped[object | None] = mapped_column(JSON, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "company_id",
            "metric_key",
            "source_url",
            "metric_value",
            name="uq_metric_observation_run_company_metric_source_value",
        ),
        Index(
            "ix_metric_observation_company_metric",
            "company_id",
            "metric_key",
        ),
    )


class EvidenceReadinessRecord(Base):
    """Evidence quality scores."""

    __tablename__ = "evidence_readiness"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(500), nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_level: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    source_domain_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metric_source_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metric_explainability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unsupported_metrics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "company_id",
            name="uq_evidence_readiness_run_company",
        ),
    )


class ContradictionRecord(Base):
    """Detected data conflicts."""

    __tablename__ = "research_contradictions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_runs.id"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contradiction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[object | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ignored_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    transitions: Mapped[list["ContradictionTransitionRecord"]] = relationship(
        "ContradictionTransitionRecord",
        back_populates="contradiction",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "company_id",
            "metric_key",
            "contradiction_type",
            name="uq_contradiction_run_company_metric_type",
        ),
    )


class ContradictionTransitionRecord(Base):
    """Contradiction status history."""

    __tablename__ = "research_contradiction_transitions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contradiction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_contradictions.id"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str] = mapped_column(String(50), nullable=False)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    changed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    contradiction: Mapped["ContradictionRecord"] = relationship("ContradictionRecord", back_populates="transitions")
