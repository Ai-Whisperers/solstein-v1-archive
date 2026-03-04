import asyncio
from pathlib import Path

from loguru import logger
from src.solstein.data.loaders import CompetitorDataLoader
from src.solstein.data.repositories import SupabaseRepository


async def seed_data():
    """Seed companies from JSON to Supabase."""
    logger.info("Starting data seeding process...")

    # Initialize repository
    repo = SupabaseRepository()

    # Load data
    data_path = Path("data/input/competitor_data.json")
    if not data_path.exists():
        logger.error(f"Seeding source not found: {data_path}")
        return

    loader = CompetitorDataLoader(data_dir=data_path.parent)
    companies = loader.load_companies()

    logger.info(f"Loaded {len(companies)} companies from JSON. Syncing to Supabase...")

    count = 0
    for company in companies:
        try:
            repo.save(company)
            count += 1
            if count % 5 == 0:
                logger.info(f"Progress: {count}/{len(companies)} companies synced...")
        except Exception as e:
            logger.error(f"Failed to seed {company.name}: {e}")

    logger.info(f"Seeding complete. {count} companies successfully synced.")

if __name__ == "__main__":
    asyncio.run(seed_data())
