"""
Temporal Workflows for Solstein Intelligence Engine.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Workflows kept for reference but are not called. Will be reimplemented with
asyncio-based task queue in Phase 2.
"""

from datetime import timedelta
from typing import Any

# from temporalio import workflow
# from temporalio.common import RetryPolicy
from .activities import calculate_company_score, fetch_market_company_ids


class BatchScoreMarketWorkflow:
    """Orchestrates scoring an entire market of companies concurrently."""

    @workflow.run
    async def run(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Workflow entrypoint."""
        workflow.logger.info("Starting BatchScoreMarketWorkflow")

        # 1. Get the list of companies to score
        company_ids = await workflow.execute_activity(
            fetch_market_company_ids,
            filters,
            schedule_to_close_timeout=timedelta(minutes=1),
        )

        workflow.logger.info(f"Preparing to score {len(company_ids)} companies.")

        # 2. Score them concurrently
        results = []
        for cid in company_ids:
            # We could use asyncio.gather for true concurrency in the workflow,
            # but sequential is safer for the demo to avoid overloading the DB
            res = await workflow.execute_activity(
                calculate_company_score,
                cid,
                schedule_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            results.append(res)

        return {
            "total_processed": len(results),
            "results": results,
            "status": "success",
        }
