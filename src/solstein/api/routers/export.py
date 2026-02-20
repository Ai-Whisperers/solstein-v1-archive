from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...api.schemas import CompanyProfileSchema
from ...config import get_settings
from ...core.repositories import CompanyFilter, CompanyRepository
from ...exporters.excel_exporter import ExcelExporter
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Export"])
settings = get_settings()
growth_scorer = GrowthScorer()
excel_exporter = ExcelExporter()


def _run_excel_export(repo: CompanyRepository, filters: dict[str, Any], filename: str) -> None:
    """Background task to generate excel report."""
    company_filter = CompanyFilter(**filters) if filters else None
    companies = repo.get_all(filters=company_filter)
    if companies:
        output_path = settings.data.export_dir / filename
        excel_exporter.create_dashboard(companies, output_path)
        logger.info(f"Excel report generated at {output_path}")


@router.get("/excel")
async def export_to_excel(
    background_tasks: BackgroundTasks,
    industry: str | None = Query(None, description="Industry to export"),
    include_charts: bool = Query(True, description="Include charts in Excel"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Trigger background Excel export."""
    try:
        filters: dict[str, Any] = {}
        if industry:
            filters["industry"] = industry

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if industry:
            filename = f"solstein_{industry.lower().replace(' ', '_')}_{timestamp}.xlsx"
        else:
            filename = f"solstein_dashboard_{timestamp}.xlsx"

        background_tasks.add_task(_run_excel_export, repo, filters, filename)

        return {
            "message": "Export started",
            "filename": filename,
            "status": "processing",
        }
    except Exception as e:
        logger.error(f"Error triggering export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering export: {str(e)}",
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
