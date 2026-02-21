from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.simulation import SimulationEngine
from ...core.repositories import CompanyFilter, CompanyRepository
from ...domain.simulation import Scenario, SimulationResult
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Simulation"])
simulation_engine = SimulationEngine()


@router.post("/run", response_model=list[SimulationResult])
async def run_simulation(
    scenario_input: Scenario,
    industry: str | None = Query(None, description="Filter companies by industry"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> list[SimulationResult]:
    """Run a market simulation scenario."""
    try:
        # 1. Get Companies
        filters = CompanyFilter(industry=industry)
        companies = repo.get_all(filters=filters)

        if not companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No companies found to simulate",
            )

        # 3. Run Simulation
        results = simulation_engine.run(scenario_input, companies)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running simulation: {str(e)}",
        ) from e
