"""SQLAlchemy ORM models for facts storage and audit trail.

This module defines the data models for storing company facts with confidence
scoring and source tracking. All models use UUID primary keys and reference
the companies table via company_id (string).
"""

import uuid
from datetime import UTC, datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
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

    batch_id: Mapped[str] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("companies.company_id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, onupdate=lambda: datetime.now(UTC)
    )
    status: Mapped[str] = mapped_column(
        String(50), default="in_progress", nullable=False
    )  # in_progress, completed, failed

    # Relationships
    facts: Mapped[List["Fact"]] = relationship(
        "Fact", back_populates="batch", cascade="all, delete-orphan"
    )

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

    fact_id: Mapped[str] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("companies.company_id"), nullable=False, index=True
    )
    batch_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("gathering_batches.batch_id"), nullable=False, index=True
    )
    fact_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "annual_revenue", "series_b_funding"
    value: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)
    value_str: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    value_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    confidence: Mapped[float] = mapped_column(
        Numeric(3, 2), default=0.5, nullable=False
    )  # 0.0 - 1.0
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, onupdate=lambda: datetime.now(UTC)
    )

    # Relationships
    batch: Mapped["GatheringBatch"] = relationship(
        "GatheringBatch", back_populates="facts"
    )
    sources: Mapped[List["FactSource"]] = relationship(
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
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
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

    source_id: Mapped[str] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, nullable=False
    )
    fact_id: Mapped[str] = mapped_column(
        Uuid, ForeignKey("facts.fact_id"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "sec_edgar", "companies_house", "newsapi", "github"
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    extraction_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False, onupdate=lambda: datetime.now(UTC)
    )
    raw_content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Store original API response for audit trail

    # Relationships
    fact: Mapped["Fact"] = relationship("Fact", back_populates="sources")

    def __repr__(self) -> str:
        return f"<FactSource(source_id={self.source_id}, source_type={self.source_type})>"
