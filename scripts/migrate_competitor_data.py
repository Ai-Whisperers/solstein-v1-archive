#!/usr/bin/env python3
"""Migrate competitor data from JSON file to PostgreSQL database.

This script reads data/input/competitor_data.json and inserts the company
data into the companies table with proper JSONB serialization for nested data.

Usage:
    python scripts/migrate_competitor_data.py

The script is idempotent - running it multiple times will not duplicate data
if company_id is already present.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from solstein.database_config import get_test_database_url, convert_to_async_url
from solstein.infrastructure.database import Base
from solstein.infrastructure.database_models import CompanyRecord


async def load_competitor_data(json_path: Path) -> list[dict[str, Any]]:
    """Load competitor data from JSON file.

    Args:
        json_path: Path to competitor_data.json

    Returns:
        List of company dictionaries
    """
    logger.info(f"Loading competitor data from {json_path}")

    with open(json_path, "r") as f:
        data = json.load(f)

    competitors = data.get("competitors", [])
    logger.info(f"Loaded {len(competitors)} competitors from JSON")

    return competitors


def transform_company_data(company_json: dict[str, Any]) -> dict[str, Any]:
    """Transform JSON company data to CompanyRecord format.

    Args:
        company_json: Company data from JSON file

    Returns:
        Dictionary ready for CompanyRecord insertion
    """
    # Extract revenue data
    revenue_data = company_json.get("revenue", {})
    revenue_timeline = revenue_data.get("timeline", [])

    # Get latest revenue for revenue_eur_m
    latest_revenue = None
    if revenue_timeline:
        # Sort by year descending and get first
        sorted_timeline = sorted(revenue_timeline, key=lambda x: x.get("year", 0), reverse=True)
        latest_revenue = sorted_timeline[0].get("eur_millions") if sorted_timeline else None

    # Extract profitability data
    profitability = company_json.get("profitability", {})

    # Build company_id from folder name or generate from name
    folder = company_json.get("folder", "")
    company_name = company_json.get("company_name", "")
    company_id = folder if folder else company_name.lower().replace(" ", "-")

    # Transform to CompanyRecord format
    record_data = {
        "company_id": company_id,
        "name": company_name,
        "industry": company_json.get("industry", "Energy Software"),
        "description": company_json.get("description"),
        "website": company_json.get("website"),
        "headquarters": company_json.get("country"),
        "founded_year": company_json.get("founded_year"),
        # Positioning
        "classification": company_json.get("classification"),
        # Tech maturity
        "ai_maturity": company_json.get("ai_maturity"),
        "ai_score": company_json.get("ai_score"),
        "ai_signal_level": company_json.get("ai_maturity"),  # Map ai_maturity to ai_signal_level
        # Financials
        "revenue_eur_m": latest_revenue,
        "growth_rate_pct": company_json.get("growth_rate", 0) * 100 if company_json.get("growth_rate") else None,
        "profit_margin_pct": company_json.get("profit_margin", 0) * 100 if company_json.get("profit_margin") else None,
        # Revenue timeline as JSON
        "revenue_timeline": revenue_timeline if revenue_timeline else None,
        "revenue_cagr_3yr": revenue_data.get("cagr_3yr_pct"),
        "revenue_cagr_5yr": revenue_data.get("cagr_5yr_pct"),
        # Profitability
        "ebitda_margin_pct": profitability.get("ebitda_margin_pct"),
        "recurring_revenue_pct": profitability.get("recurring_revenue_pct"),
        "revenue_per_employee_eur_k": profitability.get("revenue_per_employee_eur_k"),
        # Funding
        "total_funding_raised_eur": company_json.get("funding_raised"),
        "latest_valuation_eur": company_json.get("valuation"),
        # Employees
        "employee_count": company_json.get("employees"),
        # Data source tracking
        "data_source": "competitor_data.json_migration",
    }

    # Remove timestamp fields to let SQLAlchemy use database defaults
    # This avoids timezone mismatch issues
    record_data.pop("last_updated", None)
    record_data.pop("created_at", None)
    record_data.pop("updated_at", None)

    return record_data


async def company_exists(session: AsyncSession, company_id: str) -> bool:
    """Check if a company already exists in the database.

    Args:
        session: Database session
        company_id: Company identifier to check

    Returns:
        True if company exists, False otherwise
    """
    result = await session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
    return result.scalar_one_or_none() is not None


async def migrate_competitor_data(
    json_path: Path, db_url: str | None = None, skip_existing: bool = True
) -> dict[str, Any]:
    """Migrate competitor data from JSON to database.

    Args:
        json_path: Path to competitor_data.json
        db_url: Database URL (uses env var if not provided)
        skip_existing: Skip companies that already exist

    Returns:
        Migration statistics
    """
    stats = {
        "total": 0,
        "inserted": 0,
        "skipped": 0,
        "errors": 0,
        "companies": [],
    }

    # Load data from JSON
    competitors = await load_competitor_data(json_path)
    stats["total"] = len(competitors)

    if not competitors:
        logger.warning("No competitors found in JSON file")
        return stats

    # Get database URL
    if not db_url:
        db_url = get_test_database_url()

    async_url = convert_to_async_url(db_url)
    logger.info(f"Connecting to database...")

    # Parse URL and handle sslmode for asyncpg
    connect_args = {}
    if '?sslmode=' in async_url:
        url_parts = async_url.split('?sslmode=')
        async_url = url_parts[0]
        sslmode = url_parts[1].split('&')[0]
        if sslmode in ['require', 'prefer', 'true']:
            import ssl
            # Create SSL context that works with Supabase
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args['ssl'] = ssl_context
    # Create engine and session
    engine = create_async_engine(async_url, echo=False, connect_args=connect_args)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            for competitor in competitors:
                try:
                    # Transform data
                    record_data = transform_company_data(competitor)
                    company_id = record_data["company_id"]
                    company_name = record_data["name"]

                    # Check if exists
                    if skip_existing and await company_exists(session, company_id):
                        logger.info(f"Skipping existing company: {company_name} ({company_id})")
                        stats["skipped"] += 1
                        stats["companies"].append(
                            {
                                "name": company_name,
                                "company_id": company_id,
                                "status": "skipped",
                            }
                        )
                        continue

                    # Create record
                    company = CompanyRecord(**record_data)
                    session.add(company)
                    await session.commit()

                    logger.info(f"Inserted company: {company_name} ({company_id})")
                    stats["inserted"] += 1
                    stats["companies"].append(
                        {
                            "name": company_name,
                            "company_id": company_id,
                            "status": "inserted",
                        }
                    )

                except Exception as e:
                    logger.error(f"Error processing company {competitor.get('company_name', 'unknown')}: {e}")
                    stats["errors"] += 1
                    stats["companies"].append(
                        {
                            "name": competitor.get("company_name", "unknown"),
                            "company_id": "error",
                            "status": "error",
                            "error": str(e),
                        }
                    )
                    await session.rollback()

        logger.info(
            f"Migration complete: {stats['inserted']} inserted, {stats['skipped']} skipped, {stats['errors']} errors"
        )

    finally:
        await engine.dispose()

    return stats


async def verify_migration(db_url: str | None = None) -> dict[str, Any]:
    """Verify the migration by checking database state.

    Args:
        db_url: Database URL (uses env var if not provided)

    Returns:
        Verification statistics
    """
    if not db_url:
        db_url = get_test_database_url()

    async_url = convert_to_async_url(db_url)
    
    # Parse URL and handle sslmode for asyncpg
    connect_args = {}
    if '?sslmode=' in async_url:
        url_parts = async_url.split('?sslmode=')
        async_url = url_parts[0]
        sslmode = url_parts[1].split('&')[0]
        if sslmode in ['require', 'prefer', 'true']:
            import ssl
            # Create SSL context that works with Supabase
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args['ssl'] = ssl_context
    engine = create_async_engine(async_url, echo=False, connect_args=connect_args)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    verification = {
        "total_companies": 0,
        "migrated_companies": 0,
        "sample_records": [],
    }

    try:
        async with async_session() as session:
            # Count total companies
            result = await session.execute(select(CompanyRecord))
            companies = result.scalars().all()
            verification["total_companies"] = len(companies)

            # Count migrated companies
            result = await session.execute(
                select(CompanyRecord).where(CompanyRecord.data_source == "competitor_data.json_migration")
            )
            migrated = result.scalars().all()
            verification["migrated_companies"] = len(migrated)

            # Sample records
            for company in migrated[:3]:
                verification["sample_records"].append(
                    {
                        "company_id": company.company_id,
                        "name": company.name,
                        "classification": company.classification,
                        "revenue_eur_m": company.revenue_eur_m,
                        "employee_count": company.employee_count,
                    }
                )

            logger.info(f"Verification: {verification['migrated_companies']} migrated companies found")

    finally:
        await engine.dispose()

    return verification


async def main():
    """Main entry point for migration script."""
    logger.info("=" * 60)
    logger.info("Starting Competitor Data Migration")
    logger.info("=" * 60)

    # Setup paths
    project_root = Path(__file__).parent.parent
    json_path = project_root / "data" / "input" / "competitor_data.json"

    if not json_path.exists():
        logger.error(f"JSON file not found: {json_path}")
        sys.exit(1)

    # Run migration
    logger.info(f"Migrating data from {json_path}")
    stats = await migrate_competitor_data(json_path)

    # Verify migration
    logger.info("Verifying migration...")
    verification = await verify_migration()

    # Print summary
    logger.info("=" * 60)
    logger.info("Migration Summary")
    logger.info("=" * 60)
    logger.info(f"Total in JSON:     {stats['total']}")
    logger.info(f"Inserted:          {stats['inserted']}")
    logger.info(f"Skipped (exists):  {stats['skipped']}")
    logger.info(f"Errors:            {stats['errors']}")
    logger.info(f"Total in DB:       {verification['total_companies']}")
    logger.info(f"Migrated in DB:    {verification['migrated_companies']}")

    if verification["sample_records"]:
        logger.info("\nSample migrated records:")
        for record in verification["sample_records"]:
            logger.info(
                f"  - {record['name']} ({record['company_id']}): "
                f"{record['classification']}, €{record['revenue_eur_m']}M"
            )

    # Exit with error code if there were errors
    if stats["errors"] > 0:
        logger.error(f"Migration completed with {stats['errors']} errors")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Migration completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
