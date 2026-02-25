"""
Task 11: Classification Confidence Scoring Tests

Verify that classification confidence is calculated and available.
"""

import pytest
from src.solstein.analytics.classification import (
    format_classification_with_confidence,
    get_classification_with_confidence,
    is_tentative_classification,
)
from src.solstein.analytics.scoring import GrowthScorer
from src.solstein.data.unified_loader import UnifiedCompanyLoader


class TestClassificationConfidence:
    """Test classification confidence scoring."""

    @pytest.fixture
    def loader(self):
        """Load unified companies."""
        return UnifiedCompanyLoader()

    @pytest.fixture
    def companies(self, loader):
        """Get all unified companies."""
        return loader.load_unified_companies()

    @pytest.fixture
    def scorer(self):
        """Create scorer."""
        return GrowthScorer()

    def test_classification_with_confidence_returns_tuple(self, companies, scorer):
        """Test that get_classification_with_confidence returns (classification, confidence) tuple."""
        company = companies[0]
        scored = scorer.calculate_scores(company)

        result = get_classification_with_confidence(scored)

        assert isinstance(result, tuple)
        assert len(result) == 2
        classification, confidence = result
        assert isinstance(classification, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_confidence_is_calculated_for_all_companies(self, companies, scorer):
        """Test that confidence is calculated for all companies."""
        for company in companies:
            scored = scorer.calculate_scores(company)
            _, confidence = get_classification_with_confidence(scored)

            # Confidence should always be between 0 and 1
            assert 0 <= confidence <= 1, f"Invalid confidence {confidence} for {company.name}"

    def test_tentative_classification_flag(self, companies, scorer):
        """Test that tentative classification flag works."""
        for company in companies[:20]:
            scored = scorer.calculate_scores(company)
            _, confidence = get_classification_with_confidence(scored)
            is_tentative = is_tentative_classification(confidence)

            # Tentative if confidence < 0.65
            if confidence < 0.65:
                assert is_tentative, f"Classification with confidence {confidence} should be tentative"
            else:
                assert not is_tentative, f"Classification with confidence {confidence} should not be tentative"

    def test_format_classification_with_confidence(self, companies, scorer):
        """Test that classification can be formatted with confidence."""
        company = companies[0]
        scored = scorer.calculate_scores(company)
        classification, confidence = get_classification_with_confidence(scored)

        formatted = format_classification_with_confidence(classification, confidence)

        assert isinstance(formatted, str)
        assert classification in formatted
        # Check that confidence percentage is in the formatted string
        confidence_pct = int(confidence * 100)
        assert str(confidence_pct) in formatted or str(confidence_pct + 1) in formatted

    def test_confidence_range_valid(self, companies, scorer):
        """Test that all confidence scores are in valid 0-1 range."""
        for company in companies:
            scored = scorer.calculate_scores(company)
            _, confidence = get_classification_with_confidence(scored)

            assert 0 <= confidence <= 1, f"Confidence {confidence} out of range"

    def test_classification_confidence_integration(self, companies, scorer):
        """Test that classification and confidence work together."""
        classifications = set()

        for company in companies:
            scored = scorer.calculate_scores(company)
            classification, confidence = get_classification_with_confidence(scored)

            classifications.add(classification)

            # Verify confidence is valid
            assert 0 <= confidence <= 1

        # Should have multiple classifications
        assert len(classifications) > 0, "No classifications found"
        assert len(classifications) >= 2, "Should have at least 2 different classifications"
