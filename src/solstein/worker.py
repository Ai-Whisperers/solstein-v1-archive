"""
Temporal Worker entry point for Solstein Intelligence Engine.

Run this to start the worker that listens for and executes scoring workflows.
Usage: python -m solstein.worker
"""

import asyncio
from temporalio.client import Client as TemporalClient
from temporalio.worker import Worker
from loguru import logger

from .config import get_settings
from .analytics.activities import calculate_company_score, fetch_market_company_ids
from .analytics.workflows import BatchScoreMarketWorkflow

TASK_QUEUE = "solstein-scoring"


async def run_worker() -> None:
    """Connect to Temporal and run a worker."""
    settings = get_settings()

    logger.info(f"Connecting Temporal worker to {settings.temporal.host_url}")
    client = await TemporalClient.connect(
        settings.temporal.host_url,
        namespace=settings.temporal.namespace,
        api_key=settings.temporal.api_key,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[BatchScoreMarketWorkflow],
        activities=[calculate_company_score, fetch_market_company_ids],
    )

    logger.info(f"Temporal worker listening on queue '{TASK_QUEUE}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
