"""
Verify Simulation Engine logic.
"""

from solstein.analytics.simulation import SimulationEngine
from solstein.domain.models import Company, CompanyTier, FinancialMetric
from solstein.domain.simulation import MarketCondition, MarketConditionType, Scenario


def verify_simulation():
    print("Initializing Simulation Verification...")

    # 1. Setup Data
    company = Company(
        id="sim_test",
        name="SimTest Corp",
        tier=CompanyTier.TIER_2,
        industry="SaaS",
        financials=FinancialMetric(
            revenue=10_000_000, growth_rate=50.0, valuation=100_000_000
        ),
    )

    # 2. Define Scenario: "Tech Recession"
    # High interest rates, low sector growth
    scenario = Scenario(
        id="recession_2024",
        name="Tech Recession",
        description="High interest rates and cooling sector",
        conditions=[
            MarketCondition(
                type=MarketConditionType.INTEREST_RATE,
                name="Rate Hike",
                impact_factor=1.05,  # 5% rate -> negative impact on valuation
            ),
            MarketCondition(
                type=MarketConditionType.SECTOR_GROWTH,
                name="SaaS Cooling",
                impact_factor=-1.0,  # -1.0 to growth score
                affected_industries=["SaaS"],
            ),
        ],
    )

    # 3. Run Simulation
    engine = SimulationEngine()
    results = engine.run(scenario, [company])
    result = results[0]

    # 4. Assertions
    print(f"\nResults for {result.company_name}:")
    print(f"Base Valuation: ${result.base_valuation:,.0f}")
    print(
        f"Simulated Valuation: ${result.simulated_valuation:,.0f} "
        f"({result.valuation_change_pct:+.1%})"
    )
    print(f"Base Growth Score: {result.base_growth_score:.2f}")
    print(
        f"Simulated Growth Score: {result.simulated_growth_score:.2f} "
        f"({result.growth_score_change:+.2f})"
    )
    print("Notes:")
    for note in result.notes:
        print(f" - {note}")

    # Check Logic
    if result.simulated_valuation >= result.base_valuation:
        print("\nFAILURE: Valuation should have decreased in recession scenario.")
        exit(1)

    if result.simulated_growth_score >= result.base_growth_score:
        print("\nFAILURE: Growth score should have decreased due to cooling sector.")
        exit(1)

    print("\nSUCCESS: Simulation logic verified!")


if __name__ == "__main__":
    verify_simulation()
