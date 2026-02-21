"""Database models for persistence of scoring data and market intelligence.

SQLAlchemy ORM models for storing:
- Scoring results (growth, financial health, competitive position)
- Signal evidence (extracted data points that contributed to scores)
- Market snapshots (historical state of companies for trend analysis)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from .database import Base


class ScoringRecord(Base):
    """Stores the final scoring result for a company at a point in time."""

    __tablename__ = "scoring_records"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(255), index=True, nullable=False)
    company_name = Column(String(500), nullable=False)

    growth_score = Column(Float, nullable=False)
    financial_health_score = Column(Float, nullable=False)
    competitive_position_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)

    classification = Column(String(50), nullable=False)

    scored_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    data_sources_used = Column(JSON, nullable=True)

    signals = relationship(
        "SignalRecord", back_populates="scoring_record", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_company_scored_at", "company_id", "scored_at"),
        Index("ix_overall_score", "overall_score"),
        Index("ix_classification", "classification"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "growth_score": self.growth_score,
            "financial_health_score": self.financial_health_score,
            "competitive_position_score": self.competitive_position_score,
            "overall_score": self.overall_score,
            "classification": self.classification,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
            "data_sources_used": self.data_sources_used,
            "signals_count": len(self.signals) if self.signals else 0,
        }


class SignalRecord(Base):
    """Stores individual signals extracted from data sources.

    Each signal represents a data point that contributed to a score.
    """

    __tablename__ = "signal_records"

    id = Column(Integer, primary_key=True, index=True)
    scoring_record_id = Column(
        Integer, ForeignKey("scoring_records.id"), nullable=False, index=True
    )

    signal_name = Column(String(255), nullable=False, index=True)
    signal_category = Column(String(50), nullable=False)
    signal_value = Column(Float, nullable=True)
    signal_text = Column(String(2000), nullable=True)

    source_agent = Column(String(100), nullable=False)
    evidence = Column(JSON, nullable=True)

    confidence = Column(Float, nullable=False)

    extracted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    scoring_record = relationship("ScoringRecord", back_populates="signals")

    __table_args__ = (
        Index("ix_signal_name_category", "signal_name", "signal_category"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "signal_name": self.signal_name,
            "signal_category": self.signal_category,
            "signal_value": self.signal_value,
            "signal_text": self.signal_text,
            "source_agent": self.source_agent,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "extracted_at": self.extracted_at.isoformat()
            if self.extracted_at
            else None,
        }


class MarketSnapshot(Base):
    """Snapshot of market state at a point in time.

    Used for trend analysis and historical comparison.
    """

    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(
        DateTime, nullable=False, index=True, default=datetime.utcnow
    )

    total_companies_scored = Column(Integer, nullable=False)
    average_growth_score = Column(Float, nullable=False)
    average_financial_score = Column(Float, nullable=False)
    average_competitive_score = Column(Float, nullable=False)

    rocket_count = Column(Integer, nullable=False)
    neutral_count = Column(Integer, nullable=False)
    dinosaur_count = Column(Integer, nullable=False)

    market_metadata = Column(JSON, nullable=True)

    __table_args__ = (Index("ix_snapshot_date", "snapshot_date"),)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "snapshot_date": self.snapshot_date.isoformat()
            if self.snapshot_date
            else None,
            "total_companies_scored": self.total_companies_scored,
            "average_growth_score": self.average_growth_score,
            "average_financial_score": self.average_financial_score,
            "average_competitive_score": self.average_competitive_score,
            "rocket_count": self.rocket_count,
            "neutral_count": self.neutral_count,
            "dinosaur_count": self.dinosaur_count,
            "market_metadata": self.market_metadata,
        }
