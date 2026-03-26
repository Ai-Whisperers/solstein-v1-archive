from unittest.mock import patch

import pytest

from solstein.analytics.scoring import (
    CompetitiveOverlapCalculator,
    GrowthScorer,
    MarketAnalyzer,
    classify_company,
)
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    FinancialMetric,
    ThreatLevel,
)
from solstein.exceptions import ScoringError


def make_company(**kwargs):
    fin = FinancialMetric(allow_empty_primary=True)
    base = {
        "id": "cmp-1",
        "name": "C1",
        "description": "desc",
        "industry": "Tech",
        "financials": fin,
        "ai_maturity": AIMaturity.NONE,
        "threat_level": ThreatLevel.MEDIUM,
        "tier": CompanyTier.TIER_3,
        "geographic_presence": [],
        "tech_stack": [],
        "key_customers": [],
    }
    base.update(kwargs)
    return Company(**base)


def test_classify_company_none():
    assert classify_company(None) == "Salt"


def test_growth_scorer_raises_when_subscorer_fails():
    scorer = GrowthScorer()
    company = make_company()
    with patch.object(scorer.financial_health_scorer, "score", side_effect=RuntimeError("boom")):
        with pytest.raises(ScoringError):
            scorer.calculate_scores(company)

    assert company.growth_score is None
    assert company.financial_health_score is None
    assert company.composite_score is None
    assert company.scoring_breakdown["status"] == "failed"
    assert "financial" in company.scoring_breakdown["errors"]


def test_growth_scorer_growth_score_employee_efficiency():
    scorer = GrowthScorer()
    # High efficiency
    fin = FinancialMetric(revenue=10_000_000.0, employees=10)  # 1M per emp
    company = make_company(financials=fin)
    scorer.calculate_scores(company)
    assert company.growth_score > 5.0  # Just assert it calculated

    # Med efficiency
    fin = FinancialMetric(revenue=4_000_000.0, employees=10)  # 400k per emp
    company = make_company(financials=fin)
    scorer.calculate_scores(company)


def test_growth_scorer_growth_score_funding():
    scorer = GrowthScorer()
    # High funding
    fin = FinancialMetric(funding_raised=60_000_000.0, employees=1)
    company = make_company(financials=fin)
    scorer.calculate_scores(company)


def test_financial_health_employee_efficiency():
    scorer = GrowthScorer()
    # Exceptional
    fin = FinancialMetric(revenue=20_000_000.0, employees=10)  # 2M per emp
    company = make_company(financials=fin)
    scorer.calculate_scores(company)

    # Good
    fin = FinancialMetric(revenue=7_000_000.0, employees=10)  # 700k
    company = make_company(financials=fin)
    scorer.calculate_scores(company)

    # Low
    fin = FinancialMetric(revenue=500_000.0, employees=10)  # 50k
    company = make_company(financials=fin)
    scorer.calculate_scores(company)


def test_financial_health_funding_cushion():
    scorer = GrowthScorer()
    # High ratio
    fin = FinancialMetric(revenue=1_000_000.0, funding_raised=6_000_000.0)  # > 5.0
    company = make_company(financials=fin)
    scorer.calculate_scores(company)

    # Med ratio
    fin = FinancialMetric(revenue=1_000_000.0, funding_raised=3_000_000.0)  # > 2.0
    company = make_company(financials=fin)
    scorer.calculate_scores(company)

    # Thin ratio penalty
    fin = FinancialMetric(revenue=1_000_000.0, funding_raised=100_000.0, profit_margin=2.0)  # < 0.5 and <5% margin
    company = make_company(financials=fin)
    scorer.calculate_scores(company)


def test_competitive_position_geography_and_tech():
    scorer = GrowthScorer()
    # Regional geo, diverse tech
    company = make_company(
        geographic_presence=["US", "CA", "UK", "DE"],  # > 3
        tech_stack=["Python", "React", "AWS", "Docker", "K8s", "Redis"],  # > 5
    )
    scorer.calculate_scores(company)


def test_market_analyzer_determine_trends():
    analyzer = MarketAnalyzer()
    c1 = make_company(tech_stack=["AWS Cloud"])
    trends = analyzer._determine_trends([c1])
    assert "Cloud-Native Infrastructure" in trends


def test_market_analyzer_tier_distribution():
    analyzer = MarketAnalyzer()
    c1 = make_company(tier="Tier 1")
    c2 = make_company(tier="Tier 2")
    c3 = make_company(tier="Tier 1")
    dist = analyzer._calculate_tier_distribution([c1, c2, c3])
    assert dist["Tier 1"] == 2
    assert dist["Tier 2"] == 1


def test_market_analyzer_growth_metrics():
    analyzer = MarketAnalyzer()

    # Empty
    assert analyzer._calculate_growth_metrics([])["average"] == 0.0
    assert analyzer._calculate_growth_metrics([make_company()])["average"] == 0.0

    # Even count for median, some high growth, some declining
    c1 = make_company(financials=FinancialMetric(growth_rate=30.0, employees=1))
    c2 = make_company(financials=FinancialMetric(growth_rate=-10.0, employees=1))
    c3 = make_company(financials=FinancialMetric(growth_rate=10.0, employees=1))
    c4 = make_company(financials=FinancialMetric(growth_rate=5.0, employees=1))

    metrics = analyzer._calculate_growth_metrics([c1, c2, c3, c4])
    # sorted: -10, 5, 10, 30. Median of 5 and 10 is 7.5
    assert metrics["median"] == 7.5
    assert metrics["high_growth_count"] == 1
    assert metrics["declining_count"] == 1


def test_market_analyzer_financial_metrics():
    analyzer = MarketAnalyzer()

    # Empty
    assert analyzer._calculate_financial_metrics([])["total_revenue"] == 0
    assert analyzer._calculate_financial_metrics([make_company()])["total_revenue"] == 0

    # Unprofitable vs profitable
    c1 = make_company(financials=FinancialMetric(revenue=100.0, profit_margin=10.0))
    c2 = make_company(financials=FinancialMetric(revenue=50.0, profit_margin=-5.0))
    c3 = make_company(financials=FinancialMetric(revenue=200.0, profit_margin=0.0))

    metrics = analyzer._calculate_financial_metrics([c1, c2, c3])
    assert metrics["total_revenue"] == 350.0
    assert metrics["profitable_companies"] == 1
    assert metrics["unprofitable_companies"] == 2


def test_market_analyzer_technology_metrics():
    analyzer = MarketAnalyzer()

    assert analyzer._calculate_technology_metrics([])["unique_technologies"] == 0

    c1 = make_company(ai_maturity=AIMaturity.STRONG, tech_stack=["Python", "Cloud"], saas_maturity=5)
    c2 = make_company(ai_maturity=AIMaturity.NONE, tech_stack=["Python", "Java"], saas_maturity=3)

    metrics = analyzer._calculate_technology_metrics([c1, c2])
    assert metrics["ai_adoption"]["Strong"] == 1
    assert metrics["ai_adoption"]["None"] == 1
    assert metrics["average_saas_maturity"] == 4.0
    assert metrics["unique_technologies"] == 3


def test_market_analyzer_most_common_tech():
    analyzer = MarketAnalyzer()
    c1 = make_company(tech_stack=["Python", "Cloud"])
    c2 = make_company(tech_stack=["Python", "Java"])
    common = analyzer._most_common_tech([c1, c2])
    assert common[0][0] == "Python"
    assert common[0][1] == 2


def test_market_analyzer_competitive_intensity():
    analyzer = MarketAnalyzer()

    # Empty
    assert analyzer._calculate_competitive_intensity([])["hhi"] == 0.0

    c1 = make_company(threat_level=ThreatLevel.HIGH, financials=FinancialMetric(revenue=100.0))
    c2 = make_company(threat_level=ThreatLevel.LOW, financials=FinancialMetric(revenue=100.0))

    metrics = analyzer._calculate_competitive_intensity([c1, c2])
    assert metrics["threat_distribution"]["High"] == 1
    assert metrics["direct_competitors"] == 1
    # 50% and 50% -> 2500 + 2500 = 5000
    assert metrics["hhi"] == 5000.0
    assert metrics["market_concentration"] == "Highly Concentrated"


def test_market_analyzer_interpret_hhi():
    analyzer = MarketAnalyzer()
    assert analyzer._interpret_hhi(3000) == "Highly Concentrated"
    assert analyzer._interpret_hhi(2000) == "Moderately Concentrated"
    assert analyzer._interpret_hhi(1200) == "Somewhat Concentrated"
    assert analyzer._interpret_hhi(500) == "Competitive"


def test_competitive_overlap_customer_overlap():
    calc = CompetitiveOverlapCalculator()

    # Test valid customers
    c1 = make_company(key_customers=["Bank of America", "Stripe Tech"])
    c2 = make_company(key_customers=["Stripe Corp", "Unknown"])

    overlap = calc.calculate_overlap(c1, c2)
    assert overlap > 0.0
    assert calc._calculate_customer_overlap(c1, c2) > 0.0

    # Test empty returns 0
    assert calc._calculate_customer_overlap(make_company(key_customers=[]), c2) == 0.0
    assert (
        calc._calculate_geographic_overlap(
            make_company(geographic_presence=["US"]),
            make_company(geographic_presence=[]),
        )
        == 0.0
    )
    assert calc._calculate_technology_overlap(make_company(tech_stack=["Python"]), make_company(tech_stack=[])) == 0.0
