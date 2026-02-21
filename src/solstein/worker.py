"""
Temporal Worker entry point for Solstein Intelligence Engine.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Worker code kept for reference. Will be reimplemented with asyncio-based task
queue in Phase 2.
"""

import asyncio

from loguru import logger

# from temporalio.client import Client as TemporalClient
# from temporalio.worker import Worker
from .analytics.activities import calculate_company_score, fetch_market_company_ids
from .analytics.workflows import BatchScoreMarketWorkflow
from .config import get_settings

TASK_QUEUE = "solstein-scoring"


async def run_worker() -> None:
    """Connect to Temporal and run a worker (currently unavailable)."""
    logger.error("Temporal worker disabled - temporalio dependency removed")
    logger.info("Temporal integration will be reimplemented in Phase 2")
    raise RuntimeError(
        "Temporal worker is currently disabled. It will be reimplemented "
        "with an asyncio-based task queue in Phase 2."
    )


if __name__ == "__main__":
    asyncio.run(run_worker())
