from typing import Any

from fastapi import APIRouter, Depends, Query, status
from loguru import logger

from ...analytics.simulation import SimulationEngine
from ...core.repositories import CompanyFilter
from ...domain.simulation import Scenario, SimulationResult
from ..dependencies import get_company_repository, get_current_tenant
from ..exceptions import APIError

router = APIRouter(tags=["Simulation"])
simulation_engine = SimulationEngine()


@router.post("/run", response_model=list[SimulationResult])
async def run_simulation(
    scenario_input: Scenario,
    industry: str | None = Query(None, description="Filter companies by industry"),
    _: dict[str, Any] = Depends(get_current_tenant),
    repo: Any = Depends(get_company_repository),
) -> list[SimulationResult]:
    """Run a market simulation scenario."""
    try:
        # 1. Get Companies
        filters = CompanyFilter(industry=industry)
        companies = await repo.get_all_filtered(industry=filters.industry, skip=0, limit=1000)

        if not companies:
            raise APIError(
                code="NOT_FOUND",
                message="No companies found to simulate",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 3. Run Simulation
        results = simulation_engine.run(scenario_input, companies)

        return results

    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error running simulation",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e
