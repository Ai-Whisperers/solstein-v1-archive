from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from ...analytics.simulation import SimulationEngine
from ...api.schemas import ScenarioSchema, SimulationResultSchema
from ...core.repositories import CompanyFilter, CompanyRepository
from ...domain.simulation import MarketCondition, MarketConditionType, Scenario
from ..dependencies import get_current_user, get_repository

router = APIRouter(tags=["Simulation"])
simulation_engine = SimulationEngine()


@router.post("/run", response_model=list[SimulationResultSchema])
async def run_simulation(
    scenario_input: ScenarioSchema,
    industry: str | None = Query(None, description="Filter companies by industry"),
    _: dict[str, Any] = Depends(get_current_user),
    repo: CompanyRepository = Depends(get_repository),
) -> list[SimulationResultSchema]:
    """Run a market simulation scenario."""
    try:
        # 1. Convert Schema to Domain Entity
        conditions = []
        for c in scenario_input.conditions:
            try:
                cond_type = MarketConditionType(c.type)
            except ValueError:
                # Skip invalid types or handle error
                continue

            conditions.append(
                MarketCondition(
                    type=cond_type,
                    name=c.name,
                    impact_factor=c.impact_factor,
                    description=c.description,
                    affected_industries=c.affected_industries or [],
                )
            )

        scenario = Scenario(
            id=scenario_input.id,
            name=scenario_input.name,
            description=scenario_input.description,
            conditions=conditions,
        )

        # 2. Get Companies
        filters = CompanyFilter(industry=industry)
        companies = repo.get_all(filters=filters)

        if not companies:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No companies found to simulate",
            )

        # 3. Run Simulation
        results = simulation_engine.run(scenario, companies)

        # 4. Map to Schema
        return [
            SimulationResultSchema(
                company_id=r.company_id,
                company_name=r.company_name,
                base_valuation=r.base_valuation or 0.0,
                simulated_valuation=r.simulated_valuation or 0.0,
                valuation_change_pct=r.valuation_change_pct,
                base_growth_score=r.base_growth_score,
                simulated_growth_score=r.simulated_growth_score,
                growth_score_change=r.growth_score_change,
                notes=r.notes,
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running simulation: {str(e)}",
        ) from e
