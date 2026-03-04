import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CompanyRecord(Base):
    """Stores comprehensive company data for PE intelligence.

    This is the main entity for storing detailed company information
    extracted from various sources. All detailed data is stored here
    even if not displayed in Excel exports.
    """

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(500), nullable=False)

    # Basic info
    industry = Column(String(100), default="Energy Software")
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    headquarters = Column(String(100), nullable=True)
    founded_year = Column(Integer, nullable=True)

    # Positioning
    tier = Column(String(50), nullable=True)
    threat_level = Column(String(50), nullable=True)
    classification = Column(String(50), nullable=True)

    # Tech maturity
    ai_maturity = Column(String(50), nullable=True)
    saas_maturity = Column(Integer, nullable=True)
    ai_score = Column(Integer, nullable=True)
    ai_signal_level = Column(String(50), nullable=True)
    ai_key_capabilities = Column(Text, nullable=True)
    ai_in_production = Column(String(10), nullable=True)

    # Financials (latest)
    revenue_eur_m = Column(Float, nullable=True)
    revenue_confidence = Column(String(50), nullable=True)
    growth_rate_pct = Column(Float, nullable=True)
    growth_confidence = Column(String(50), nullable=True)
    profit_margin_pct = Column(Float, nullable=True)
    ebitda_margin_pct = Column(Float, nullable=True)
    recurring_revenue_pct = Column(Float, nullable=True)
    revenue_per_employee_eur_k = Column(Float, nullable=True)

    # Revenue timeline (stored as JSON for full history)
    revenue_timeline = Column(JSON, nullable=True)
    revenue_cagr_3yr = Column(Float, nullable=True)
    revenue_cagr_5yr = Column(Float, nullable=True)

    # Funding
    funding_rounds = Column(JSON, nullable=True)
    total_funding_raised_eur = Column(Float, nullable=True)
    latest_valuation_eur = Column(Float, nullable=True)
    lead_investors = Column(JSON, nullable=True)
    funding_war_chest = Column(Text, nullable=True)

    # Employees
    employee_count = Column(Integer, nullable=True)
    employee_cagr_3yr = Column(Float, nullable=True)
    open_positions = Column(Integer, nullable=True)

    # Raw profitability metrics (from source)
    profitability_raw_metrics = Column(JSON, nullable=True)

    # Data quality
    data_availability = Column(Text, nullable=True)
    data_source = Column(String(255), nullable=True)

    # Scores (calculated)
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
        Index("ix_company_industry", "industry"),  # NEW: For industry filtering
        Index("ix_company_headquarters", "headquarters"),  # NEW: For region filtering
        Index("ix_company_tier", "tier"),
        Index("ix_company_classification", "classification"),
        Index("ix_company_ai_score", "ai_score"),
        Index("ix_company_composite_score", "composite_score"),  # NEW: For sorting by score
        Index("ix_company_revenue_eur_m", "revenue_eur_m"),  # NEW: For revenue filtering
        Index("ix_company_growth_rate", "growth_rate_pct"),  # NEW: For growth filtering
        Index("ix_company_last_updated", "last_updated"),  # NEW: For recency queries
        # Composite index for common filter combinations
        Index("ix_company_industry_headquarters", "industry", "headquarters"),  # NEW: Combined filter
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.name,
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
            "scored_at": (self.scored_at.isoformat() if self.scored_at is not None else None),
            "data_sources_used": self.data_sources_used,
            "signals_count": len(self.signals) if self.signals else 0,
        }


class SignalRecord(Base):
    """Stores individual signals extracted from data sources.

    Each signal represents a data point that contributed to a score.
    """

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
            "extracted_at": (self.extracted_at.isoformat() if self.extracted_at is not None else None),
        }


class MarketSnapshot(Base):
    """Snapshot of market state at a point in time.

    Used for trend analysis and historical comparison.
    """

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
        """Convert to dictionary representation."""
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

    # Analysis artifacts (Stored as JSON for transparency)
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
        """Convert to dictionary representation."""
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


class ResearchRunRecord(Base):
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


class OutboxRecord(Base):
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


class ResearchStageRecord(Base):
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


class EnrichmentAuditRecord(Base):
    """Stores audit trail for enrichment operations (Phase 11).

    Tracks all enrichment requests, successes, failures, and cache hits.
    """

    __tablename__ = "enrichment_audit_trail"

    id = Column(Integer, primary_key=True, index=True)
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
        return datetime.now(timezone.utc) > self.expires_at

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
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        onupdate=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )

    __table_args__ = (
        Index("ix_tenants_api_key_hash", "api_key_hash"),
        Index("ix_tenants_is_active", "is_active"),
    )


class FactRecord(Base):
    """Stores company facts as key-value pairs with confidence scoring."""

    __tablename__ = "fact_records"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String(255), ForeignKey("companies.company_id"), nullable=False, index=True)
    run_id: Mapped[str | None] = mapped_column(String(255), ForeignKey("research_runs.run_id"), nullable=True, index=True)
    fact_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fact_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_fact_records_company_key", "company_id", "fact_key"),
        Index("ix_fact_records_status", "status"),
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "company_id": self.company_id,
            "run_id": self.run_id,
            "fact_key": self.fact_key,
            "fact_value": self.fact_value,
            "status": self.status,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
