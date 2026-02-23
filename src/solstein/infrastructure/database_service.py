from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import CompanyAnalysisAuditTrail
from .database_models import (
    AuditTrailRecord,
    MarketSnapshot,
    ScoringRecord,
    SignalRecord,
)


class DatabaseService:
    """Service for database persistence operations."""

    def __init__(self, session: AsyncSession):
        """Initialize with an async database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def save_scoring_record(
        self,
        company_id: str,
        company_name: str,
        growth_score: float,
        financial_health_score: float,
        competitive_position_score: float,
        overall_score: float,
        classification: str,
        data_sources_used: dict | None = None,
    ) -> ScoringRecord:
        """Save a scoring record to the database."""
        record = ScoringRecord(
            company_id=company_id,
            company_name=company_name,
            growth_score=growth_score,
            financial_health_score=financial_health_score,
            competitive_position_score=competitive_position_score,
            overall_score=overall_score,
            classification=classification,
            data_sources_used=data_sources_used,
            scored_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def save_signal(
        self,
        scoring_record_id: int,
        signal_name: str,
        signal_category: str,
        source_agent: str,
        confidence: float,
        signal_value: float | None = None,
        signal_text: str | None = None,
        evidence: dict | None = None,
    ) -> SignalRecord:
        """Save a signal record linked to a scoring record."""
        signal = SignalRecord(
            scoring_record_id=scoring_record_id,
            signal_name=signal_name,
            signal_category=signal_category,
            source_agent=source_agent,
            confidence=confidence,
            signal_value=signal_value,
            signal_text=signal_text,
            evidence=evidence,
            extracted_at=datetime.now(UTC),
        )
        self.session.add(signal)
        await self.session.flush()
        return signal

    async def save_market_snapshot(
        self,
        total_companies_scored: int,
        average_growth_score: float,
        average_financial_score: float,
        average_competitive_score: float,
        phoenix_count: int,
        salt_count: int,
        lead_count: int,
        market_metadata: dict | None = None,
    ) -> MarketSnapshot:
        """Save a market snapshot for trend analysis."""
        snapshot = MarketSnapshot(
            snapshot_date=datetime.now(UTC),
            total_companies_scored=total_companies_scored,
            average_growth_score=average_growth_score,
            average_financial_score=average_financial_score,
            average_competitive_score=average_competitive_score,
            phoenix_count=phoenix_count,
            salt_count=salt_count,
            lead_count=lead_count,
            market_metadata=market_metadata,
        )
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def save_audit_trail(self, audit_trail: CompanyAnalysisAuditTrail) -> AuditTrailRecord:
        """Save a complete company analysis audit trail."""
        record = AuditTrailRecord(
            company_id=audit_trail.company_id,
            gathering_batch_id=audit_trail.gathering_batch_id,
            company_name=audit_trail.company_name,
            raw_data=audit_trail.raw_data.model_dump() if audit_trail.raw_data else None,
            aggregated_facts=audit_trail.aggregated_facts.model_dump() if audit_trail.aggregated_facts else None,
            extracted_signals=audit_trail.extracted_signals.model_dump() if audit_trail.extracted_signals else None,
            growth_score=audit_trail.growth_score,
            financial_health_score=audit_trail.financial_health_score,
            competitive_position_score=audit_trail.competitive_position_score,
            classification=audit_trail.classification,
            scoring_breakdown=audit_trail.scoring_breakdown,
            analysis_started_at=audit_trail.analysis_started_at,
            analysis_completed_at=audit_trail.analysis_completed_at,
            analysis_duration_seconds=audit_trail.analysis_duration_seconds,
            data_completeness=audit_trail.data_completeness,
            confidence_level=audit_trail.confidence_level,
            errors=audit_trail.errors,
            warnings=audit_trail.warnings,
            created_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_audit_trail(self, company_id: str) -> AuditTrailRecord | None:
        """Get the most recent audit trail for a company."""
        query = (
            select(AuditTrailRecord)
            .where(AuditTrailRecord.company_id == company_id)
            .order_by(desc(AuditTrailRecord.created_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_company_scores(self, company_id: str, limit: int = 10) -> list[ScoringRecord]:
        """Get historical scores for a company."""
        query = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(desc(ScoringRecord.scored_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_score(self, company_id: str) -> ScoringRecord | None:
        """Get the most recent score for a company."""
        query = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(desc(ScoringRecord.scored_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_signals_for_score(self, scoring_record_id: int) -> list[SignalRecord]:
        """Get all signals for a scoring record."""
        query = select(SignalRecord).where(SignalRecord.scoring_record_id == scoring_record_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_market_snapshots(self, limit: int = 10) -> list[MarketSnapshot]:
        """Get recent market snapshots."""
        query = select(MarketSnapshot).order_by(desc(MarketSnapshot.snapshot_date)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()
