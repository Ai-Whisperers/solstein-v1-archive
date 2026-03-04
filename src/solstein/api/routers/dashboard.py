"""Dashboard API endpoints (EPIC-031).

Provides aggregated summary data for the Next.js front-end dashboard:
- GET /dashboard/summary  — KPI cards (totals, tier breakdown, avg score)
- GET /dashboard/sectors  — Companies grouped by industry/sector
- GET /dashboard/trends   — Composite score trend over time (mocked until
                            historical data is stored)
- GET /dashboard/top      — Top-N companies by composite score
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database import get_async_session
from solstein.infrastructure.database_models import CompanyRecord

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ---------------------------------------------------------------------------
# Summary KPIs
# ---------------------------------------------------------------------------


@router.get("/summary", name="dashboard_summary")
async def get_summary(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, Any]:
    """Return dashboard KPI summary.

    Includes total company count, tier breakdown, score averages,
    and AI maturity distribution.
    """
    logger.debug("Dashboard summary requested")

    # Total companies
    total_result = await session.execute(select(func.count()).select_from(CompanyRecord))
    total: int = total_result.scalar_one_or_none() or 0

    # Tier breakdown
    tier_result = await session.execute(
        select(CompanyRecord.tier, func.count().label("count"))
        .where(CompanyRecord.tier.isnot(None))
        .group_by(CompanyRecord.tier)
    )
    tier_breakdown: dict[str, int] = {row.tier: row.count for row in tier_result}

    # Average scores
    score_result = await session.execute(
        select(
            func.avg(CompanyRecord.composite_score).label("avg_composite"),
            func.avg(CompanyRecord.growth_score).label("avg_growth"),
            func.avg(CompanyRecord.financial_health_score).label("avg_financial"),
            func.avg(CompanyRecord.competitive_position_score).label("avg_competitive"),
        )
    )
    scores = score_result.one()

    # AI maturity distribution
    ai_result = await session.execute(
        select(CompanyRecord.ai_maturity, func.count().label("count"))
        .where(CompanyRecord.ai_maturity.isnot(None))
        .group_by(CompanyRecord.ai_maturity)
    )
    ai_distribution: dict[str, int] = {row.ai_maturity: row.count for row in ai_result}

    return {
        "total_companies": total,
        "tier_breakdown": tier_breakdown,
        "average_scores": {
            "composite": round(scores.avg_composite or 0.0, 2),
            "growth": round(scores.avg_growth or 0.0, 2),
            "financial_health": round(scores.avg_financial or 0.0, 2),
            "competitive_position": round(scores.avg_competitive or 0.0, 2),
        },
        "ai_maturity_distribution": ai_distribution,
    }


# ---------------------------------------------------------------------------
# Sector breakdown
# ---------------------------------------------------------------------------


@router.get("/sectors", name="dashboard_sectors")
async def get_sectors(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
) -> list[dict[str, Any]]:
    """Return companies grouped by industry sector."""
    result = await session.execute(
        select(
            CompanyRecord.industry,
            func.count().label("count"),
            func.avg(CompanyRecord.composite_score).label("avg_score"),
            func.max(CompanyRecord.composite_score).label("max_score"),
        )
        .where(CompanyRecord.industry.isnot(None))
        .group_by(CompanyRecord.industry)
        .order_by(func.count().desc())
        .limit(limit)
    )
    return [
        {
            "industry": row.industry,
            "company_count": row.count,
            "avg_composite_score": round(row.avg_score or 0.0, 2),
            "max_composite_score": round(row.max_score or 0.0, 2),
        }
        for row in result
    ]


# ---------------------------------------------------------------------------
# Top companies
# ---------------------------------------------------------------------------


@router.get("/top", name="dashboard_top_companies")
async def get_top_companies(
    n: int = Query(10, ge=1, le=100),
    tier: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
) -> list[dict[str, Any]]:
    """Return top-N companies ordered by composite score."""
    stmt = (
        select(CompanyRecord)
        .where(CompanyRecord.composite_score.isnot(None))
        .order_by(CompanyRecord.composite_score.desc())
        .limit(n)
    )
    if tier:
        stmt = stmt.where(CompanyRecord.tier == tier)

    result = await session.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "rank": i + 1,
            "name": r.name,
            "tier": r.tier,
            "industry": r.industry,
            "composite_score": r.composite_score,
            "growth_score": r.growth_score,
            "financial_health_score": r.financial_health_score,
            "competitive_position_score": r.competitive_position_score,
            "threat_level": r.threat_level,
        }
        for i, r in enumerate(records)
    ]


# ---------------------------------------------------------------------------
# Score trends (stub — returns mock data until historical snapshots exist)
# ---------------------------------------------------------------------------


@router.get("/trends", name="dashboard_trends")
async def get_trends(
    periods: int = Query(6, ge=1, le=24, description="Number of monthly periods"),
) -> dict[str, Any]:
    """Return composite score trend data.

    Currently returns a mock trend.  When historical score snapshots are
    stored (EPIC-023+), this endpoint will query the snapshot table.
    """
    import datetime as _dt

    now = _dt.datetime.utcnow()
    labels = []
    for i in range(periods, 0, -1):
        month = now.replace(day=1) - _dt.timedelta(days=30 * (i - 1))
        labels.append(month.strftime("%Y-%m"))

    return {
        "labels": labels,
        "note": "Historical snapshot data not yet available. Connect EPIC-023 pgvector snapshots.",
        "avg_composite_score": [None] * periods,
        "phoenix_count": [None] * periods,
    }
