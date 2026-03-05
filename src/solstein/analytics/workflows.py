import importlib
from typing import Any

try:
    workflow = importlib.import_module("temporalio.workflow")
except Exception:

    class _WorkflowStub:
        class RetryPolicy:
            pass

        async def execute_activity(self, *args, **kwargs):
            raise RuntimeError("Temporal workflow is unavailable")

        class _Logger:
            def info(self, *args, **kwargs):
                pass

        logger = _Logger()

    workflow = _WorkflowStub()

from .activities import calculate_company_score, fetch_market_company_ids


class BatchScoreMarketWorkflow:
    async def run(self, filters: dict[str, Any]) -> dict[str, Any]:
        company_ids = await workflow.execute_activity(fetch_market_company_ids, filters)
        results = []
        for company_id in company_ids:
            score = await workflow.execute_activity(calculate_company_score, company_id)
            results.append(score)
        return {
            "status": "success",
            "total_processed": len(results),
            "results": results,
        }
