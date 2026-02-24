"""SQLAlchemy ORM models for facts storage and audit trail.

This module defines the data models for storing company facts with confidence
scoring and source tracking. All models use UUID primary keys and reference
the companies table via company_id (string).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from solstein.infrastructure.database import Base


class GatheringBatch(Base):
    """Tracks a batch of facts gathered for a company at a specific time.

    Each gathering operation (e.g., "fetch SEC EDGAR data for company X")
    creates a batch record. This allows auditing which facts were gathered
    together and when.
    """

    __tablename__ = "gathering_batches"

    batch_id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, nullable=False)
    company_id: Mapped[str] = mapped_column(String(255), ForeignKey("companies.company_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    status: Mapped[str] = mapped_column(
        String(50), default="in_progress", nullable=False
    )  # in_progress, completed, failed

    # Relationships
    facts: Mapped[list["Fact"]] = relationship("Fact", back_populates="batch", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<GatheringBatch(batch_id={self.batch_id}, company_id={self.company_id}, status={self.status})>"


class Fact(Base):
    """Immutable fact record with confidence scoring and source tracking.

    Each fact represents a single piece of information about a company
    (e.g., "annual revenue is $10M", "series B funding round"). Facts are
    immutable and include confidence scores to distinguish authoritative
    data (SEC filings, 0.95) from rumors (news, 0.60).
    """

    __tablename__ = "facts"

    fact_id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, nullable=False)
    company_id: Mapped[str] = mapped_column(String(255), ForeignKey("companies.company_id"), nullable=False, index=True)
    batch_id: Mapped[str] = mapped_column(Uuid, ForeignKey("gathering_batches.batch_id"), nullable=False, index=True)
    fact_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "annual_revenue", "series_b_funding"
    value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    value_str: Mapped[str | None] = mapped_column(String(500), nullable=True)
    value_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), default=0.5, nullable=False)  # 0.0 - 1.0
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    batch: Mapped["GatheringBatch"] = relationship("GatheringBatch", back_populates="facts")
    sources: Mapped[list["FactSource"]] = relationship(
        "FactSource", back_populates="fact", cascade="all, delete-orphan"
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_company_fact_type", "company_id", "fact_type"),
        Index("idx_company_extracted", "company_id", "extracted_at"),
    )

    def validate(self) -> None:
        """Validate fact constraints.

        Raises:
            ValueError: If confidence is outside 0.0-1.0 range or required fields are missing.
        """
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.fact_type:
            raise ValueError("Fact type is required")
        if not self.company_id:
            raise ValueError("Company ID is required")
        if not self.batch_id:
            raise ValueError("Batch ID is required")

    def __repr__(self) -> str:
        return f"<Fact(fact_id={self.fact_id}, fact_type={self.fact_type}, confidence={self.confidence})>"


class FactSource(Base):
    """Audit trail: tracks the source of each fact.

    Each fact can have multiple sources (e.g., same revenue figure from
    SEC filing and Companies House). This table stores the source metadata
    for full auditability.
    """

    __tablename__ = "fact_sources"

    source_id: Mapped[str] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, nullable=False)
    fact_id: Mapped[str] = mapped_column(Uuid, ForeignKey("facts.fact_id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "sec_edgar", "companies_house", "newsapi", "github"
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    extraction_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)  # Store original API response for audit trail

    # Relationships
    fact: Mapped["Fact"] = relationship("Fact", back_populates="sources")

    def __repr__(self) -> str:
        return f"<FactSource(source_id={self.source_id}, source_type={self.source_type})>"



class RefreshMetadata(Base):
    """Tracks refresh scheduling and status for each data source.

    This table stores metadata about when each source was last refreshed,
    when the next refresh is scheduled, and the current status of the
    refresh process. Used by Celery Beat for scheduling and by the
    API for status checks.
    """

    __tablename__ = "refresh_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # sec_edgar, companies_house, newsapi, github
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # financial, regulatory, news, github
    last_refresh_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_refresh_status: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # success, failed, partial
    last_refresh_job_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    next_scheduled_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True
    )
    refresh_interval_seconds: Mapped[int] = mapped_column(
        nullable=False, default=86400
    )  # default: 24 hours
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC),
        nullable=False,
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<RefreshMetadata(source={self.source_name}, last_refresh={self.last_refresh_time})>"


class DataSourceConflict(Base):
    """Records contradictions between data sources for manual review.

    When two or more sources provide conflicting values for the same
    metric, this table records the conflict for resolution. Supports
    three resolution strategies:
    - highest_confidence: Use the value from the source with highest confidence
    - weighted_average: Blend values weighted by confidence scores
    - flagged_for_review: Mark for analyst review
    """

    __tablename__ = "data_source_conflicts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("companies.company_id"), nullable=False, index=True
    )
    metric_key: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "annual_revenue", "employee_count"
    period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Source 1 (the higher confidence source)
    source1_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source1_value: Mapped[Optional[float]] = mapped_column(Numeric(20, 4), nullable=True)
    source1_confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    source1_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Source 2 (the lower confidence source)
    source2_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source2_value: Mapped[Optional[float]] = mapped_column(Numeric(20, 4), nullable=True)
    source2_confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    source2_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Resolution
    contradiction_detected: Mapped[bool] = mapped_column(nullable=False, default=True)
    resolution_strategy: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # highest_confidence, weighted_average, flagged_for_review, manual
    chosen_value: Mapped[Optional[float]] = mapped_column(Numeric(20, 4), nullable=True)
    chosen_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    flagged_for_review: Mapped[bool] = mapped_column(nullable=False, default=False)
    analyst_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC),
        nullable=False,
        onupdate=lambda: datetime.now(UTC),
    )

    # Indexes
    __table_args__ = (
        Index("idx_conflict_company_metric", "company_id", "metric_key"),
        Index("idx_conflict_flagged", "flagged_for_review"),
    )

    def __repr__(self) -> str:
        return f"<DataSourceConflict(company={self.company_id}, metric={self.metric_key}, resolved={self.resolution_strategy})>"


class ConfidenceCalibration(Base):
    """Tracks accuracy of confidence scores for calibration.

    This table records predictions against actual observed values to
    calibrate confidence scores over time. After 10+ data points,
    we can calculate a calibration factor and adjust confidence scores
    to be more accurate.
    """

    __tablename__ = "confidence_calibration"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # sec_edgar, companies_house, etc.
    metric_key: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # annual_revenue, employee_count, etc.
    company_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )

    # Prediction (original confidence score)
    predicted_value: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 4), nullable=True
    )
    confidence_original: Mapped[float] = mapped_column(
        Numeric(3, 2), nullable=False
    )

    # Actual (observed value - may come later from another source)
    actual_value: Mapped[Optional[float]] = mapped_column(
        Numeric(20, 4), nullable=True
    )
    actual_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    actual_observed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    # Derived
    is_correct: Mapped[Optional[bool]] = mapped_column(nullable=True)  # null = unknown
    accuracy_tolerance_pct: Mapped[float] = mapped_column(
        nullable=False, default=10.0
    )  # 10% tolerance by default

    # Calibration factor (calculated after 10+ records)
    calibration_factor: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2), nullable=True
    )  # e.g., 0.95 means 95% accurate
    confidence_adjusted: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC),
        nullable=False,
        onupdate=lambda: datetime.now(UTC),
    )

    # Indexes
    __table_args__ = (
        Index("idx_calibration_source_metric", "source_name", "metric_key"),
        Index("idx_calibration_is_correct", "is_correct"),
    )

    def __repr__(self) -> str:
        return f"<ConfidenceCalibration(source={self.source_name}, factor={self.calibration_factor})>"
