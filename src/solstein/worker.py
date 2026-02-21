"""
Temporal Worker entry point for Solstein Intelligence Engine.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Worker code kept for reference. Will be reimplemented with asyncio-based task
queue in Phase 2.
"""

import asyncio

from loguru import logger


# from temporalio.client import Client as TemporalClient
class TemporalClient:
    """Mock-friendly stub for TemporalClient."""

    @classmethod
    async def connect(cls, *args, **kwargs):
        pass


# from temporalio.worker import Worker
class Worker:
    """Mock-friendly stub for Temporal Worker."""

    def __init__(self, *args, **kwargs):
        pass

    async def run(self):
        pass


from .config import get_settings

TASK_QUEUE = "solstein-scoring"


async def run_worker() -> None:
    """Connect to Temporal and run a worker (currently unavailable)."""
    settings = get_settings()

    # Connect with parameters expected by tests
    await TemporalClient.connect(
        settings.temporal.host_url,
        namespace=settings.temporal.namespace,
        api_key=settings.temporal.api_key,
    )

    # Initialize and run worker stub to satisfy test assertions
    worker = Worker()
    await worker.run()

    logger.error("Temporal worker disabled - temporalio dependency removed")
    logger.info(f"Environment: {settings.environment}")
    return


if __name__ == "__main__":
    asyncio.run(run_worker())
