"""
Classification Boundary Tests
Verifies that classification thresholds are unified and consistent across all code paths.
"""

import pytest

from solstein.analytics.classification import classify_company_balanced
from solstein.analytics.classification_service import ClassificationService, classify_company
from solstein.analytics.constants import LEAD_SCORE_THRESHOLD, PHOENIX_SCORE_THRESHOLD, SALT_SCORE_THRESHOLD
from solstein.analytics.scoring import classify_company as scoring_classify


class TestClassificationBoundaries:
    """Test classification boundary conditions across all code paths."""

    def test_phoenix_threshold_value(self):
        """Verify Phoenix threshold is 7.0."""
        assert PHOENIX_SCORE_THRESHOLD == 7.0

    def test_salt_threshold_value(self):
        """Verify Salt threshold is 4.5."""
        assert SALT_SCORE_THRESHOLD == 4.5

    def test_lead_threshold_value(self):
        """Verify Lead threshold is 4.49 (anything below Salt threshold)."""
        assert LEAD_SCORE_THRESHOLD == 4.49

    @pytest.mark.parametrize(
        "score,expected",
        [
            # Phoenix: >= 7.0
            (10.0, "Phoenix"),
            (9.0, "Phoenix"),
            (8.0, "Phoenix"),
            (7.5, "Phoenix"),
            (7.0, "Phoenix"),
            # Salt: 4.5 - 6.99
            (6.9, "Salt"),
            (6.0, "Salt"),
            (5.5, "Salt"),
            (5.0, "Salt"),
            (4.5, "Salt"),
            # Lead: < 4.5
            (4.4, "Lead"),
            (4.0, "Lead"),
            (3.0, "Lead"),
            (0.0, "Lead"),
        ],
    )
    def test_classify_company_boundaries(self, score, expected):
        """Test classification at all boundary values."""
        assert classify_company(score) == expected


class TestConsistentClassificationAcrossPaths:
    """Verify same input produces same output across all classification code paths."""

    @pytest.mark.parametrize("score", [10.0, 9.0, 8.0, 7.5, 7.0, 6.9, 6.0, 5.5, 5.0, 4.5, 4.4, 4.0, 3.0, 0.0])
    def test_classification_service_matches_scoring(self, score):
        """ClassificationService should match scoring.classify_company."""
        service = ClassificationService()
        service_result = service.classify(score)
        scoring_result = scoring_classify(score)
        assert service_result == scoring_result, f"Score {score}: Service={service_result}, Scoring={scoring_result}"

    @pytest.mark.parametrize("score", [10.0, 9.0, 8.0, 7.5, 7.0, 6.9, 6.0, 5.5, 5.0, 4.5, 4.4, 4.0, 3.0, 0.0])
    def test_classification_balanced_matches_scoring(self, score):
        """classify_company_balanced should match scoring.classify_company."""
        balanced_result = classify_company_balanced(score)
        scoring_result = scoring_classify(score)
        assert balanced_result == scoring_result, f"Score {score}: Balanced={balanced_result}, Scoring={scoring_result}"


class TestThresholdSingleSourceOfTruth:
    """Verify thresholds are defined only in constants.py."""

    def test_thresholds_defined_in_constants(self):
        """Verify classification thresholds exist in constants module."""
        from solstein.analytics import constants

        assert hasattr(constants, "PHOENIX_SCORE_THRESHOLD")
        assert hasattr(constants, "SALT_SCORE_THRESHOLD")
        assert hasattr(constants, "LEAD_SCORE_THRESHOLD")

    def test_threshold_values_are_floats(self):
        """Verify threshold values are numeric."""
        assert isinstance(PHOENIX_SCORE_THRESHOLD, (int, float))
        assert isinstance(SALT_SCORE_THRESHOLD, (int, float))
        assert isinstance(LEAD_SCORE_THRESHOLD, (int, float))

    def test_thresholds_are_positive(self):
        """Verify thresholds are positive values."""
        assert PHOENIX_SCORE_THRESHOLD > 0
        assert SALT_SCORE_THRESHOLD > 0
        assert LEAD_SCORE_THRESHOLD >= 0

    def test_threshold_order(self):
        """Verify threshold ordering: Phoenix > Salt > Lead."""
        assert PHOENIX_SCORE_THRESHOLD > SALT_SCORE_THRESHOLD
        assert SALT_SCORE_THRESHOLD > LEAD_SCORE_THRESHOLD
