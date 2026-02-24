import asyncio

from loguru import logger

from solstein.analytics.scoring import GrowthScorer
from solstein.data.loaders import CompetitorDataLoader
from solstein.data.repositories import SupabaseRepository


async def seed_supabase() -> None:
    """Seed Supabase with data from JSON files."""
    logger.info("Starting Supabase seeding process...")

    # Initialize components
    loader = CompetitorDataLoader()
    repo = SupabaseRepository()
    scorer = GrowthScorer()

    try:
        # Load companies from JSON
        companies = loader.load_companies()
        logger.info(f"Found {len(companies)} companies in JSON source.")

        for i, company in enumerate(companies):
            logger.info(f"Processing company {i + 1}/{len(companies)}: {company.name}")

            # Re-calculate scores to ensure they are fresh and include composite score
            scored_company = scorer.calculate_scores(company)

            # Save to Supabase
            repo.save(scored_company)

        logger.info("Seeding completed successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_supabase())
