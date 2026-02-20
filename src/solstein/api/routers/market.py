from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import MarketAnalyzer
from ...core.repositories import CompanyRepository, CompanyFilter
from ...data.models import CompetitiveOverlap, MarketAnalysis
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Market Analysis"])
market_analyzer = MarketAnalyzer()


@router.get("/market/analysis")
async def analyze_market(
    industry: str | None = Query(None, description="Industry to analyze"),
    region: str | None = Query(None, description="Geographic region"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> MarketAnalysis:
    """Analyze market competitive landscape."""
    try:
        # Use repository with filters
        filters = CompanyFilter(industry=industry)
        filtered_companies = repo.get_all(filters=filters)

        if not filtered_companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No companies found for industry: {industry}",
            )

        # Perform market analysis
        analysis = market_analyzer.analyze_market(filtered_companies)

        return MarketAnalysis.model_validate(analysis)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Error analyzing market: {str(e)}"
            ),
        ) from e


@router.get("/market/overlap/{company_id}", response_model=list[CompetitiveOverlap])
async def get_competitive_overlap(
    company_id: str,
    top_n: int = Query(10, ge=1, le=50, description="Number of top overlaps to return"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> list[CompetitiveOverlap]:
    """Get competitive overlap for a company."""
    try:
        # Get target company directly
        target_company = repo.get_by_id(company_id)

        if not target_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found",
            )

        # Get all other companies for comparison
        companies = repo.get_all()

        # Check if target company exists in full list just in case
        # repo.get_by_id behaves differently (Assuming it matches)

        # Calculate overlaps (simplified for demo)
        overlaps = []
        for company in companies:
            if company.id == company_id:
                continue

            # Simple overlap calculation based on industry and tier
            overlap_score = 0.0
            if company.industry == target_company.industry:
                overlap_score += 0.5
            if company.tier == target_company.tier:
                overlap_score += 0.3
            if company.ai_maturity == target_company.ai_maturity:
                overlap_score += 0.2

            overlaps.append(
                CompetitiveOverlap(
                    company_a_id=company_id,
                    company_b_id=company.id,
                    overlap_score=overlap_score,
                    notes=f"Calculated based on industry and tier match at {datetime.now()}",
                )
            )

        # Sort by overlap score and return top N
        overlaps.sort(key=lambda x: x.overlap_score, reverse=True)
        return overlaps[:top_n]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating competitive overlap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating competitive overlap: {str(e)}",
        ) from e


@router.get("/search", tags=["Search"])
async def search_companies(
    query: str = Query(..., min_length=2, description="Search query"),
    field: str = Query(
        "name", description="Field to search (name, industry, description)"
    ),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Search companies by various fields."""
    try:
        # In a real impl, repo would have a search method
        # For now, load all and search in memory
        companies = repo.get_all()

        results = []
        query_lower = query.lower()

        for company in companies:
            search_value = None
            if field == "name" and company.name:
                search_value = company.name.lower()
            elif field == "industry" and company.industry:
                search_value = company.industry.lower()
            elif field == "description" and company.description:
                search_value = company.description.lower()

            if search_value and query_lower in search_value:
                results.append(company)

        return {
            "query": query,
            "field": field,
            "total_results": len(results),
            "results": results[:100],  # Limit results
        }
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching companies: {str(e)}",
        ) from e
