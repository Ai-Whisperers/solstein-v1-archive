
from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...api.schemas import CompanyProfileSchema
from ...core.repositories import CompanyRepository
from ...data.models import CompanyTier
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Companies"])
growth_scorer = GrowthScorer()

@router.get("/companies", response_model=list[CompanyProfileSchema])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    tier: CompanyTier | None = Query(None, description="Filter by company tier"),
    industry: str | None = Query(None, description="Filter by industry"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue in EUR millions"),
    _: dict = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository)
):
    """Get list of companies with optional filtering."""
    try:
        # Use Repository Pattern
        filters = {
            "tier": tier,
            "industry": industry,
            "min_revenue": min_revenue
        }

        # Get filtered results directly from repository (Returns Domain Entities)
        filtered_companies = repo.get_all(filters=filters)

        # Apply pagination
        paginated = filtered_companies[skip:skip + limit]

        return paginated
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}"
        )


@router.get("/companies/{company_id}", response_model=CompanyProfileSchema)
async def get_company(
    company_id: str,
    _: dict = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository)
):
    """Get company by ID."""
    try:
        company = repo.get_by_id(company_id)

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {company_id} not found"
            )

        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving company: {str(e)}"
        )


@router.post("/companies", response_model=CompanyProfileSchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyProfileSchema,
    _: dict = Depends(get_current_user)
):
    """Create a new company profile."""
    try:
        # In production, this would save to database
        # For demo, just validate and return
        logger.info(f"Creating company: {company.name}")

        # Calculate scores
        scored_company = growth_scorer.calculate_scores(company)

        return scored_company
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {str(e)}"
        )
