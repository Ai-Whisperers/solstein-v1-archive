from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...api.schemas import CompanyProfileSchema
from ...config import get_settings
from ...core.repositories import CompanyFilter, CompanyRepository
from ...exporters.excel_exporter import ExcelExporter
from ...tasks import export_marketing_report
from ...core.repositories import CompanyRepository
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Export"])
settings = get_settings()
growth_scorer = GrowthScorer()
excel_exporter = ExcelExporter()


@router.get("/excel")
async def export_to_excel(
    industry: str | None = Query(None, description="Industry to export"),
    include_charts: bool = Query(True, description="Include charts in Excel"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Trigger background Excel export."""
    try:
        # Generate filters
        filters: dict[str, Any] = {}
        if industry:
            filters["industry"] = industry

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if industry:
            filename = f"solstein_{industry.lower().replace(' ', '_')}_{timestamp}.xlsx"
        else:
            filename = f"solstein_dashboard_{timestamp}.xlsx"

        # Trigger Celery task
        # Note: In production we'd use .delay(). For now assuming Celery is configured.
        task = export_marketing_report.delay(filters=filters, output_filename=filename)

        return {
            "message": "Export started",
            "task_id": task.id,
            "filename": filename,
            "status": "processing",
        }
    except Exception as e:
        logger.error(f"Error triggering export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Error triggering export: {str(e)}"
            ),
        ) from e


@router.get("/json")
async def export_to_json(
    industry: str | None = Query(None, description="Industry to export"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> JSONResponse:
    """Export company data to JSON."""
    try:
        filters = CompanyFilter(industry=industry)

        filtered_companies = repo.get_all(filters=filters)

        # Filter by industry if specified (manual check to be safe)
        if industry:
            filtered_companies = [
                c
                for c in filtered_companies
                if c.industry and industry.lower() in c.industry.lower()
            ]

        if not filtered_companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No companies found for industry: {industry}",
            )

        # Convert to dict with JSON serializable values
        companies_data = []
        for company in filtered_companies:
            # Map Domain Entity -> Schema -> Dict
            schema = CompanyProfileSchema.model_validate(company)
            company_dict = schema.model_dump(mode="json")

            # Add scores
            scored = growth_scorer.calculate_scores(company)
            company_dict.update(
                {
                    "growth_score": scored.growth_score,
                    "financial_health_score": scored.financial_health_score,
                    "competitive_position_score": scored.competitive_position_score,
                }
            )
            companies_data.append(company_dict)

        # Create output
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_companies": len(companies_data),
            "companies": companies_data,
        }

        return JSONResponse(content=export_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting to JSON: {str(e)}",
        ) from e
