"""
Market Simulation Engine.
"""

from loguru import logger

from ...domain.models import Company
from ...domain.simulation import MarketConditionType, Scenario, SimulationResult
from ..scoring import GrowthScorer


class SimulationEngine:
    """Engine for running market simulations."""

    def __init__(self, scorer: GrowthScorer | None = None):
        self.scorer = scorer or GrowthScorer()

    def run(self, scenario: Scenario, companies: list[Company]) -> list[SimulationResult]:
        """
        Run a simulation scenario on a list of companies.

        Args:
            scenario: The scenario to simulate.
            companies: List of companies to include in the simulation.

        Returns:
            List of simulation results.
        """
        logger.info(f"Running simulation '{scenario.name}' on {len(companies)} companies")
        results = []

        for company in companies:
            result = self._simulate_company(scenario, company)
            results.append(result)

        return results

    def _simulate_company(self, scenario: Scenario, company: Company) -> SimulationResult:
        """Simulate scenario impact on a single company."""

        # 1. Base Metrics
        base_scores = self.scorer.calculate_scores(company)
        base_growth_score = base_scores.growth_score or 0.0
        base_valuation = company.financials.valuation or 0.0

        # 2. Apply Conditions
        simulated_growth_score = base_growth_score
        simulated_valuation = base_valuation
        notes = []

        for condition in scenario.conditions:
            # Check if company is in affected industry (if specified)
            if condition.affected_industries:
                if not company.industry:
                    continue
                if not any(ind.lower() in company.industry.lower() for ind in condition.affected_industries):
                    continue

            # Apply impact based on condition type
            match condition.type:
                case MarketConditionType.INTEREST_RATE:
                    # Higher interest rates -> Lower valuations for growth companies
                    # impact_factor: e.g., 1.05 for 5% rate increase
                    # Simplified logic: Valuation drops by (rate * 10)%
                    # If factor is > 1 (rate up), valuation down
                    if condition.impact_factor > 1.0:
                        drop_pct = (condition.impact_factor - 1.0) * 2.0  # Magnified impact
                        simulated_valuation *= 1.0 - drop_pct
                        notes.append(f"Valuation impacted by interest rates (-{drop_pct:.1%})")
                    else:
                        # Rates down, valuation up
                        boost_pct = (1.0 - condition.impact_factor) * 1.5
                        simulated_valuation *= 1.0 + boost_pct
                        notes.append(f"Valuation boosted by low interest rates (+{boost_pct:.1%})")

                case MarketConditionType.SECTOR_GROWTH:
                    # Sector growth directly impacts growth score
                    simulated_growth_score += condition.impact_factor
                    notes.append(f"Growth score adjusted by sector trend ({condition.impact_factor:+})")

                case MarketConditionType.COMPETITOR_ACTIVITY:
                    # High competitor activity reduces growth score
                    if condition.impact_factor > 0:
                        simulated_growth_score -= condition.impact_factor * 0.5
                        notes.append(f"Growth score reduced by competition (-{condition.impact_factor * 0.5})")

                case MarketConditionType.INFLATION:
                    # Inflation eats into profit margins (implied) -> lower valuation
                    if condition.impact_factor > 0.02:  # Normal inflation < 2%
                        impact = (condition.impact_factor - 0.02) * 5.0
                        simulated_valuation *= 1.0 - impact
                        notes.append(f"Valuation reduced by high inflation (-{impact:.1%})")

        # 3. Cap Scores
        simulated_growth_score = max(0.0, min(10.0, simulated_growth_score))

        # 4. Calculate Changes
        val_change = 0.0
        if base_valuation > 0:
            val_change = (simulated_valuation - base_valuation) / base_valuation

        growth_change = simulated_growth_score - base_growth_score

        return SimulationResult(
            company_id=company.id,
            company_name=company.name,
            base_valuation=base_valuation,
            simulated_valuation=simulated_valuation,
            valuation_change_pct=val_change,
            base_growth_score=base_growth_score,
            simulated_growth_score=simulated_growth_score,
            growth_score_change=growth_change,
            notes=notes,
        )
