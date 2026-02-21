from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import CompetitiveOverlapCalculator, MarketAnalyzer
from ...core.repositories import CompanyFilter, CompanyRepository
from ...domain.models import CompetitiveOverlap, MarketAnalysis
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Market Analysis"])
market_analyzer = MarketAnalyzer()
overlap_calculator = CompetitiveOverlapCalculator()


@router.get("/analysis", response_model=MarketAnalysis)
async def analyze_market(
    industry: str | None = Query(None, description="Industry to analyze"),
    region: str | None = Query(None, description="Region to analyze"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> MarketAnalysis:
    """Perform market analysis for a specific industry/region."""
    try:
        # Pass filters to repository for efficient data fetching
        filters = CompanyFilter(industry=industry)
        companies = repo.get_all(filters=filters)

        if region:
            companies = [
                c
                for c in companies
                if region.lower() in [p.lower() for p in c.geographic_presence]
            ]  # noqa: E501

        if not companies:
            return MarketAnalysis(
                market_name=industry or "Total Market",
                companies=[],
            )

        analysis = market_analyzer.analyze_market(companies)
        if industry:
            analysis.market_name = industry

        return analysis
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing market: {str(e)}",
        ) from e


@router.get("/overlap/{company_id}", response_model=list[CompetitiveOverlap])
async def get_competitive_overlap(
    company_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> list[CompetitiveOverlap]:
    """Calculate competitive overlap using the specialized calculator."""
    try:
        target = repo.get_by_id(company_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {company_id} not found",
            )

        # Get peers (same industry)
        filters = CompanyFilter(industry=target.industry)
        all_companies = repo.get_all(filters=filters)

        # Calculate overlaps using the domain logic
        overlaps = []
        for peer in all_companies:
            if peer.id == target.id:
                continue

            # Use the actual calculator (already instantiated in this module)
            score = overlap_calculator.calculate_overlap(target, peer)

            overlaps.append(
                CompetitiveOverlap(
                    company_a_id=target.id,
                    company_b_id=peer.id,
                    overlap_score=score,
                    overlap_areas=[target.industry]
                    if target.industry
                    and peer.industry
                    and target.industry.lower() == peer.industry.lower()
                    else [],  # noqa: E501
                    competitive_intensity="Medium",
                    notes=None,
                )
            )

        # Sort by overlap score descending (ensure standard integer/float returning for Mypy)  # noqa: E501
        def _get_score(overlap: CompetitiveOverlap) -> float:
            return float(overlap.overlap_score)

        overlaps.sort(key=_get_score, reverse=True)

        return overlaps[:10]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating overlap: {e}")
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
