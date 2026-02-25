"""
Task 9-11: Classification System Tests

Tests for balanced classification (Phoenix/Salt/Lead) with confidence scoring.
"""

import pytest
from src.solstein.domain.models import Company, FinancialMetric
from src.solstein.analytics.classification import (
    classify_company_balanced,
    calculate_classification_confidence,
    get_classification_with_confidence,
    is_tentative_classification,
    format_classification_with_confidence,
    get_classification_distribution,
    validate_classification_distribution,
)


class TestClassifyCompanyBalanced:
    """Test balanced classification logic."""

    def test_phoenix_high_score(self):
        """Test Phoenix classification for high scores."""
        assert classify_company_balanced(7.0) == "Phoenix"
        assert classify_company_balanced(8.0) == "Phoenix"
        assert classify_company_balanced(10.0) == "Phoenix"

    def test_salt_medium_score(self):
        """Test Salt classification for medium scores."""
        assert classify_company_balanced(5.5) == "Salt"
        assert classify_company_balanced(6.0) == "Salt"
        assert classify_company_balanced(6.99) == "Salt"

    def test_lead_low_score(self):
        """Test Lead classification for low scores."""
        assert classify_company_balanced(5.49) == "Lead"
        assert classify_company_balanced(4.0) == "Lead"
        assert classify_company_balanced(0.0) == "Lead"

    def test_boundary_phoenix_salt(self):
        """Test boundary between Phoenix and Salt."""
        assert classify_company_balanced(6.99) == "Salt"
        assert classify_company_balanced(7.0) == "Phoenix"

    def test_boundary_salt_lead(self):
        """Test boundary between Salt and Lead."""
        assert classify_company_balanced(5.49) == "Lead"
        assert classify_company_balanced(5.5) == "Salt"

    def test_none_score(self):
        """Test None score defaults to Salt."""
        assert classify_company_balanced(None) == "Salt"


class TestCalculateClassificationConfidence:
    """Test classification confidence calculation."""

    def test_high_completeness_high_confidence(self):
        """Test high completeness gives high confidence."""
        confidence = calculate_classification_confidence(7.0, 90.0)
        assert confidence > 0.8

    def test_low_completeness_low_confidence(self):
        """Test low completeness gives low confidence."""
        confidence = calculate_classification_confidence(7.0, 20.0)
        assert confidence < 0.5

    def test_boundary_score_reduces_confidence(self):
        """Test scores near boundaries have reduced confidence."""
        # Score near boundary (5.5)
        boundary_confidence = calculate_classification_confidence(5.5, 80.0)
        # Score far from boundary (6.5) - should have higher confidence
        normal_confidence = calculate_classification_confidence(6.5, 80.0)

        assert boundary_confidence < normal_confidence

    def test_none_values_low_confidence(self):
        """Test None values give low confidence."""
        assert calculate_classification_confidence(None, 80.0) == 0.3
        assert calculate_classification_confidence(7.0, None) == 0.3

    def test_confidence_range(self):
        """Test confidence is always 0-1."""
        for score in [0.0, 5.0, 7.0, 10.0]:
            for completeness in [0.0, 50.0, 100.0]:
                confidence = calculate_classification_confidence(score, completeness)
                assert 0.0 <= confidence <= 1.0


class TestGetClassificationWithConfidence:
    """Test getting classification with confidence."""

    def test_complete_company(self):
        """Test classification for complete company."""
        company = Company(
            id="test-1",
            name="Test Company",
            composite_score=7.5,
            data_quality_tier="COMPLETE",
        )

        classification, confidence = get_classification_with_confidence(company)

        assert classification == "Phoenix"
        assert confidence > 0.8

    def test_partial_company(self):
        """Test classification for partial company."""
        company = Company(
            id="test-2",
            name="Test Company",
            composite_score=5.8,
            data_quality_tier="PARTIAL",
        )

        classification, confidence = get_classification_with_confidence(company)

        assert classification == "Salt"
        assert 0.5 < confidence < 0.8

    def test_insufficient_company(self):
        """Test classification for insufficient data company."""
        company = Company(
            id="test-3",
            name="Test Company",
            composite_score=4.5,
            data_quality_tier="INSUFFICIENT",
        )

        classification, confidence = get_classification_with_confidence(company)

        assert classification == "Lead"
        assert confidence < 0.5


class TestIsTentativeClassification:
    """Test tentative classification detection."""

    def test_high_confidence_not_tentative(self):
        """Test high confidence is not tentative."""
        assert is_tentative_classification(0.8) is False
        assert is_tentative_classification(1.0) is False

    def test_low_confidence_tentative(self):
        """Test low confidence is tentative."""
        assert is_tentative_classification(0.6) is True
        assert is_tentative_classification(0.3) is True

    def test_boundary_confidence(self):
        """Test boundary confidence."""
        assert is_tentative_classification(0.7) is False  # Exactly at threshold
        assert is_tentative_classification(0.69) is True  # Just below threshold


class TestFormatClassificationWithConfidence:
    """Test formatting classification with confidence."""

    def test_format_phoenix(self):
        """Test formatting Phoenix classification."""
        result = format_classification_with_confidence("Phoenix", 0.92)
        assert result == "Phoenix (92% confidence)"

    def test_format_salt(self):
        """Test formatting Salt classification."""
        result = format_classification_with_confidence("Salt", 0.65)
        assert result == "Salt (65% confidence)"

    def test_format_lead(self):
        """Test formatting Lead classification."""
        result = format_classification_with_confidence("Lead", 0.45)
        assert result == "Lead (45% confidence)"


class TestGetClassificationDistribution:
    """Test getting classification distribution."""

    def test_distribution_single_company(self):
        """Test distribution with single company."""
        company = Company(
            id="test-1",
            name="Test Company",
            composite_score=7.5,
        )

        dist = get_classification_distribution([company])

        assert dist["Phoenix"] == 1
        assert dist["Salt"] == 0
        assert dist["Lead"] == 0

    def test_distribution_multiple_companies(self):
        """Test distribution with multiple companies."""
        companies = [
            Company(id="1", name="Phoenix Co", composite_score=7.5),
            Company(id="2", name="Salt Co 1", composite_score=6.0),
            Company(id="3", name="Salt Co 2", composite_score=5.8),
            Company(id="4", name="Lead Co", composite_score=4.5),
        ]

        dist = get_classification_distribution(companies)

        assert dist["Phoenix"] == 1
        assert dist["Salt"] == 2
        assert dist["Lead"] == 1


class TestValidateClassificationDistribution:
    """Test validating classification distribution."""

    def test_valid_distribution(self):
        """Test validation of valid distribution."""
        companies = []
        # Create 20% Phoenix (4 companies)
        for i in range(4):
            companies.append(Company(id=f"p{i}", name=f"Phoenix {i}", composite_score=7.5))
        # Create 65% Salt (13 companies)
        for i in range(13):
            companies.append(Company(id=f"s{i}", name=f"Salt {i}", composite_score=6.0))
        # Create 15% Lead (3 companies)
        for i in range(3):
            companies.append(Company(id=f"l{i}", name=f"Lead {i}", composite_score=4.5))

        result = validate_classification_distribution(companies)

        assert result["phoenix_valid"] is True
        assert result["salt_valid"] is True
        assert result["lead_valid"] is True
        assert result["total"] == 20

    def test_invalid_distribution_too_many_salt(self):
        """Test validation fails with too many Salt."""
        companies = []
        # Create 5% Phoenix
        for i in range(1):
            companies.append(Company(id=f"p{i}", name=f"Phoenix {i}", composite_score=7.5))
        # Create 95% Salt (too many)
        for i in range(19):
            companies.append(Company(id=f"s{i}", name=f"Salt {i}", composite_score=6.0))

        result = validate_classification_distribution(companies)

        assert result["phoenix_valid"] is False
        assert result["salt_valid"] is False
        assert result["lead_valid"] is False

    def test_distribution_percentages(self):
        """Test distribution percentage calculations."""
        companies = [
            Company(id="1", name="Phoenix", composite_score=7.5),
            Company(id="2", name="Salt", composite_score=6.0),
            Company(id="3", name="Lead", composite_score=4.5),
        ]

        result = validate_classification_distribution(companies)

        assert abs(result["phoenix_pct"] - 1 / 3) < 0.01
        assert abs(result["salt_pct"] - 1 / 3) < 0.01
        assert abs(result["lead_pct"] - 1 / 3) < 0.01
