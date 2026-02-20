from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...tasks import batch_score_companies, export_marketing_report
from ...core.repositories import CompanyRepository
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Scoring"])
growth_scorer = GrowthScorer()


@router.post("/company/{company_id}/score")
async def score_company(
    company_id: str,
    background_tasks: BackgroundTasks,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Calculate growth and competitive scores for a company."""
    try:
        companies = repo.get_all()
        target_company = repo.get_by_id(company_id)

        # In case get_by_id fails or we need to find in list logic from main.py
        if not target_company:
            # Find company manually just to match original logic
            # if repo.get_by_id isn't fully implemented yet
            for company in companies:
                if company.id == company_id:
                    target_company = company
                    break

        if not target_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found",
            )

        # Calculate scores with explanations
        scored_company = growth_scorer.calculate_scores(target_company)

        growth = scored_company.growth_score or 0.0
        
        classification = "Neutral"
        if growth >= 7.0:
            classification = "Rocket"
        elif growth <= 4.0:
            classification = "Dinosaur"

        return {
            "company_id": company_id,
            "growth_score": scored_company.growth_score,
            "financial_health_score": scored_company.financial_health_score,
            "competitive_position_score": scored_company.competitive_position_score,
            "classification": classification,
            "scoring_breakdown": scored_company.scoring_breakdown,
            "calculated_at": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scoring company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring company: {str(e)}",
        ) from e


@router.get("/batch")
async def batch_score_companies_endpoint(
    industry: str | None = Query(None, description="Industry to score"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue"),
    _: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Batch score multiple companies in the background."""
    try:
        filters = {
            "industry": industry,
            "min_revenue": min_revenue
        }
        
        # Trigger Celery task
        task = batch_score_companies.delay(filters=filters)

        return {
            "message": "Batch scoring task started",
            "task_id": task.id,
            "status": "processing",
            "filters": filters
        }
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch scoring: {str(e)}",
        ) from e


@router.get("/stats", tags=["Statistics"])
async def get_statistics(
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Get platform statistics."""
    try:
        companies = repo.get_all()

        # Calculate statistics
        total_companies = len(companies)

        # Revenue statistics
        revenues = [c.financials.revenue for c in companies if c.financials.revenue]
        total_revenue = sum(revenues) if revenues else 0
        avg_revenue = total_revenue / len(revenues) if revenues else 0

        # Growth statistics
        growth_rates = [
            c.financials.growth_rate for c in companies if c.financials.growth_rate
        ]
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

        # Tier distribution
        tier_counts: dict[str, int] = {}
        for company in companies:
            tier = company.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Score companies to get classifications
        rocket_count = 0
        dinosaur_count = 0
        neutral_count = 0

        for company in companies[:50]:  # Limit for performance
            try:
                scored = growth_scorer.calculate_scores(company)
                growth = scored.growth_score or 0.0
                if growth >= 7.0:
                    rocket_count += 1
                elif growth <= 4.0:
                    dinosaur_count += 1
                else:
                    neutral_count += 1
            except Exception:
                neutral_count += 1

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
            "growth_classification": {
                "rockets": rocket_count,
                "dinosaurs": dinosaur_count,
                "neutral": neutral_count,
            },
            "calculated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating statistics: {str(e)}",
        ) from e
