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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from solstein.infrastructure.database_models import CompanyRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        data = json.load(f)

    if "competitors" not in data:
        raise ValueError("JSON must contain 'competitors' key")

    competitors = data["competitors"]
    logger.info(f"Found {len(competitors)} companies in JSON")

    # Create async engine and session
    engine = create_async_engine(db_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        companies_to_add = []

        for competitor in competitors:
            try:
                # Check if company already exists
                company_name = competitor.get("company_name")
                existing = await session.execute(select(CompanyRecord).where(CompanyRecord.name == company_name))
                existing_company = existing.scalar_one_or_none()

                if existing_company:
                    logger.info(f"Company '{company_name}' already exists, skipping")
                    continue

                # Create company record
                company = CompanyRecord(
                    company_id=str(uuid.uuid4()),
                    name=company_name,
                    industry=competitor.get("industry", "Energy Software"),
                    description=competitor.get("description"),
                    website=competitor.get("website"),
                    headquarters=competitor.get("country"),
                    founded_year=competitor.get("founded_year"),
                    # Positioning
                    classification=competitor.get("classification"),
                    # Tech maturity
                    ai_maturity=competitor.get("ai_maturity"),
                    ai_score=int(competitor.get("ai_score", 0)) if competitor.get("ai_score") else None,
                    # Financials (latest)
                    revenue_eur_m=competitor.get("revenue", {}).get("timeline", [{}])[-1].get("eur_millions"),
                    growth_rate_pct=competitor.get("growth_rate"),
                    profit_margin_pct=competitor.get("profit_margin"),
                    ebitda_margin_pct=competitor.get("profitability", {}).get("ebitda_margin_pct"),
                    recurring_revenue_pct=competitor.get("profitability", {}).get("recurring_revenue_pct"),
                    revenue_per_employee_eur_k=competitor.get("profitability", {}).get("revenue_per_employee_eur_k"),
                    # Revenue timeline
                    revenue_timeline=competitor.get("revenue", {}).get("timeline"),
                    revenue_cagr_3yr=competitor.get("revenue", {}).get("cagr_3yr_pct"),
                    revenue_cagr_5yr=competitor.get("revenue", {}).get("cagr_5yr_pct"),
                    # Funding
                    total_funding_raised_eur=competitor.get("funding_raised"),
                    latest_valuation_eur=competitor.get("valuation"),
                    # Employees
                    employee_count=competitor.get("employees"),
                    # Raw profitability metrics
                    profitability_raw_metrics=competitor.get("profitability"),
                    # Data quality
                    data_source="competitor_data.json",
                    # Metadata
                    created_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    last_updated=datetime.now(timezone.utc).replace(tzinfo=None),
                )

                companies_to_add.append(company)
                logger.info(f"Prepared company: {company_name}")

            except Exception as e:
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
            logger.info(
                f"  - {company.name} ({company.country}): "
                f"Revenue: {company.revenue_eur_m}M EUR, "
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
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
