from datetime import datetime
from typing import Any

from celery import shared_task
from loguru import logger

from .config import get_settings
from .data.repositories import JsonFileRepository
from .exporters.excel_exporter import ExcelExporter


@shared_task(name="export_marketing_report")
def export_marketing_report(filters: dict[str, Any], output_filename: str) -> str:
    """
    Generate Excel report in background.
    """
    logger.info(f"Starting background export task. Filters: {filters}")

    settings = get_settings()
    # 1. Initialize Repository
    repo = JsonFileRepository(data_dir=settings.data.data_dir)

    from .core.repositories import CompanyFilter
    # 2. Fetch Data
    companies = repo.get_all(filters=CompanyFilter(**filters))

    if not companies:
        logger.warning("No companies found matching filters.")
        return "No data found"

    # 3. Export
    exporter = ExcelExporter()
    output_dir = settings.data.export_dir
    output_path = output_dir / output_filename

    logger.info(f"Generating Excel report at {output_path}")
    exporter.create_dashboard(companies, output_path)

    return str(output_path)


@shared_task(name="batch_score_companies")
def batch_score_companies(filters: dict[str, Any]) -> dict[str, Any]:
    """
    Score multiple companies in the background.
    """
    logger.info(f"Starting background batch scoring task. Filters: {filters}")

    from .analytics.scoring import GrowthScorer
    from .core.repositories import CompanyFilter

    settings = get_settings()
    repo = JsonFileRepository(data_dir=settings.data.data_dir)
    scorer = GrowthScorer()

    # Fetch data
    companies = repo.get_all(filters=CompanyFilter(**filters))
    
    results = []
    for company in companies:
        try:
            scored = scorer.calculate_scores(company)
            growth = scored.growth_score or 0.0
            
            classification = "Neutral"
            if growth >= 7.0:
                classification = "Rocket"
            elif growth <= 4.0:
                classification = "Dinosaur"

            results.append({
                "company_id": company.id,
                "company_name": company.name,
                "growth_score": scored.growth_score,
                "classification": classification,
                "status": "success"
            })
        except Exception as e:
            logger.warning(f"Error scoring company {company.id}: {e}")
            results.append({
                "company_id": company.id,
                "error": str(e),
                "status": "error"
            })

    return {
        "total_processed": len(results),
        "results": results,
        "completed_at": datetime.now().isoformat()
    }
