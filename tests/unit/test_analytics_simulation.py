"""
Unit tests for Market Simulation Engine.
"""

import pytest

from solstein.analytics.simulation import SimulationEngine
from solstein.domain.models import Company, FinancialMetric
from solstein.domain.simulation import MarketCondition, MarketConditionType, Scenario

@pytest.fixture
def sample_company():
    return Company(
        id="c1",
        name="Tech Innovator",
        industry="Technology Software",
        financials=FinancialMetric(
            revenue=10.0,
            valuation=100.0,
            growth_rate=25.0
        )
    )

def test_simulation_engine_interest_rates_up(sample_company):
    engine = SimulationEngine()
    
    scenario = Scenario(
        id="s1",
        name="High Rates",
        description="Interest rates go up 5%",
        conditions=[
            MarketCondition(
                type=MarketConditionType.INTEREST_RATE,
                name="Rate Hike",
                impact_factor=1.05,
                affected_industries=["Technology"]
            )
        ]
    )
    
    results = engine.run(scenario, [sample_company])
    
    assert len(results) == 1
    res = results[0]
    assert res.company_id == "c1"
    
    # 1.05 factor -> 0.05 increase -> 2.0 multiplier = 0.1 drop = 10% drop
    # Valuation 100.0 * 0.9 = 90.0
    assert res.simulated_valuation == pytest.approx(90.0)
    assert res.valuation_change_pct == pytest.approx(-0.1)

def test_simulation_engine_interest_rates_down(sample_company):
    engine = SimulationEngine()
    
    scenario = Scenario(
        id="s2",
        name="Low Rates",
        description="Interest rates go down 5%",
        conditions=[
            MarketCondition(
                type=MarketConditionType.INTEREST_RATE,
                name="Rate Cut",
                impact_factor=0.95,
                affected_industries=[]
            )
        ]
    )
    
    results = engine.run(scenario, [sample_company])
    res = results[0]
    
    # 0.95 -> 0.05 drop -> 1.5 multiplier = 0.075 boost = 7.5% boost
    # Valuation 100.0 * 1.075 = 107.5
    assert res.simulated_valuation == pytest.approx(107.5)
    assert res.valuation_change_pct == pytest.approx(0.075)

def test_simulation_sector_growth(sample_company):
    engine = SimulationEngine()
    scenario = Scenario(
        id="s3",
        name="Growth Spurt",
        description="",
        conditions=[
            MarketCondition(
                type=MarketConditionType.SECTOR_GROWTH,
                name="SaaS Boom",
                impact_factor=2.0
            )
        ]
    )
    results = engine.run(scenario, [sample_company])
    res = results[0]
    
    assert res.simulated_growth_score > res.base_growth_score
    assert res.growth_score_change == pytest.approx(2.0)

def test_simulation_inflation(sample_company):
    engine = SimulationEngine()
    scenario = Scenario(
        id="s4",
        name="Hyperinflation",
        description="",
        conditions=[
            MarketCondition(
                type=MarketConditionType.INFLATION,
                name="Inflation Surge",
                impact_factor=0.08  # 8%
            )
        ]
    )
    results = engine.run(scenario, [sample_company])
    res = results[0]
    
    # 0.08 - 0.02 = 0.06 * 5.0 = 0.3 impact = 30% drop
    # 100.0 * 0.7 = 70.0
    assert res.simulated_valuation == pytest.approx(70.0)
    assert res.valuation_change_pct == pytest.approx(-0.3)

def test_simulation_competitor_activity(sample_company):
    engine = SimulationEngine()
    scenario = Scenario(
        id="s5",
        name="Competition",
        description="",
        conditions=[
            MarketCondition(
                type=MarketConditionType.COMPETITOR_ACTIVITY,
                name="New Entrants",
                impact_factor=3.0
            )
        ]
    )
    results = engine.run(scenario, [sample_company])
    res = results[0]
    
    # Growth score drops by 3.0 * 0.5 = 1.5
    assert res.growth_score_change == pytest.approx(-1.5)

def test_simulation_ignores_unaffected_industry(sample_company):
    engine = SimulationEngine()
    scenario = Scenario(
        id="s6",
        name="Energy Shock",
        description="",
        conditions=[
            MarketCondition(
                type=MarketConditionType.SECTOR_GROWTH,
                name="Energy Boom",
                impact_factor=5.0,
                affected_industries=["Energy", "Oil"]
            )
        ]
    )
    results = engine.run(scenario, [sample_company])
    res = results[0]
    
    # No change expected since company is 'Technology Software'
    assert res.growth_score_change == 0.0
