"""
Celery background tasks.
"""

from typing import Any

from celery import shared_task
from loguru import logger

from .config import get_settings
from .data.repositories import JsonFileRepository
from .exporters.excel_exporter import ExcelExporter

settings = get_settings()

@shared_task(name="export_marketing_report")
def export_marketing_report(filters: dict[str, Any], output_filename: str) -> str:
    """
    Generate Excel report in background.

    Args:
        filters: Dictionary of filters to apply to the repository query.
        output_filename: Name of the output file.

    Returns:
        Absolute path to the generated file.
    """
    logger.info(f"Starting background export task. Filters: {filters}")

    # 1. Initialize Repository (fresh instance for the worker)
    # Note: in a real DB scenario, we'd use a session factory.
    # For JSON file repo, it's safe to instantiate.
    repo = JsonFileRepository(data_dir=settings.data.data_dir)

    # 2. Fetch Data
    companies = repo.get_all(filters=filters)

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
