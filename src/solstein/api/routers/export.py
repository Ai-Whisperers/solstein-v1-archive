import asyncio
from datetime import datetime
from typing import Protocol, cast

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from fastapi.responses import JSONResponse
from loguru import logger

from ...analytics.scoring import GrowthScorer
from ...config import get_settings
from ...core.repositories import CompanyFilter, CompanyRepository
from ...domain.models import Company
from ...exporters.excel import ExcelExporter
from ...infrastructure.database import db_manager
from ...infrastructure.repositories import ReleaseGateAuditRepository
from ...data.report_release_gate import ReportReleaseGate
from ..dependencies import get_current_user, get_company_repository
from ..exceptions import APIError

router = APIRouter(tags=["Export"])
settings = get_settings()
growth_scorer = GrowthScorer()
excel_exporter = ExcelExporter()
report_gate = ReportReleaseGate()


class LLMCompanyRepository(Protocol):
    async def get_all_llm_filtered(
        self,
        criteria: str,
        limit: int | None = None,
    ) -> tuple[list[Company], dict[str, object]]: ...


def _reason_details(result) -> list[dict[str, object]]:
    return [{"code": reason.code, "message": reason.message} for reason in result.reasons]


async def _log_gate_decision(
    operation: str,
    status_value: str,
    companies: list[Company],
    reasons: list[dict[str, object]] | None = None,
) -> None:
    company_ids = [company.id for company in companies]
    company_names = [company.name for company in companies]
    reason_codes = [str(reason.get("code", "unknown")) for reason in (reasons or [])]
    async with db_manager.get_session() as session:
        repo = ReleaseGateAuditRepository(session)
        await repo.log_decision(
            operation=operation,
            status=status_value,
            company_ids=company_ids,
            company_names=company_names,
            reason_codes=reason_codes,
            reason_details=reasons,
        )
        await session.commit()


def _gate_or_raise_sync(companies: list[Company], operation: str) -> None:
    result = report_gate.evaluate(companies)
    details = _reason_details(result)
    status_value = "passed" if result.passed else "blocked"
    asyncio.run(_log_gate_decision(operation, status_value, companies, details))
    if result.passed:
        return
    raise APIError(
        code="REPORT_NOT_READY",
        message="Report release gate failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details,
    )


async def _gate_or_raise_async(companies: list[Company], operation: str) -> None:
    result = report_gate.evaluate(companies)
    details = _reason_details(result)
    status_value = "passed" if result.passed else "blocked"
    await _log_gate_decision(operation, status_value, companies, details)
    if result.passed:
        return
    raise APIError(
        code="REPORT_NOT_READY",
        message="Report release gate failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details,
    )


def _run_excel_export(repo: CompanyRepository, filters: dict[str, str], filename: str) -> None:  # noqa: E501
    """Background task to generate excel report."""
    industry = filters.get("industry") if filters else None
    company_filter = CompanyFilter(industry=industry) if industry else None
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

        try:
            _gate_or_raise_sync(companies, operation="excel")
        except APIError as exc:
            logger.error(f"Excel export blocked by gate: {exc.details}")
            return

        output_path = settings.data.export_dir / filename
        excel_exporter.create_dashboard(companies, output_path)
        logger.info(f"Excel report generated at {output_path}")


@router.get("/excel")
async def export_to_excel(
    background_tasks: BackgroundTasks,
    industry: str | None = Query(None, description="Industry to export"),
    include_charts: bool = Query(True, description="Include charts in Excel"),
    _: dict[str, object] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> dict[str, object]:
    """Trigger background Excel export."""
    try:
        _include_charts = include_charts
        filters = {"industry": industry} if industry else {}

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
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error triggering export",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/json")
async def export_to_json(
    industry: str | None = Query(None, description="Industry to export"),
    _: dict[str, object] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> JSONResponse:
    """Export company data to JSON."""
    try:
        filters = CompanyFilter(industry=industry)

        filtered_companies = repo.get_all(filters=filters)

        # Filter by industry if specified (manual check to be safe)
        if industry:
            filtered_companies = [
                c for c in filtered_companies if c.industry and industry.lower() in c.industry.lower()
            ]

        if not filtered_companies:
            raise APIError(
                code="NOT_FOUND",
                message=f"No companies found for industry: {industry}",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Convert to dict with JSON serializable values
        companies_data = []
        scored_companies = []
        for company in filtered_companies:
            # Score and map Domain Entity directly to Dict
            scored = growth_scorer.calculate_scores(company)
            scored_companies.append(scored)
            company_dict = scored.model_dump(mode="json")
            companies_data.append(company_dict)

        await _gate_or_raise_async(scored_companies, operation="json")

        # Create output
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_companies": len(companies_data),
            "companies": companies_data,
        }

        return JSONResponse(content=export_data)
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error exporting to JSON",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/search/llm")
async def search_with_llm(
    criteria: str = Query(
        ...,
        description="Natural language search criteria (e.g., 'tech companies', 'fast growing SaaS')",
    ),
    limit: int | None = Query(None, description="Maximum number of results"),
    include_reasoning: bool = Query(True, description="Include LLM reasoning in response"),
    _: dict[str, object] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_company_repository),
) -> JSONResponse:
    """Search and filter companies using natural language criteria via LLM.

    This endpoint uses AI to understand natural language criteria and match
    companies based on their full profile, not just keyword matching.
    """
    _include_reasoning = include_reasoning
    llm_repo = cast(LLMCompanyRepository, cast(object, repo))
    companies, filter_metadata = await llm_repo.get_all_llm_filtered(
        criteria=criteria,
        limit=limit,
    )
    _ = filter_metadata
    if not companies:
        return JSONResponse(
            content={
                "criteria": criteria,
                "total_matched": 0,
                "companies": [],
            },
            status_code=200,
        )

    return JSONResponse(
        content={
            "criteria": criteria,
            "total_matched": len(companies),
            "companies": [
                {
                    "id": str(c.id),
                    "name": c.name,
                    "industry": c.industry,
                    "classification": c.classification,
                }
                for c in companies
            ],
        },
        status_code=200,
    )
