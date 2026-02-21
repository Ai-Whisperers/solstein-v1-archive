"""
Temporal Workflows for Solstein Intelligence Engine.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Workflows kept for reference but are not called. Will be reimplemented with
asyncio-based task queue in Phase 2.
"""

import asyncio
from datetime import timedelta
from typing import Any

# from temporalio import workflow
# from temporalio.common import RetryPolicy


class WorkflowStub:
    """Mock-friendly stub for Temporal workflow."""

    def run(self, func):
        return func

    async def execute_activity(self, *args, **kwargs):
        pass

    @property
    def logger(self):
        import logging

        return logging.getLogger("workflow_stub")

    @property
    def RetryPolicy(self):
        return lambda **kwargs: None


workflow = WorkflowStub()
RetryPolicy = workflow.RetryPolicy

from .activities import calculate_company_score, fetch_market_company_ids


class BatchScoreMarketWorkflow:
    """Orchestrates scoring an entire market of companies concurrently.

    NOTE: Temporal integration disabled. Stubs kept for import compatibility.
    """

    async def run(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Orchestrate scoring an entire market of companies concurrently."""
        workflow.logger.info(f"Starting batch scoring with filters: {filters}")

        # 1. Fetch Company IDs
        company_ids = await workflow.execute_activity(
            fetch_market_company_ids,
            filters,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            ),
        )

        # 2. Score each company (Concurrent execution via execute_activity)
        tasks = [
            workflow.execute_activity(
                calculate_company_score,
                cid,
                start_to_close_timeout=timedelta(minutes=2),
            )
            for cid in company_ids
        ]

        results = await asyncio.gather(*tasks)

        return {
            "total_processed": len(company_ids),
            "results": results,
            "status": "success",
        }


class Worker:
    """Mock-friendly stub for Temporal Worker."""

    def __init__(self, *args, **kwargs):
        pass

    async def run(self):
        pass
