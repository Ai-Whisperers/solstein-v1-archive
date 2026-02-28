from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...core.repositories import CompanyFilter, CompanyRepository
from ...domain.models import Company, CompanyTier
from ..dependencies import get_current_user, get_company_repository

router = APIRouter(tags=["Companies"])
growth_scorer = GrowthScorer()


@router.get("/companies", response_model=list[Company])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    tier: CompanyTier | None = Query(None, description="Filter by company tier"),
    industry: str | None = Query(None, description="Filter by industry"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue in EUR millions"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> list[Company]:
    """Get list of companies with optional filtering."""
    try:
        filters = CompanyFilter(tier=tier, industry=industry, min_revenue=min_revenue)

        # Use server-side pagination in repository
        filtered_companies = repo.get_all(limit=limit, offset=skip, filters=filters)

        return filtered_companies
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}",
        ) from e


@router.get("/companies/{company_id}", response_model=Company)
async def get_company(
    company_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> Any:
    """Get company by ID."""
    try:
        company = repo.get_by_id(company_id)

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found",
            )

        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving company: {str(e)}",
        ) from e


@router.post(
    "/companies",
    response_model=Company,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    company_in: Company,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> Company:
    """Create a new company profile."""
    try:
        logger.info(f"Creating company: {company_in.name}")

        # Calculate scores
        scored_company = growth_scorer.calculate_scores(company_in)

        # Persist to database
        saved_company = repo.save(scored_company)

        return saved_company
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {str(e)}",
        ) from e


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> None:
    """Delete a company profile."""
    try:
        success = repo.delete(company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting company: {str(e)}",
        ) from e
