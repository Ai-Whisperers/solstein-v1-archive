"""Eager loading repository patterns for N+1 query elimination.

EPIC-025 Story 3: Implements eager loading using SQLAlchemy's selectinload and
joinedload to eliminate N+1 query patterns when fetching related data.

Usage:
    # Instead of N+1 queries
    companies = await repo.get_all()
    for c in companies:
        scores = await scoring_repo.get_by_company(c.id)  # N queries!

    # Use eager loading - single query
    companies_with_scores = await eager_repo.get_all_with_scoring()
"""

from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from solstein.infrastructure.database_models import (
    CompanyRecord,
    ScoringRecord,
    SignalRecord,
)

T = TypeVar("T")


class EagerCompanyRepository:
    """Repository with eager loading to eliminate N+1 queries.

    This repository provides methods that load related data (scoring, signals)
    in a single query using SQLAlchemy's eager loading capabilities.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with async database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def get_by_id_with_scoring(self, company_id: str) -> CompanyRecord | None:
        """Get company with all scoring records loaded.

        Uses selectinload to fetch scoring_records in a single query,
        eliminating the N+1 pattern when accessing company scores.

        Args:
            company_id: Unique company identifier.

        Returns:
            CompanyRecord with scoring_records loaded, or None.
        """
        stmt = (
            select(CompanyRecord)
            .where(CompanyRecord.company_id == company_id)
            .options(selectinload(CompanyRecord.scoring_records))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_latest_scoring(self, company_id: str) -> CompanyRecord | None:
        """Get company with only the latest scoring record.

        More efficient than loading all scoring history when only
        the current score is needed.

        Args:
            company_id: Unique company identifier.

        Returns:
            CompanyRecord with latest scoring loaded, or None.
        """
        # First get the company
        stmt = select(CompanyRecord).where(CompanyRecord.company_id == company_id)
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            return None

        # Get latest scoring in separate query (still 2 queries, not N+1)
        scoring_stmt = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(ScoringRecord.scored_at.desc())
            .limit(1)
        )
        scoring_result = await self.session.execute(scoring_stmt)
        latest_scoring = scoring_result.scalar_one_or_none()

        if latest_scoring:
            # Attach to company for convenient access
            company.latest_scoring = latest_scoring

        return company

    async def get_all_with_scoring(self, skip: int = 0, limit: int = 100) -> list[CompanyRecord]:
        """Get all companies with their scoring records.

        Efficiently loads all companies and their scoring history
        in just 2 queries (one for companies, one for all their scores).

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of CompanyRecord objects with scoring_records loaded.
        """
        stmt = select(CompanyRecord).offset(skip).limit(limit).options(selectinload(CompanyRecord.scoring_records))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_batch_with_scoring(self, company_ids: list[str]) -> list[CompanyRecord]:
        """Get multiple companies with scoring in a batch.

        Uses IN clause for efficient batch loading. All companies
        and their scores are loaded in just 2 queries.

        Args:
            company_ids: List of company IDs to fetch.

        Returns:
            List of CompanyRecord objects with scoring_records loaded.
        """
        if not company_ids:
            return []

        stmt = (
            select(CompanyRecord)
            .where(CompanyRecord.company_id.in_(company_ids))
            .options(selectinload(CompanyRecord.scoring_records))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_classification_with_scoring(
        self, classification: str, skip: int = 0, limit: int = 100
    ) -> list[CompanyRecord]:
        """Get companies by classification with scoring loaded.

        Efficiently loads all Phoenix/Salt/Lead companies with their
        complete scoring history for analysis.

        Args:
            classification: Classification filter (Phoenix, Salt, Lead).
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of CompanyRecord objects with scoring_records loaded.
        """
        stmt = (
            select(CompanyRecord)
            .where(CompanyRecord.classification == classification)
            .offset(skip)
            .limit(limit)
            .options(selectinload(CompanyRecord.scoring_records))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class EagerScoringRepository:
    """Repository for scoring records with eager signal loading."""

    def __init__(self, session: AsyncSession):
        """Initialize with async database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def get_by_id_with_signals(self, scoring_id: int) -> ScoringRecord | None:
        """Get scoring record with all signals loaded.

        Eliminates N+1 when iterating through signals for a score.

        Args:
            scoring_id: Scoring record ID.

        Returns:
            ScoringRecord with signals loaded, or None.
        """
        stmt = select(ScoringRecord).where(ScoringRecord.id == scoring_id).options(selectinload(ScoringRecord.signals))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_company_with_signals(
        self, company_id: str, skip: int = 0, limit: int = 100
    ) -> list[ScoringRecord]:
        """Get all scoring records for a company with signals.

        Loads all scores and their signals in just 2 queries.

        Args:
            company_id: Company identifier.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of ScoringRecord objects with signals loaded.
        """
        stmt = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .options(selectinload(ScoringRecord.signals))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_company_with_signals(self, company_id: str) -> ScoringRecord | None:
        """Get latest scoring record with all signals.

        Efficiently loads the most recent score with its complete
        signal breakdown for explainability.

        Args:
            company_id: Company identifier.

        Returns:
            Latest ScoringRecord with signals loaded, or None.
        """
        stmt = (
            select(ScoringRecord)
            .where(ScoringRecord.company_id == company_id)
            .order_by(ScoringRecord.scored_at.desc())
            .limit(1)
            .options(selectinload(ScoringRecord.signals))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_batch_with_signals(self, scoring_ids: list[int]) -> list[ScoringRecord]:
        """Get multiple scoring records with signals.

        Batch loads all requested scores and their signals
        efficiently in just 2 queries.

        Args:
            scoring_ids: List of scoring record IDs.

        Returns:
            List of ScoringRecord objects with signals loaded.
        """
        if not scoring_ids:
            return []

        stmt = (
            select(ScoringRecord).where(ScoringRecord.id.in_(scoring_ids)).options(selectinload(ScoringRecord.signals))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class BatchLoader:
    """Utility for batch loading related data efficiently.

    Implements the DataLoader pattern for batching multiple
    individual requests into efficient bulk queries.
    """

    def __init__(self, session: AsyncSession):
        """Initialize with async database session.

        Args:
            session: AsyncSession for database operations.
        """
        self.session = session

    async def load_company_scoring_map(self, company_ids: list[str]) -> dict[str, list[ScoringRecord]]:
        """Load scoring records for multiple companies.

        Returns a mapping of company_id -> list of scoring records.
        Efficiently loads all data in a single query.

        Args:
            company_ids: List of company IDs.

        Returns:
            Dictionary mapping company_id to its scoring records.
        """
        if not company_ids:
            return {}

        stmt = select(ScoringRecord).where(ScoringRecord.company_id.in_(company_ids))
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Group by company_id
        scoring_map: dict[str, list[ScoringRecord]] = {cid: [] for cid in company_ids}
        for record in records:
            if record.company_id in scoring_map:
                scoring_map[record.company_id].append(record)

        return scoring_map

    async def load_scoring_signal_map(self, scoring_ids: list[int]) -> dict[int, list[SignalRecord]]:
        """Load signals for multiple scoring records.

        Returns a mapping of scoring_id -> list of signals.
        Efficiently loads all data in a single query.

        Args:
            scoring_ids: List of scoring record IDs.

        Returns:
            Dictionary mapping scoring_id to its signals.
        """
        if not scoring_ids:
            return {}

        stmt = select(SignalRecord).where(SignalRecord.scoring_record_id.in_(scoring_ids))
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Group by scoring_record_id
        signal_map: dict[int, list[SignalRecord]] = {sid: [] for sid in scoring_ids}
        for record in records:
            if record.scoring_record_id in signal_map:
                signal_map[record.scoring_record_id].append(record)

        return signal_map

    async def load_latest_scoring_for_companies(self, company_ids: list[str]) -> dict[str, ScoringRecord | None]:
        """Load the latest scoring record for each company.

        Uses a window function to efficiently get the latest
        score per company in a single query.

        Args:
            company_ids: List of company IDs.

        Returns:
            Dictionary mapping company_id to its latest scoring.
        """
        if not company_ids:
            return {}

        # Use DISTINCT ON for PostgreSQL to get latest per company
        stmt = (
            select(ScoringRecord)
            .distinct(ScoringRecord.company_id)
            .where(ScoringRecord.company_id.in_(company_ids))
            .order_by(ScoringRecord.company_id, ScoringRecord.scored_at.desc())
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        # Build mapping
        latest_map: dict[str, ScoringRecord | None] = {cid: None for cid in company_ids}
        for record in records:
            latest_map[record.company_id] = record

        return latest_map
