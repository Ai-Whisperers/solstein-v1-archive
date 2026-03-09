"""
Migration script to load competitor data from JSON into PostgreSQL.

This script reads competitor_data.json and inserts all companies into the
companies table using SQLAlchemy ORM. It is idempotent and can be run
multiple times safely.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from solstein.infrastructure.database_models import CompanyRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _parse_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _build_company_record(competitor: dict[str, object]) -> CompanyRecord:
    profitability = competitor.get("profitability")
    profitability_data: dict[str, Any] = {}
    if isinstance(profitability, dict):
        profitability_data = cast("dict[str, Any]", profitability)

    revenue = competitor.get("revenue")
    revenue_data: dict[str, Any] = {}
    if isinstance(revenue, dict):
        revenue_data = cast("dict[str, Any]", revenue)
    timeline = revenue_data.get("timeline")
    timeline_data: list[dict[str, Any]] = []
    if isinstance(timeline, list):
        for item_obj in cast("list[object]", timeline):
            if isinstance(item_obj, dict):
                timeline_data.append(cast("dict[str, Any]", item_obj))
    latest_timeline: dict[str, Any] = timeline_data[-1] if timeline_data else {}

    return CompanyRecord(
        company_id=str(uuid.uuid4()),
        name=str(competitor.get("company_name") or "unknown"),
        industry=str(competitor.get("industry") or "Energy Software"),
        description=str(competitor.get("description") or "") or None,
        website=str(competitor.get("website") or "") or None,
        headquarters=str(competitor.get("country") or "") or None,
        founded_year=competitor.get("founded_year") if isinstance(competitor.get("founded_year"), int) else None,
        classification=str(competitor.get("classification") or "") or None,
        ai_maturity=str(competitor.get("ai_maturity") or "") or None,
        ai_score=_parse_float(competitor.get("ai_score")),
        revenue_eur_m=_parse_float(latest_timeline.get("eur_millions")),
        growth_rate_pct=_parse_float(competitor.get("growth_rate")),
        profit_margin_pct=_parse_float(competitor.get("profit_margin")),
        ebitda_margin_pct=_parse_float(profitability_data.get("ebitda_margin_pct")),
        recurring_revenue_pct=_parse_float(profitability_data.get("recurring_revenue_pct")),
        revenue_per_employee_eur_k=_parse_float(profitability_data.get("revenue_per_employee_eur_k")),
        revenue_timeline=timeline_data,
        revenue_cagr_3yr=_parse_float(revenue_data.get("cagr_3yr_pct")),
        revenue_cagr_5yr=_parse_float(revenue_data.get("cagr_5yr_pct")),
        total_funding_raised_eur=_parse_float(competitor.get("funding_raised")),
        latest_valuation_eur=_parse_float(competitor.get("valuation")),
        employee_count=competitor.get("employees") if isinstance(competitor.get("employees"), int) else None,
        profitability_raw_metrics=profitability_data,
        data_source="competitor_data.json",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        last_updated=datetime.now(timezone.utc).replace(tzinfo=None),
    )


async def load_competitor_data(json_path: str | Path, db_url: str) -> None:
    """
    Load competitor data from JSON file into PostgreSQL.

    Args:
        json_path: Path to competitor_data.json file
        db_url: Database connection URL (async SQLAlchemy format)

    Raises:
        FileNotFoundError: If JSON file not found
        ValueError: If JSON structure is invalid
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    # Load JSON data
    logger.info(f"Loading JSON from {json_path}")
    with open(json_path) as f:
        loaded = json.load(f)

    if not isinstance(loaded, dict):
        raise ValueError("JSON root must be an object")
    data = cast("dict[str, Any]", loaded)

    if "competitors" not in data:
        raise ValueError("JSON must contain 'competitors' key")

    competitors_raw = data["competitors"]
    if not isinstance(competitors_raw, list):
        raise ValueError("'competitors' must be an array")
    competitors: list[dict[str, object]] = []
    for item_obj in cast("list[object]", competitors_raw):
        if isinstance(item_obj, dict):
            competitors.append(cast("dict[str, object]", item_obj))
    logger.info(f"Found {len(competitors)} companies in JSON")

    # Create async engine and session
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        companies_to_add: list[CompanyRecord] = []

        for competitor in competitors:
            try:
                # Check if company already exists
                company_name = competitor.get("company_name")
                existing = await session.execute(select(CompanyRecord).where(CompanyRecord.name == company_name))
                existing_company = existing.scalar_one_or_none()

                if existing_company:
                    logger.info(f"Company '{company_name}' already exists, skipping")
                    continue

                company = _build_company_record(competitor)

                companies_to_add.append(company)
                logger.info(f"Prepared company: {company_name}")

            except (TypeError, ValueError, KeyError) as e:
                logger.error(f"Error processing company {competitor.get('company_name')}: {e}")
                raise

        # Add all companies at once
        session.add_all(companies_to_add)

        # Commit all changes
        await session.commit()
        logger.info("All companies committed to database")

    # Verify data integrity
    async with async_session() as session:
        result = await session.execute(select(CompanyRecord))
        companies = result.scalars().all()
        logger.info(f"Verification: {len(companies)} companies in database")

        for company in companies:
            revenue_display = getattr(company, "revenue_eur_m", None)
            logger.info(
                f"  - {company.name} ({company.headquarters}): "
                f"Revenue: {revenue_display}M EUR, "
                f"Employees: {company.employee_count}, "
                f"Classification: {company.classification}"
            )

    await engine.dispose()


async def main():
    """Main entry point for the migration script."""
    from solstein.config import get_settings

    # Get database URL from environment or use default
    settings = get_settings()
    db_url = settings.get_database_url(test=True) or "postgresql+asyncpg://solstein:solstein@localhost:5432/solstein"

    # Get JSON path
    json_path = Path(__file__).parent.parent.parent.parent / "data" / "input" / "competitor_data.json"

    logger.info(f"Starting migration: {json_path} → {db_url}")

    try:
        await load_competitor_data(json_path, db_url)
        logger.info("Migration completed successfully")
    except (FileNotFoundError, ValueError, SQLAlchemyError, OSError) as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
