"""Market analysis and search API routes.

Provides endpoints for:
- Market analysis by industry/region
- Competitive overlap calculations
- Company search with pagination
"""

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from ...analytics.scoring import CompetitiveOverlapCalculator, MarketAnalyzer
from ...infrastructure.company_repository import CompanyRepository
from ...domain.models import CompetitiveOverlap, MarketAnalysis
from ..dependencies import get_current_user, get_company_repository
from ..exceptions import APIError

router = APIRouter(tags=["Market Analysis"])
market_analyzer = MarketAnalyzer()
overlap_calculator = CompetitiveOverlapCalculator()


@router.get("/analysis", response_model=MarketAnalysis)
async def analyze_market(
    industry: str | None = Query(None, description="Industry to analyze"),
    region: str | None = Query(None, description="Region to analyze"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum companies to analyze"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> MarketAnalysis:
    """Perform market analysis for a specific industry/region."""
    try:
        # Use database-level filtering with pagination
        companies = await repo.get_all_filtered(
            industry=industry,
            region=region,
            limit=limit,
        )

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
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error analyzing market",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/overlap/{company_id}", response_model=list[CompetitiveOverlap])
async def get_competitive_overlap(
    company_id: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of competitors to return"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> list[CompetitiveOverlap]:
    """Calculate competitive overlap using the specialized calculator."""
    try:
        # Get target company with caching
        target = await repo.get_by_id(company_id)
        if not target:
            raise APIError(
                code="NOT_FOUND",
                message=f"Company {company_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Get peers from same industry (database-level filtering)
        peers = await repo.filter_by(industry=target.industry)

        # Calculate overlaps using the domain logic
        overlaps = []
        peer_count = 0
        for peer in peers:
            if peer.company_id == target.company_id:
                continue

            if peer_count >= limit:
                break

            # Use the actual calculator
            score = overlap_calculator.calculate_overlap(target, peer)

            overlaps.append(
                CompetitiveOverlap(
                    company_a_id=target.company_id,
                    company_b_id=peer.company_id,
                    overlap_score=score,
                    overlap_areas=[target.industry]
                    if target.industry and peer.industry and target.industry.lower() == peer.industry.lower()
                    else [],
                    competitive_intensity="Medium",
                    notes=None,
                )
            )
            peer_count += 1

        # Sort by overlap score descending
        overlaps.sort(key=lambda x: x.overlap_score, reverse=True)

        return overlaps
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error calculating overlap: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error calculating competitive overlap",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/search", tags=["Search"])
async def search_companies(
    query: str = Query(..., min_length=2, description="Search query"),
    field: str = Query("name", description="Field to search (name, industry, description)"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results to return"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> dict[str, Any]:
    """Search companies by various fields."""
    try:
        # Use database-level search with pagination
        companies = await repo.search(query=query, field=field)

        # Apply pagination in Python since search doesn't support skip/limit yet
        total = len(companies)
        paginated = companies[skip : skip + limit]

        return {
            "query": query,
            "field": field,
            "skip": skip,
            "limit": limit,
            "total_results": total,
            "results": paginated,
        }
    except ValueError as e:
        logger.warning(f"Invalid search parameters: {e}")
        raise APIError(
            code="BAD_REQUEST",
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from e
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error searching companies",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e
