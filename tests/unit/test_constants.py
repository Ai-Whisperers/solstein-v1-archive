"""Tests for solstein constants module."""

import pytest
from solstein.constants import (
    ScoringWeights,
    Thresholds,
    Classification,
    CompanyTier,
    ThreatLevel,
    REVENUE_PER_EMPLOYEE_EXCEPTIONAL,
    GROWTH_RATE_EXCEPTIONAL,
    AI_EXCEPTIONAL,
)


class TestScoringWeights:
    def test_growth_weight(self):
        assert ScoringWeights.GROWTH.value == 0.4

    def test_financial_health_weight(self):
        assert ScoringWeights.FINANCIAL_HEALTH.value == 0.3

    def test_competitive_position_weight(self):
        assert ScoringWeights.COMPETITIVE_POSITION.value == 0.3

    def test_weights_sum_to_one(self):
        total = (
            ScoringWeights.GROWTH.value
            + ScoringWeights.FINANCIAL_HEALTH.value
            + ScoringWeights.COMPETITIVE_POSITION.value
        )
        assert total == 1.0


class TestThresholds:
    def test_revenue_per_employee_exceptional(self):
        assert Thresholds.REVENUE_PER_EMPLOYEE_EXCEPTIONAL.value == 250

    def test_growth_rate_exceptional(self):
        assert Thresholds.GROWTH_RATE_EXCEPTIONAL.value == 30


class TestClassification:
    def test_rocket(self):
        assert Classification.ROCKET.value == "Rocket"

    def test_riser(self):
        assert Classification.RISER.value == "Riser"

    def test_steady(self):
        assert Classification.STEADY.value == "Steady"

    def test_dinosaur(self):
        assert Classification.DINOSAUR.value == "Dinosaur"


class TestCompanyTier:
    def test_tier_1(self):
        assert CompanyTier.TIER_1.value == "Tier 1"

    def test_tier_3(self):
        assert CompanyTier.TIER_3.value == "Tier 3"


class TestThreatLevel:
    def test_low(self):
        assert ThreatLevel.LOW.value == "Low"

    def test_high(self):
        assert ThreatLevel.HIGH.value == "High"


class TestConstants:
    def test_revenue_per_employee_exceptional(self):
        assert REVENUE_PER_EMPLOYEE_EXCEPTIONAL == 250

    def test_growth_rate_exceptional(self):
        assert GROWTH_RATE_EXCEPTIONAL == 30

    def test_ai_exceptional(self):
        assert AI_EXCEPTIONAL == 8
