"""Service layer for database persistence operations.

Provides high-level operations for storing and retrieving scoring data,
signals, and market snapshots.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .database_models import ScoringRecord, SignalRecord, MarketSnapshot


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
        data_sources_used: Optional[dict] = None,
    ) -> ScoringRecord:
        """Save a scoring record to the database.

        Args:
            company_id: Unique company identifier
            company_name: Human-readable company name
            growth_score: Growth momentum score
            financial_health_score: Financial health score
            competitive_position_score: Competitive position score
            overall_score: Overall composite score
            classification: Score classification (Rocket, Neutral, Dinosaur)
            data_sources_used: Dictionary of data sources and their results

        Returns:
            ScoringRecord: Saved record with database ID
        """
        record = ScoringRecord(
            company_id=company_id,
            company_name=company_name,
            growth_score=growth_score,
            financial_health_score=financial_health_score,
            competitive_position_score=competitive_position_score,
            overall_score=overall_score,
            classification=classification,
            data_sources_used=data_sources_used,
            scored_at=datetime.utcnow(),
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
        signal_value: Optional[float] = None,
        signal_text: Optional[str] = None,
        evidence: Optional[dict] = None,
    ) -> SignalRecord:
        """Save a signal record linked to a scoring record.

        Args:
            scoring_record_id: ID of parent ScoringRecord
            signal_name: Name of the signal
            signal_category: Category (e.g., 'revenue', 'funding', 'hiring')
            source_agent: Name of the agent that extracted the signal
            confidence: Confidence score (0-1)
            signal_value: Numeric value of the signal
            signal_text: Text representation of the signal
            evidence: Dictionary of evidence supporting the signal

        Returns:
            SignalRecord: Saved signal record
        """
        signal = SignalRecord(
            scoring_record_id=scoring_record_id,
            signal_name=signal_name,
            signal_category=signal_category,
            source_agent=source_agent,
            confidence=confidence,
            signal_value=signal_value,
            signal_text=signal_text,
            evidence=evidence,
            extracted_at=datetime.utcnow(),
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
        rocket_count: int,
        neutral_count: int,
        dinosaur_count: int,
        market_metadata: Optional[dict] = None,
    ) -> MarketSnapshot:
        """Save a market snapshot for trend analysis.

        Args:
            total_companies_scored: Number of companies in this snapshot
            average_growth_score: Mean growth score across all companies
            average_financial_score: Mean financial health score
            average_competitive_score: Mean competitive position score
            rocket_count: Count of high-growth companies
            neutral_count: Count of stable companies
            dinosaur_count: Count of legacy companies
            market_metadata: Additional metadata about market state

        Returns:
            MarketSnapshot: Saved snapshot record
        """
        snapshot = MarketSnapshot(
            snapshot_date=datetime.utcnow(),
            total_companies_scored=total_companies_scored,
            average_growth_score=average_growth_score,
            average_financial_score=average_financial_score,
            average_competitive_score=average_competitive_score,
            rocket_count=rocket_count,
            neutral_count=neutral_count,
            dinosaur_count=dinosaur_count,
            market_metadata=market_metadata,
        )
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot

    async def get_company_scores(
        self, company_id: str, limit: int = 10
    ) -> List[ScoringRecord]:
        """Get historical scores for a company.

        Args:
            company_id: Company identifier
            limit: Maximum number of records to return

        Returns:
            List of ScoringRecord sorted by most recent first
        """
        query = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(desc(ScoringRecord.scored_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_score(self, company_id: str) -> Optional[ScoringRecord]:
        """Get the most recent score for a company.

        Args:
            company_id: Company identifier

        Returns:
            Most recent ScoringRecord or None if not found
        """
        query = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(desc(ScoringRecord.scored_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_signals_for_score(self, scoring_record_id: int) -> List[SignalRecord]:
        """Get all signals for a scoring record.

        Args:
            scoring_record_id: ID of the scoring record

        Returns:
            List of SignalRecord
        """
        query = select(SignalRecord).where(
            SignalRecord.scoring_record_id == scoring_record_id
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_market_snapshots(self, limit: int = 10) -> List[MarketSnapshot]:
        """Get recent market snapshots.

        Args:
            limit: Maximum number of snapshots to return

        Returns:
            List of MarketSnapshot sorted by most recent first
        """
        query = (
            select(MarketSnapshot)
            .order_by(desc(MarketSnapshot.snapshot_date))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()
