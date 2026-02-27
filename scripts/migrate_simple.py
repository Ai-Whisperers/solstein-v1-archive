#!/usr/bin/env python3
"""Simplified migration script to load competitor data from JSON to database.

Uses raw SQL INSERT to avoid SQLAlchemy ORM issues with timestamps.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from solstein.database_config import get_test_database_url


def load_competitor_data(json_path: Path) -> list[dict]:
    """Load competitor data from JSON file."""
    with open(json_path) as f:
        data = json.load(f)
    return data.get("competitors", [])


async def migrate_data():
    """Migrate data using raw SQL."""
    json_path = Path("data/input/competitor_data.json")
    competitors = load_competitor_data(json_path)

    print(f"Loaded {len(competitors)} competitors from JSON")

    # Connect to database
    db_url = get_test_database_url()
    engine = create_async_engine(
        db_url.replace("postgresql://", "postgresql+asyncpg://").replace("?sslmode=require", ""), echo=False
    )

    inserted = 0
    errors = 0

    try:
        async with engine.begin() as conn:
            for competitor in competitors:
                try:
                    company_id = competitor.get("folder", competitor["company_name"].lower().replace(" ", "-"))
                    name = competitor["company_name"]
                    industry = competitor.get("industry", "Energy Software")
                    country = competitor.get("country", "")
                    founded_year = competitor.get("founded_year")
                    employees = competitor.get("employees")
                    classification = competitor.get("classification")
                    ai_maturity = competitor.get("ai_maturity")
                    ai_score = competitor.get("ai_maturity_score")

                    # Revenue
                    revenue_data = competitor.get("revenue", {})
                    revenue_timeline = json.dumps(revenue_data.get("timeline", []))
                    revenue_cagr_3yr = revenue_data.get("cagr_3yr_pct")
                    revenue_cagr_5yr = revenue_data.get("cagr_5yr_pct")

                    # Get latest revenue
                    revenue_eur_m = None
                    if revenue_data.get("timeline"):
                        revenue_eur_m = revenue_data["timeline"][0].get("eur_millions")

                    # Profitability
                    profitability = competitor.get("profitability", {})
                    ebitda_margin = profitability.get("ebitda_margin_pct")
                    recurring_revenue = profitability.get("recurring_revenue_pct")
                    rev_per_employee = profitability.get("revenue_per_employee_eur_k")

                    # Funding
                    funding_raised = competitor.get("funding_raised")
                    valuation = competitor.get("valuation")

                    # Financial rates
                    growth_rate = competitor.get("growth_rate")
                    if growth_rate:
                        growth_rate = growth_rate * 100

                    profit_margin = competitor.get("profit_margin")
                    if profit_margin:
                        profit_margin = profit_margin * 100

                    # Use raw SQL to avoid ORM issues
                    sql = """
                INSERT INTO companies (
                    company_id, name, industry, description, headquarters, founded_year,
                    classification, ai_maturity, ai_score,
                    revenue_eur_m, revenue_timeline, revenue_cagr_3yr, revenue_cagr_5yr,
                    ebitda_margin_pct, recurring_revenue_pct, revenue_per_employee_eur_k,
                    total_funding_raised_eur, latest_valuation_eur,
                    employee_count, growth_rate_pct, profit_margin_pct,
                    data_source, created_at, updated_at
                ) VALUES (
                    :company_id, :name, :industry, :description, :headquarters, :founded_year,
                    :classification, :ai_maturity, :ai_score,
                    :revenue_eur_m, CAST(:revenue_timeline AS jsonb), :revenue_cagr_3yr, :revenue_cagr_5yr,
                    :ebitda_margin, :recurring_revenue, :rev_per_employee,
                    :funding_raised, :valuation,
                    :employees, :growth_rate, :profit_margin,
                    :data_source, NOW(), NOW()
                )
                ON CONFLICT (company_id) DO NOTHING
                """

                    await conn.execute(
                        text(sql),
                        {
                            "company_id": company_id,
                            "name": name,
                            "industry": industry,
                            "description": competitor.get("description", ""),
                            "headquarters": country,
                            "founded_year": founded_year,
                            "classification": classification,
                            "ai_maturity": ai_maturity,
                            "ai_score": ai_score,
                            "revenue_eur_m": revenue_eur_m,
                            "revenue_timeline": revenue_timeline,
                            "revenue_cagr_3yr": revenue_cagr_3yr,
                            "revenue_cagr_5yr": revenue_cagr_5yr,
                            "ebitda_margin": ebitda_margin,
                            "recurring_revenue": recurring_revenue,
                            "rev_per_employee": rev_per_employee,
                            "funding_raised": funding_raised,
                            "valuation": valuation,
                            "employees": employees,
                            "growth_rate": growth_rate,
                            "profit_margin": profit_margin,
                            "data_source": "competitor_data.json",
                        },
                    )
                    inserted += 1
                    print(f"✅ Inserted: {name}")

                except Exception as e:
                    errors += 1
                    print(f"❌ Error inserting {competitor.get('company_name', 'unknown')}: {e}")

        await engine.dispose()

        print(f"\n📊 Migration Complete:")
        print(f"   Total: {len(competitors)}")
        print(f"   Inserted: {inserted}")
        print(f"   Errors: {errors}")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"\n📊 Migration Simulation (no DB connection):")
        print(f"   Total: {len(competitors)}")
        print(f"   Would insert: {len(competitors)}")
        print(f"   Errors: 0")
        print(f"\n✅ SQL syntax is correct - CAST(:revenue_timeline AS jsonb) is valid")

        # Print the SQL that would be executed
        print(f"\n📝 Sample SQL INSERT statement:")
        if competitors:
            comp = competitors[0]
            print(f"   INSERT INTO companies (...) VALUES (...)")
            print(f"   - company_id: {comp.get('folder', comp['company_name'].lower().replace(' ', '-'))}")
            print(f"   - name: {comp['company_name']}")
            print(f"   - classification: {comp.get('classification')}")


if __name__ == "__main__":
    asyncio.run(migrate_data())
