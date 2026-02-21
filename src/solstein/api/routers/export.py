from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...config import get_settings
from ...core.repositories import CompanyFilter, CompanyRepository
from ...exporters.excel_exporter import ExcelExporter
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Export"])
settings = get_settings()
growth_scorer = GrowthScorer()
excel_exporter = ExcelExporter()


def _run_excel_export(
    repo: CompanyRepository, filters: dict[str, Any], filename: str
) -> None:  # noqa: E501
    """Background task to generate excel report."""
    company_filter = CompanyFilter(**filters) if filters else None
    companies = repo.get_all(filters=company_filter)

    # Apply scoring to all companies before export
    if companies:
        scored_companies = []
        for company in companies:
            try:
                scored = growth_scorer.calculate_scores(company)
                scored_companies.append(scored)
            except Exception as e:
                logger.warning(f"Failed to score company {company.name}: {e}")
                scored_companies.append(company)
        companies = scored_companies

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
            # Score and map Domain Entity directly to Dict
            scored = growth_scorer.calculate_scores(company)
            company_dict = scored.model_dump(mode="json")
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


@router.get("/search/llm")
async def search_with_llm(
    criteria: str = Query(
        ...,
        description="Natural language search criteria (e.g., 'tech companies', 'fast growing SaaS')",
    ),
    limit: int | None = Query(None, description="Maximum number of results"),
    include_reasoning: bool = Query(
        True, description="Include LLM reasoning in response"
    ),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> JSONResponse:
    """Search and filter companies using natural language criteria via LLM.

    This endpoint uses AI to understand natural language criteria and match
    companies based on their full profile, not just keyword matching.
    """
    try:
        from ...data.repositories import JsonFileRepository

        if not isinstance(repo, JsonFileRepository):
            return JSONResponse(
                content={
                    "error": "LLM filtering is only available for JSON repository"
                },
                status_code=400,
            )

        companies, filter_metadata = await repo.get_all_llm_filtered(
            criteria=criteria,
            limit=limit,
        )

        if not companies:
            return JSONResponse(
                content={
                    "criteria": criteria,
                    "total_matched": 0,
                    "companies": [],
                    "message": "No companies matched the criteria",
                }
            )

        scored_companies = []
        for company in companies:
            scored = growth_scorer.calculate_scores(company)
            scored_companies.append(scored)

        companies_data = [c.model_dump(mode="json") for c in scored_companies]

        response = {
            "criteria": criteria,
            "total_matched": filter_metadata["total_matched"],
            "total_checked": filter_metadata["total_checked"],
            "companies": companies_data,
        }

        if include_reasoning:
            response["filter_reasoning"] = filter_metadata["reasoning"]

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error in LLM search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in LLM search: {str(e)}",
        ) from e
