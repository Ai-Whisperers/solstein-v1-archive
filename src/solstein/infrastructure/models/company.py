"""Company and scoring database models.

Contains ORM models for:
- Company data storage
- Scoring records and signals
- Market snapshots
- Audit trails
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    pass


class CompanyRecord(Base):
    """Stores company data with financial metrics and AI scores."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(255), unique=True, index=True, nullable=False)
    tenant_id = Column(String(255), index=True, nullable=True)
    name = Column(String(500), nullable=False)
    industry = Column(String(255), nullable=True)
    description = Column(String(5000), nullable=True)
    website = Column(String(500), nullable=True)
    headquarters = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)

    # Classification
    tier = Column(String(50), nullable=True)
    threat_level = Column(String(50), nullable=True)
    classification = Column(String(50), nullable=True)
    ai_maturity = Column(String(50), nullable=True)
    saas_maturity = Column(String(50), nullable=True)

    # AI Scores
    ai_score = Column(Float, nullable=True)
    ai_signal_level = Column(String(50), nullable=True)
    ai_key_capabilities = Column(JSON, nullable=True)
    ai_in_production = Column(Integer, nullable=True)

    # Financial metrics
    revenue_eur_m = Column(Float, nullable=True)
    revenue_confidence = Column(String(50), nullable=True)
    growth_rate_pct = Column(Float, nullable=True)
    growth_confidence = Column(String(50), nullable=True)
    profit_margin_pct = Column(Float, nullable=True)
    ebitda_margin_pct = Column(Float, nullable=True)
    recurring_revenue_pct = Column(Float, nullable=True)
    revenue_per_employee_eur_k = Column(Float, nullable=True)
    revenue_timeline = Column(JSON, nullable=True)
    revenue_cagr_3yr = Column(Float, nullable=True)
    revenue_cagr_5yr = Column(Float, nullable=True)

    # Funding
    funding_rounds = Column(JSON, nullable=True)
    total_funding_raised_eur = Column(Float, nullable=True)
    latest_valuation_eur = Column(Float, nullable=True)
    lead_investors = Column(JSON, nullable=True)
    funding_war_chest = Column(Float, nullable=True)

    # Employees
    employee_count = Column(Integer, nullable=True)
    employee_cagr_3yr = Column(Float, nullable=True)
    open_positions = Column(Integer, nullable=True)

    # Data quality
    profitability_raw_metrics = Column(JSON, nullable=True)
    data_availability = Column(JSON, nullable=True)
    data_source = Column(String(100), nullable=True)

    # Scores
    growth_score = Column(Float, nullable=True)
    financial_health_score = Column(Float, nullable=True)
    competitive_position_score = Column(Float, nullable=True)
    composite_score = Column(Float, nullable=True)
    scoring_breakdown = Column(JSON, nullable=True)

    # Metadata
    last_updated = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_company_name", "name"),
        Index("ix_company_tenant", "tenant_id"),
        Index("ix_company_industry", "industry"),
        Index("ix_company_headquarters", "headquarters"),
        Index("ix_company_tier", "tier"),
        Index("ix_company_classification", "classification"),
        Index("ix_company_ai_score", "ai_score"),
        Index("ix_company_composite_score", "composite_score"),
        Index("ix_company_revenue_eur_m", "revenue_eur_m"),
        Index("ix_company_growth_rate", "growth_rate_pct"),
        Index("ix_company_last_updated", "last_updated"),
        Index("ix_company_industry_headquarters", "industry", "headquarters"),
        Index("ix_company_tenant_industry", "tenant_id", "industry"),
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.name,
            "tenant_id": self.tenant_id,
            "industry": self.industry,
            "description": self.description,
            "website": self.website,
            "headquarters": self.headquarters,
            "founded_year": self.founded_year,
            "tier": self.tier,
            "threat_level": self.threat_level,
            "classification": self.classification,
            "ai_maturity": self.ai_maturity,
            "saas_maturity": self.saas_maturity,
            "ai_score": self.ai_score,
            "ai_signal_level": self.ai_signal_level,
            "ai_key_capabilities": self.ai_key_capabilities,
            "ai_in_production": self.ai_in_production,
            "revenue_eur_m": self.revenue_eur_m,
            "revenue_confidence": self.revenue_confidence,
            "growth_rate_pct": self.growth_rate_pct,
            "growth_confidence": self.growth_confidence,
            "profit_margin_pct": self.profit_margin_pct,
            "ebitda_margin_pct": self.ebitda_margin_pct,
            "recurring_revenue_pct": self.recurring_revenue_pct,
            "revenue_per_employee_eur_k": self.revenue_per_employee_eur_k,
            "revenue_timeline": self.revenue_timeline,
            "revenue_cagr_3yr": self.revenue_cagr_3yr,
            "revenue_cagr_5yr": self.revenue_cagr_5yr,
            "funding_rounds": self.funding_rounds,
            "total_funding_raised_eur": self.total_funding_raised_eur,
            "latest_valuation_eur": self.latest_valuation_eur,
            "lead_investors": self.lead_investors,
            "funding_war_chest": self.funding_war_chest,
            "employee_count": self.employee_count,
            "employee_cagr_3yr": self.employee_cagr_3yr,
            "open_positions": self.open_positions,
            "profitability_raw_metrics": self.profitability_raw_metrics,
            "data_availability": self.data_availability,
            "data_source": self.data_source,
            "growth_score": self.growth_score,
            "financial_health_score": self.financial_health_score,
            "competitive_position_score": self.competitive_position_score,
            "composite_score": self.composite_score,
            "scoring_breakdown": self.scoring_breakdown,
            "last_updated": (self.last_updated.isoformat() if self.last_updated is not None else None),
            "created_at": (self.created_at.isoformat() if self.created_at is not None else None),
        }


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

    scored_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    data_sources_used = Column(JSON, nullable=True)

    signals = relationship("SignalRecord", back_populates="scoring_record", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_company_scored_at", "company_id", "scored_at"),
        Index("ix_overall_score", "overall_score"),
        Index("ix_classification", "classification"),
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "growth_score": self.growth_score,
            "financial_health_score": self.financial_health_score,
            "competitive_position_score": self.competitive_position_score,
            "overall_score": self.overall_score,
            "classification": self.classification,
            "scored_at": (self.scored_at.isoformat() if self.scored_at is not None else None),
            "data_sources_used": self.data_sources_used,
            "signals_count": len(self.signals) if self.signals else 0,
        }


class SignalRecord(Base):
    """Stores individual signals extracted from data sources."""

    __tablename__ = "signal_records"

    id = Column(Integer, primary_key=True, index=True)
    scoring_record_id = Column(Integer, ForeignKey("scoring_records.id"), nullable=False, index=True)

    signal_name = Column(String(255), nullable=False, index=True)
    signal_category = Column(String(50), nullable=False)
    signal_value = Column(Float, nullable=True)
    signal_text = Column(String(2000), nullable=True)

    source_agent = Column(String(100), nullable=False)
    evidence = Column(JSON, nullable=True)

    confidence = Column(Float, nullable=False)

    extracted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    scoring_record = relationship("ScoringRecord", back_populates="signals")

    __table_args__ = (Index("ix_signal_name_category", "signal_name", "signal_category"),)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "signal_name": self.signal_name,
            "signal_category": self.signal_category,
            "signal_value": self.signal_value,
            "signal_text": self.signal_text,
            "source_agent": self.source_agent,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "extracted_at": (self.extracted_at.isoformat() if self.extracted_at is not None else None),
        }


class MarketSnapshot(Base):
    """Snapshot of market state at a point in time."""

    __tablename__ = "market_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime, nullable=False, index=True, default=lambda: datetime.now(timezone.utc))

    total_companies_scored = Column(Integer, nullable=False)
    average_growth_score = Column(Float, nullable=False)
    average_financial_score = Column(Float, nullable=False)
    average_competitive_score = Column(Float, nullable=False)

    phoenix_count = Column(Integer, nullable=False)
    salt_count = Column(Integer, nullable=False)
    lead_count = Column(Integer, nullable=False)

    market_metadata = Column(JSON, nullable=True)

    __table_args__ = (Index("ix_snapshot_date", "snapshot_date"),)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "snapshot_date": (self.snapshot_date.isoformat() if self.snapshot_date is not None else None),
            "total_companies_scored": self.total_companies_scored,
            "average_growth_score": self.average_growth_score,
            "average_financial_score": self.average_financial_score,
            "average_competitive_score": self.average_competitive_score,
            "phoenix_count": self.phoenix_count,
            "salt_count": self.salt_count,
            "lead_count": self.lead_count,
            "market_metadata": self.market_metadata,
        }


class AuditTrailRecord(Base):
    """Stores the complete audit trail for a company analysis."""

    __tablename__ = "audit_trails"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(255), index=True, nullable=False)
    gathering_batch_id = Column(String(255), index=True, nullable=False)
    company_name = Column(String(500), nullable=False)

    raw_data = Column(JSON, nullable=True)
    aggregated_facts = Column(JSON, nullable=True)
    extracted_signals = Column(JSON, nullable=True)

    growth_score = Column(Float, nullable=True)
    financial_health_score = Column(Float, nullable=True)
    competitive_position_score = Column(Float, nullable=True)
    classification = Column(String(50), nullable=True)

    scoring_breakdown = Column(JSON, nullable=True)

    analysis_started_at = Column(DateTime, nullable=True)
    analysis_completed_at = Column(DateTime, nullable=True)
    analysis_duration_seconds = Column(Float, nullable=True)

    data_completeness = Column(Float, default=0.0)
    confidence_level = Column(String(50), default="unknown")

    errors = Column(JSON, default=list)
    warnings = Column(JSON, default=list)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (Index("ix_audit_company_batch", "company_id", "gathering_batch_id"),)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "gathering_batch_id": self.gathering_batch_id,
            "company_name": self.company_name,
            "raw_data": self.raw_data,
            "aggregated_facts": self.aggregated_facts,
            "extracted_signals": self.extracted_signals,
            "growth_score": self.growth_score,
            "financial_health_score": self.financial_health_score,
            "competitive_position_score": self.competitive_position_score,
            "classification": self.classification,
            "analysis_started_at": (
                self.analysis_started_at.isoformat() if self.analysis_started_at is not None else None
            ),
            "analysis_completed_at": (
                self.analysis_completed_at.isoformat() if self.analysis_completed_at is not None else None
            ),
            "data_completeness": self.data_completeness,
            "confidence_level": self.confidence_level,
            "created_at": (self.created_at.isoformat() if self.created_at is not None else None),
        }
