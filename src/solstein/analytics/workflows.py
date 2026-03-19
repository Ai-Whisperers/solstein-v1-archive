import logging
import importlib
from typing import Any

logger = logging.getLogger(__name__)

try:
    workflow = importlib.import_module("temporalio.workflow")
except Exception as error:
    logger.warning("Temporal workflow import failed; using local stub: %s", error)

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

try:
    from temporalio import workflow as _temporal_workflow
    _workflow_defn = _temporal_workflow.defn
    _workflow_run = _temporal_workflow.run
except ImportError:
    # No-op decorators when Temporal is unavailable
    def _workflow_defn(cls):
        return cls
    def _workflow_run(fn):
        return fn


@_workflow_defn
class BatchScoreMarketWorkflow:
    @_workflow_run
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
