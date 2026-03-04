import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from ...analytics.company_loader import unified_score_loader
from ...analytics.scoring import GrowthScorer
from ...core.repositories import CompanyRepository
from ..dependencies import get_company_repository, get_current_user
from ..exceptions import APIError

router = APIRouter(tags=["Scoring"])
growth_scorer = GrowthScorer()


@router.post("/company/{company_id}/score")
async def score_company(
    company_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> dict[str, Any]:
    """Calculate growth and competitive scores for a company."""
    try:
        # One high-performance lookup
        # Load company with unified JSON + Markdown data for accurate scoring
        target_company = await asyncio.to_thread(unified_score_loader.load_company_for_scoring, company_id)
        if not target_company:
            # Fallback to repository if unified loader fails
            target_company = await repo.get_by_id(company_id)

        if not target_company:
            raise APIError(
                code="NOT_FOUND",
                message=f"Company with ID {company_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Calculate scores with explanations
        scored_company = growth_scorer.calculate_scores(target_company)

        growth_score = scored_company.growth_score or 0.0
        if growth_score >= 7.0:
            classification = "Phoenix"
        elif growth_score <= 3.9:
            classification = "Lead"
        else:
            classification = "Salt"

        # Save the scores back to the DB to keep it 'magically' up to date
        await repo.save(scored_company)

        return {
            "company_id": company_id,
            "growth_score": scored_company.growth_score,
            "financial_health_score": scored_company.financial_health_score,
            "competitive_position_score": scored_company.competitive_position_score,
            "composite_score": scored_company.composite_score,
            "classification": classification,
            "scoring_breakdown": scored_company.scoring_breakdown,
            "calculated_at": datetime.now().isoformat(),
        }
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error scoring company {company_id}: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error scoring company",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/batch")
async def batch_score_companies_endpoint(
    industry: str | None = Query(None, description="Industry to score"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue"),
    _: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Batch score multiple companies.

    NOTE: Temporal integration has been removed. This endpoint is disabled.
    """
    raise APIError(
        code="NOT_IMPLEMENTED",
        message="Batch scoring endpoint disabled - Temporal integration removed. Use individual /company/COMPANY_ID/score endpoint instead.",
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
    )


@router.get("/stats", tags=["Statistics"])
async def get_statistics(
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> dict[str, Any]:
    """Get platform statistics. Uses stored values for maximum performance."""
    try:
        # In a real high-perf scenario, we'd use a SQL AGGREGATE call
        # For now, fetching domain entities is still faster than re-scoring
        companies = await repo.get_all()

        total_companies = len(companies)

        # Revenue statistics
        revenues = [c.financials.revenue for c in companies if c.financials.revenue]
        total_revenue = sum(revenues) if revenues else 0
        avg_revenue = total_revenue / len(revenues) if revenues else 0

        # Growth statistics
        growth_rates = [c.financials.growth_rate for c in companies if c.financials.growth_rate]
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

        # Tier & Classification distribution (using STORED values)
        tier_counts: dict[str, int] = {}
        class_counts = {"Phoenix": 0, "Lead": 0, "Salt": 0}

        for company in companies:
            tier = company.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

            cls_val = company.classification or "Salt"
            class_counts[cls_val] = class_counts.get(cls_val, 0) + 1

        return {
            "total_companies": total_companies,
            "revenue_statistics": {
                "total_revenue_eur_m": total_revenue,
                "average_revenue_eur_m": avg_revenue,
                "companies_with_revenue_data": len(revenues),
            },
            "growth_statistics": {
                "average_growth_rate_pct": avg_growth,
                "companies_with_growth_data": len(growth_rates),
            },
            "tier_distribution": tier_counts,
            "growth_classification": class_counts,
            "calculated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error calculating statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e
