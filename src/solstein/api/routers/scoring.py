from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...core.repositories import CompanyRepository
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Scoring"])
growth_scorer = GrowthScorer()

@router.post("/company/{company_id}/score")
async def score_company(
    company_id: str,
    background_tasks: BackgroundTasks,
    _: dict = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository)
):
    """Calculate growth and competitive scores for a company."""
    try:
        companies = repo.get_all()
        target_company = repo.get_by_id(company_id)

        # In case get_by_id fails or we need to find in list logic from main.py
        if not target_company:
             # Find company manually just to match original logic if repo.get_by_id isn't fully implemented yet
            for company in companies:
                if company.id == company_id:
                    target_company = company
                    break

        if not target_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found"
            )

        # Calculate scores (could be done in background for large datasets)
        scored_company = growth_scorer.calculate_scores(target_company)

        return {
            "company_id": company_id,
            "growth_score": scored_company.growth_score,
            "financial_health_score": scored_company.financial_health_score,
            "competitive_position_score": scored_company.competitive_position_score,
            "classification": "Rocket" if scored_company.growth_score >= 7.0
                          else "Dinosaur" if scored_company.growth_score <= 4.0
                          else "Neutral",
            "calculated_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scoring company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring company: {str(e)}"
        )


@router.get("/batch")
async def batch_score_companies(
    background_tasks: BackgroundTasks,
    industry: str | None = Query(None, description="Industry to score"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue"),
    _: dict = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository)
):
    """Batch score multiple companies (runs in background)."""
    try:
        filters = {
            "industry": industry,
            "min_revenue": min_revenue
        }
        # In main.py filtering logic was partially manual. Using repo filters first.
        filtered_companies_repo = repo.get_all(filters=filters)

        # Manual filtering logic from main.py to be safe/consistent
        filtered_companies = []
        for company in filtered_companies_repo:
            if industry and company.industry and industry.lower() not in company.industry.lower():
                continue
            if min_revenue and company.financials.revenue and company.financials.revenue < min_revenue:
                continue
            filtered_companies.append(company)

        # In production, this would be a background job
        # For demo, score synchronously
        results = []
        for company in filtered_companies[:10]:  # Limit to 10 for demo
            try:
                scored = growth_scorer.calculate_scores(company)
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "growth_score": scored.growth_score,
                    "classification": "Rocket" if scored.growth_score >= 7.0
                                  else "Dinosaur" if scored.growth_score <= 4.0
                                  else "Neutral"
                })
            except Exception as e:
                logger.warning(f"Error scoring company {company.id}: {e}")
                results.append({
                    "company_id": company.id,
                    "company_name": company.name,
                    "error": str(e)
                })

        return {
            "total_companies": len(filtered_companies),
            "scored_companies": len(results),
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch scoring: {str(e)}"
        )

@router.get("/stats", tags=["Statistics"])
async def get_statistics(
    _: dict = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository)
):
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
        growth_rates = [c.financials.growth_rate for c in companies if c.financials.growth_rate]
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

        # Tier distribution
        tier_counts = {}
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
                if scored.growth_score >= 7.0:
                    rocket_count += 1
                elif scored.growth_score <= 4.0:
                    dinosaur_count += 1
                else:
                    neutral_count += 1
            except:
                neutral_count += 1

        return {
            "total_companies": total_companies,
            "revenue_statistics": {
                "total_revenue_eur_m": total_revenue,
                "average_revenue_eur_m": avg_revenue,
                "companies_with_revenue_data": len(revenues)
            },
            "growth_statistics": {
                "average_growth_rate_pct": avg_growth,
                "companies_with_growth_data": len(growth_rates)
            },
            "tier_distribution": tier_counts,
            "growth_classification": {
                "rockets": rocket_count,
                "dinosaurs": dinosaur_count,
                "neutral": neutral_count
            },
            "calculated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating statistics: {str(e)}"
        )
