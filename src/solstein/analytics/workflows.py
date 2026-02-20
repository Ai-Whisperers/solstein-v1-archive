"""
Temporal Workflows for Solstein Intelligence Engine.
These define the orchestrated sequence of activities.
"""

from datetime import timedelta
from typing import Any
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from .activities import calculate_company_score, fetch_market_company_ids

@workflow.defn
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
                retry_policy=workflow.RetryPolicy(
                    maximum_attempts=3
                )
            )
            results.append(res)
            
        return {
            "total_processed": len(results),
            "results": results,
            "status": "success"
        }
