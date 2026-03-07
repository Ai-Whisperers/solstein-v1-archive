#!/usr/bin/env python3
"""Seed database with test companies for development.

Usage:
    python scripts/seed_db.py --count 100
    python scripts/seed_db.py --count 1000 --with-enrichment
"""

from __future__ import annotations

import asyncio
import argparse
import random
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, "src")

from faker import Faker

from solstein.domain.models import Company, FinancialMetrics
from solstein.infrastructure.database import init_db, get_async_session
from solstein.infrastructure.repositories import CompanyRepository

fake = Faker()

INDUSTRIES = [
    "Software",
    "Healthcare",
    "Fintech",
    "E-commerce",
    "AI/ML",
    "Cybersecurity",
    "Biotech",
    "Clean Energy",
    "SaaS",
    "Marketplace",
    "Gaming",
    "EdTech",
    "PropTech",
    "LegalTech",
    "InsurTech",
]

STAGES = ["Seed", "Series A", "Series B", "Series C", "Series D+", "Growth", "Late Stage"]

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East", "Africa"]


def generate_company(company_id: int) -> Company:
    """Generate a synthetic company."""
    founded_year = random.randint(2010, 2023)
    stage = random.choice(STAGES)

    # Revenue based on stage
    stage_multipliers = {
        "Seed": (0.1, 1),
        "Series A": (1, 10),
        "Series B": (10, 50),
        "Series C": (50, 200),
        "Series D+": (200, 1000),
        "Growth": (500, 5000),
        "Late Stage": (1000, 10000),
    }
    min_rev, max_rev = stage_multipliers.get(stage, (1, 10))
    revenue = round(random.uniform(min_rev, max_rev), 2)

    return Company(
        id=f"test-company-{company_id:04d}",
        name=fake.company(),
        industry=random.choice(INDUSTRIES),
        stage=stage,
        description=fake.catch_phrase(),
        headquarters=fake.city(),
        region=random.choice(REGIONS),
        founded_year=founded_year,
        employee_count=random.randint(10, 10000),
        website=fake.url(),
        linkedin_url=f"https://linkedin.com/company/{fake.slug()}",
        revenue=revenue,
        revenue_growth=random.uniform(-0.2, 3.0),
        gross_margin=random.uniform(0.3, 0.9),
        ebitda_margin=random.uniform(-0.3, 0.5),
        funding_total=random.uniform(1, 500) if stage != "Seed" else random.uniform(0.5, 5),
        last_funding_date=datetime.now() - timedelta(days=random.randint(30, 730)),
        valuation=random.uniform(10, 10000) if stage not in ["Seed", "Series A"] else None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


async def seed_companies(count: int = 100, with_enrichment: bool = False) -> None:
    """Seed database with test companies."""
    print(f"🌱 Seeding {count} companies...")

    await init_db()

    async with get_async_session() as session:
        repo = CompanyRepository(session)

        companies = []
        for i in range(count):
            company = generate_company(i + 1)
            companies.append(company)

            # Batch insert every 100
            if len(companies) >= 100:
                for c in companies:
                    await repo.save(c)
                await session.commit()
                print(f"   ✓ Inserted {i + 1}/{count}")
                companies = []

        # Insert remaining
        if companies:
            for c in companies:
                await repo.save(c)
            await session.commit()

    print(f"✅ Seeded {count} companies successfully!")

    if with_enrichment:
        print("\n🔄 Triggering enrichment jobs...")
        # This would trigger Celery tasks in production
        print("   (Skipped in seed script - run enrichment manually)")


def main():
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of companies to create (default: 100)",
    )
    parser.add_argument(
        "--with-enrichment",
        action="store_true",
        help="Trigger enrichment after seeding",
    )

    args = parser.parse_args()

    try:
        asyncio.run(seed_companies(args.count, args.with_enrichment))
    except KeyboardInterrupt:
        print("\n\n❌ Seeding cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
