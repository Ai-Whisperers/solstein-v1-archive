"""Full-text search for companies using PostgreSQL tsvector.

Implements EPIC-029: full-text search against company name, description,
and industry fields using PostgreSQL's built-in GIN-indexed tsvector.

Usage::

    from solstein.infrastructure.search import CompanySearchService

    svc = CompanySearchService(session)
    results = await svc.search("fintech payments SaaS", limit=20)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from loguru import logger
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database_models import CompanyRecord

if TYPE_CHECKING:
    pass


# PostgreSQL full-text search configuration (English language stemming)
_TS_CONFIG = "english"


class CompanySearchService:
    """Full-text search service backed by PostgreSQL tsvector.

    Uses ``to_tsvector('english', ...)`` and ``to_tsquery('english', ...)``
    for stemmed keyword matching across name + description + industry.
    Falls back to ILIKE for very short or symbol-only queries.

    Args:
        session: Active async SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        tier: str | None = None,
        industry: str | None = None,
    ) -> tuple[list[CompanyRecord], int]:
        """Search companies by full-text query.

        Args:
            query: Free-text search string (e.g. ``"fintech payments B2B"``).
            limit: Max results to return.
            offset: Pagination offset.
            tier: Optional tier filter (``'Phoenix'``, ``'Salt'``, ``'Lead'``).
            industry: Optional exact industry filter.

        Returns:
            Tuple of (company records, total count).
        """
        query = query.strip()
        if not query:
            return [], 0

        # Decide: FTS or ILIKE?
        stmt = self._build_fts_stmt(query)
        count_stmt = self._build_fts_count_stmt(query)

        # Apply filters
        if tier:
            stmt = stmt.where(CompanyRecord.tier == tier)
            count_stmt = count_stmt.where(CompanyRecord.tier == tier)
        if industry:
            stmt = stmt.where(CompanyRecord.industry == industry)
            count_stmt = count_stmt.where(CompanyRecord.industry == industry)

        stmt = stmt.limit(limit).offset(offset)

        try:
            count_result = await self._session.execute(count_stmt)
            total: int = count_result.scalar_one_or_none() or 0

            result = await self._session.execute(stmt)
            records: list[CompanyRecord] = list(result.scalars().all())

            logger.debug(
                "Full-text search executed",
                query=query,
                total=total,
                returned=len(records),
            )
            return records, total
        except Exception as exc:
            logger.error("Full-text search failed, falling back to ILIKE", error=str(exc))
            return await self._ilike_fallback(query, limit, offset)

    def _build_fts_stmt(self, query: str) -> Any:
        """Build a ranked tsvector SELECT statement."""
        tsquery = func.plainto_tsquery(_TS_CONFIG, query)
        tsvector = func.to_tsvector(
            _TS_CONFIG,
            func.coalesce(CompanyRecord.name, "")
            + " "
            + func.coalesce(CompanyRecord.description, "")
            + " "
            + func.coalesce(CompanyRecord.industry, ""),
        )
        rank = func.ts_rank(tsvector, tsquery).label("rank")
        stmt = (
            select(CompanyRecord)
            .where(tsvector.op("@@")(tsquery))
            .order_by(rank.desc(), CompanyRecord.composite_score.desc())
        )
        return stmt

    def _build_fts_count_stmt(self, query: str) -> Any:
        """Build the COUNT version of the FTS query."""
        from sqlalchemy import func as _func

        tsquery = _func.plainto_tsquery(_TS_CONFIG, query)
        tsvector = _func.to_tsvector(
            _TS_CONFIG,
            _func.coalesce(CompanyRecord.name, "")
            + " "
            + _func.coalesce(CompanyRecord.description, "")
            + " "
            + _func.coalesce(CompanyRecord.industry, ""),
        )
        return select(_func.count()).select_from(CompanyRecord).where(tsvector.op("@@")(tsquery))

    async def _ilike_fallback(self, query: str, limit: int, offset: int) -> tuple[list[CompanyRecord], int]:
        """ILIKE fallback for short/symbol queries or when tsvector fails."""
        pattern = f"%{query}%"
        stmt = (
            select(CompanyRecord)
            .where(
                or_(
                    CompanyRecord.name.ilike(pattern),
                    CompanyRecord.description.ilike(pattern),
                    CompanyRecord.industry.ilike(pattern),
                )
            )
            .order_by(CompanyRecord.composite_score.desc())
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(CompanyRecord)
            .where(
                or_(
                    CompanyRecord.name.ilike(pattern),
                    CompanyRecord.description.ilike(pattern),
                    CompanyRecord.industry.ilike(pattern),
                )
            )
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one_or_none() or 0
        result = await self._session.execute(stmt)
        return list(result.scalars().all()), total


# GIN index DDL for migration reference:
GIN_INDEX_DDL = text(
    """
    CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_companies_fts
    ON companies
    USING GIN (
        to_tsvector(
            'english',
            coalesce(name, '') || ' ' ||
            coalesce(description, '') || ' ' ||
            coalesce(industry, '')
        )
    );
    """
)
"""DDL statement to create a GIN full-text search index on the companies table.

Run this in a migration (Alembic) to enable fast tsvector queries::

    from solstein.infrastructure.search import GIN_INDEX_DDL
    async with engine.connect() as conn:
        await conn.execute(GIN_INDEX_DDL)
        await conn.commit()
"""
