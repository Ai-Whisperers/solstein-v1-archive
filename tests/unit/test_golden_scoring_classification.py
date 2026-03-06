"""Golden tests for scoring and classification - G2.

These tests protect against calibration drift by ensuring that known inputs
produce expected outputs. Any change to these expected values indicates a
regression or intentional calibration change that must be reviewed.

Part of EPIC-017 Wave 2 Testing Hardening.
"""

import pytest
from datetime import date
from typing import Any

from solstein.analytics.classification_service import ClassificationService
from solstein.analytics.scoring import GrowthScorer, classify_company
from solstein.analytics.constants import (
    PHOENIX_SCORE_THRESHOLD,
    SALT_SCORE_THRESHOLD,
    LEAD_SCORE_THRESHOLD,
)
from solstein.domain.models import Company, ThreatLevel


class TestClassificationGoldenCases:
    """Golden test cases for classification boundaries."""

    @pytest.fixture
    def service(self) -> ClassificationService:
        return ClassificationService()

    PHOENIX_CASES = [
        (10.0, "Phoenix", "Perfect score"),
        (9.0, "Phoenix", "Excellent score"),
        (8.0, "Phoenix", "Strong Phoenix"),
        (7.0, "Phoenix", "Minimum Phoenix threshold"),
        (7.1, "Phoenix", "Just above threshold"),
    ]

    SALT_CASES = [
        (6.9, "Salt", "Just below Phoenix threshold"),
        (6.0, "Salt", "Mid-range Salt"),
        (5.0, "Salt", "Lower Salt"),
        (4.5, "Salt", "Minimum Salt threshold"),
    ]

    LEAD_CASES = [
        (4.49, "Lead", "Just below Salt threshold"),
        (4.0, "Lead", "Mid-range Lead"),
        (2.0, "Lead", "Weak Lead"),
        (0.0, "Lead", "Minimum score"),
    ]

    EDGE_CASES = [
        (None, "Lead", "None score defaults to Lead"),
        (-1.0, "Lead", "Negative score clamps to Lead"),
        (100.0, "Phoenix", "Extreme high score clamps to Phoenix"),
    ]

    @pytest.mark.parametrize("score,expected,description", PHOENIX_CASES + SALT_CASES + LEAD_CASES + EDGE_CASES)
    def test_classify_company_golden_cases(
        self, service: ClassificationService, score: float | None, expected: str, description: str
    ) -> None:
        """Classification must match golden expectations."""
        result = service.classify(score)
        assert result == expected, f"Failed for {description}: expected {expected}, got {result}"

    def test_boundary_thresholds_exact(self, service: ClassificationService) -> None:
        """Exact boundary thresholds must classify correctly."""
        assert service.classify(7.0) == "Phoenix"
        assert service.classify(6.999999) == "Salt"
        assert service.classify(4.5) == "Salt"
        assert service.classify(4.499999) == "Lead"


class TestClassificationConfidenceGoldenCases:
    """Golden test cases for classification confidence calculation."""

    @pytest.fixture
    def service(self) -> ClassificationService:
        return ClassificationService()

    CONFIDENCE_CASES = [
        (8.0, 100.0, (0.95, 1.0), "High score, complete data"),
        (5.0, 100.0, (0.95, 1.0), "Mid Salt, complete data"),
        (7.5, 90.0, (0.90, 0.95), "Strong Phoenix, near-complete data"),
        (4.5, 100.0, (0.90, 0.95), "Near boundary with complete data"),
        (7.0, 100.0, (0.90, 0.95), "Near boundary with complete data"),
        (6.0, 70.0, (0.78, 0.82), "Mid Salt, partial data"),
        (4.0, 80.0, (0.85, 0.90), "Lead, good data"),
        (4.5, 40.0, (0.47, 0.52), "Boundary Salt, poor data"),
        (7.0, 50.0, (0.54, 0.60), "Boundary Phoenix, incomplete data"),
        (None, 100.0, (0.28, 0.32), "None score gives low confidence"),
        (5.0, None, (0.28, 0.32), "None completeness gives low confidence"),
        (None, None, (0.28, 0.32), "Both None gives low confidence"),
    ]

    @pytest.mark.parametrize("score,completeness,expected_range,description", CONFIDENCE_CASES)
    def test_confidence_golden_cases(
        self,
        service: ClassificationService,
        score: float | None,
        completeness: float | None,
        expected_range: tuple[float, float],
        description: str,
    ) -> None:
        """Confidence calculation must match golden expectations."""
        confidence = service.calculate_confidence(score, completeness)
        min_expected, max_expected = expected_range
        assert min_expected <= confidence <= max_expected, (
            f"Failed for {description}: confidence {confidence} not in range {expected_range}"
        )


class TestScoringGoldenCases:
    """Golden test cases for scoring calculations."""

    def create_test_company(self, **kwargs: Any) -> Company:
        """Create a test company with specified attributes."""
        defaults = {
            "id": "test-company",
            "name": "Test Company",
            "industry": "Technology",
            "founded_year": 2020,
            "employees": 100,
            "revenue": 10000000.0,
            "growth_rate": 0.50,
            "profit_margin": 0.20,
            "funding": 5000000.0,
            "valuation": 50000000.0,
        }
        defaults.update(kwargs)
        return Company(**defaults)

    GROWTH_SCORE_CASES = [
        (1.00, 10000000, 10000000, (3.0, 4.0), "Hypergrowth unicorn candidate"),
        (0.50, 10000000, 5000000, (3.0, 4.0), "Strong growth mid-stage"),
        (0.30, 5000000, 2000000, (3.0, 4.0), "Moderate growth early-stage"),
        (0.10, 1000000, 500000, (3.0, 4.0), "Slow growth seed-stage"),
        (0.0, 1000000, 0, (1.0, 2.0), "Zero growth"),
        (-0.20, 5000000, 0, (0.5, 1.5), "Negative growth (declining)"),
    ]

    @pytest.mark.parametrize("growth,revenue,funding,expected_range,description", GROWTH_SCORE_CASES)
    def test_growth_score_golden_cases(
        self, growth: float, revenue: int, funding: int, expected_range: tuple[float, float], description: str
    ) -> None:
        """Growth scoring must match golden expectations."""
        company = self.create_test_company(growth_rate=growth, revenue=float(revenue), funding=float(funding))
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        score = company.growth_score
        min_expected, max_expected = expected_range
        assert min_expected <= score <= max_expected, (
            f"Failed for {description}: score {score} not in range {expected_range}"
        )

    FINANCIAL_HEALTH_CASES = [
        (50000000, 0.30, 10000000, (6.0, 7.0), "Profitable scale-up"),
        (10000000, 0.20, 5000000, (7.0, 8.0), "Healthy mid-stage"),
        (5000000, 0.10, 3000000, (7.0, 8.0), "Break-even early-stage"),
        (1000000, -0.20, 2000000, (4.5, 5.5), "Burning cash seed-stage"),
        (1000000, -0.50, 500000, (4.5, 5.5), "High burn limited runway"),
    ]

    @pytest.mark.parametrize("revenue,margin,funding,expected_range,description", FINANCIAL_HEALTH_CASES)
    def test_financial_health_golden_cases(
        self, revenue: int, margin: float, funding: int, expected_range: tuple[float, float], description: str
    ) -> None:
        """Financial health scoring must match golden expectations."""
        company = self.create_test_company(revenue=float(revenue), profit_margin=margin, funding=float(funding))
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        score = company.financial_health_score
        min_expected, max_expected = expected_range
        assert min_expected <= score <= max_expected, (
            f"Failed for {description}: score {score} not in range {expected_range}"
        )


class TestCompositeScoreGoldenCases:
    """Golden test cases for composite score calculation."""

    def create_test_company(self, **kwargs: Any) -> Company:
        """Create a test company with specified attributes."""
        defaults = {
            "id": "test-company",
            "name": "Test Company",
            "industry": "Technology",
            "founded_year": 2020,
            "employees": 100,
            "revenue": 10000000.0,
            "growth_rate": 0.50,
            "profit_margin": 0.20,
            "funding": 5000000.0,
            "valuation": 50000000.0,
        }
        defaults.update(kwargs)
        return Company(**defaults)

    COMPOSITE_SCORE_CASES = [
        (1.00, 50000000, 0.30, 10000000, (4.0, 4.6), "Lead", "Unicorn profile"),
        (0.60, 20000000, 0.25, 8000000, (4.0, 4.6), "Lead", "Strong scale-up"),
        (0.40, 10000000, 0.15, 5000000, (4.5, 5.0), "Salt", "Solid mid-stage"),
        (0.20, 5000000, 0.10, 3000000, (4.5, 5.0), "Salt", "Growing early-stage"),
        (0.10, 2000000, 0.05, 1000000, (4.5, 5.0), "Salt", "Early startup"),
        (0.0, 1000000, -0.1, 500000, (3.0, 4.0), "Lead", "Struggling startup"),
    ]

    @pytest.mark.parametrize(
        "growth,revenue,margin,funding,expected_range,expected_class,description", COMPOSITE_SCORE_CASES
    )
    def test_composite_score_golden_cases(
        self,
        growth: float,
        revenue: int,
        margin: float,
        funding: int,
        expected_range: tuple[float, float],
        expected_class: str,
        description: str,
    ) -> None:
        """Composite scoring must match golden expectations."""
        company = self.create_test_company(
            growth_rate=growth, revenue=float(revenue), profit_margin=margin, funding=float(funding)
        )
        scorer = GrowthScorer()
        scorer.calculate_scores(company)
        score = company.composite_score
        classification = classify_company(score)
        min_expected, max_expected = expected_range
        assert min_expected <= score <= max_expected, (
            f"Failed for {description}: score {score} not in range {expected_range}"
        )
        assert classification == expected_class, (
            f"Failed for {description}: expected {expected_class}, got {classification}"
        )


class TestCalibrationDriftDetection:
    """Tests to detect calibration drift in scoring and classification."""

    def test_threshold_constants_unchanged(self) -> None:
        """Threshold constants must not change without explicit review."""
        assert PHOENIX_SCORE_THRESHOLD == 7.0, "Phoenix threshold changed"
        assert SALT_SCORE_THRESHOLD == 4.5, "Salt threshold changed"
        assert LEAD_SCORE_THRESHOLD == 4.49, "Lead threshold changed"

    def test_exact_classification_values(self) -> None:
        """Exact classification values for key reference points."""
        test_cases = [
            (0.0, "Lead"),
            (4.0, "Lead"),
            (4.49, "Lead"),
            (4.5, "Salt"),
            (5.0, "Salt"),
            (6.0, "Salt"),
            (7.0, "Phoenix"),
            (8.0, "Phoenix"),
            (10.0, "Phoenix"),
        ]
        for score, expected in test_cases:
            result = classify_company(score)
            assert result == expected, f"Score {score}: expected {expected}, got {result}"
