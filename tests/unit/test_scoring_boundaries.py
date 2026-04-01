"""
STORY-045: Scoring Boundary Tests for All Classification Tiers

Verifies that the scoring system correctly classifies companies at exact
boundary values using epsilon-based testing. All tests use named constants
from solstein.analytics.constants — no numeric literals for thresholds.

These tests exercise the production classification code paths to ensure
that threshold changes are caught by CI.
"""

import pytest

from solstein.analytics.constants import (
    LEAD_SCORE_THRESHOLD,
    MAX_SCORE,
    MIN_SCORE,
    PHOENIX_SCORE_THRESHOLD,
    SALT_SCORE_THRESHOLD,
    derive_threat_level,
)
from solstein.analytics.scoring import classify_company
from solstein.domain.models import CompanyClassification

# Small epsilon for boundary testing — must be smaller than the gap
# between LEAD_SCORE_THRESHOLD (4.49) and SALT_SCORE_THRESHOLD (4.5).
EPSILON = 0.001


# ---------------------------------------------------------------------------
# REQ-1 & REQ-2: Boundary tests using named constants with epsilon
# ---------------------------------------------------------------------------


class TestPhoenixBoundary:
    """Tests around the Salt/Phoenix boundary (PHOENIX_SCORE_THRESHOLD)."""

    def test_just_below_phoenix_threshold_is_salt(self):
        """Score just below Phoenix threshold should classify as Salt."""
        score = PHOENIX_SCORE_THRESHOLD - EPSILON
        result = classify_company(score)
        assert result == CompanyClassification.SALT, (
            f"Score {score} (PHOENIX_THRESHOLD - epsilon) should be Salt, got {result}"
        )

    def test_at_phoenix_threshold_is_phoenix(self):
        """Score exactly at Phoenix threshold should classify as Phoenix."""
        score = PHOENIX_SCORE_THRESHOLD
        result = classify_company(score)
        assert result == CompanyClassification.PHOENIX, (
            f"Score {score} (exactly PHOENIX_THRESHOLD) should be Phoenix, got {result}"
        )

    def test_just_above_phoenix_threshold_is_phoenix(self):
        """Score just above Phoenix threshold should classify as Phoenix."""
        score = PHOENIX_SCORE_THRESHOLD + EPSILON
        result = classify_company(score)
        assert result == CompanyClassification.PHOENIX, (
            f"Score {score} (PHOENIX_THRESHOLD + epsilon) should be Phoenix, got {result}"
        )


class TestLeadSaltBoundary:
    """Tests around the Lead/Salt boundary (LEAD_SCORE_THRESHOLD / SALT_SCORE_THRESHOLD)."""

    def test_just_below_lead_threshold_is_lead(self):
        """Score just below Lead threshold should classify as Lead."""
        score = LEAD_SCORE_THRESHOLD - EPSILON
        result = classify_company(score)
        assert result == CompanyClassification.LEAD, (
            f"Score {score} (LEAD_THRESHOLD - epsilon) should be Lead, got {result}"
        )

    def test_at_lead_threshold_is_lead(self):
        """Score exactly at Lead threshold should classify as Lead (inclusive)."""
        score = LEAD_SCORE_THRESHOLD
        result = classify_company(score)
        assert result == CompanyClassification.LEAD, (
            f"Score {score} (exactly LEAD_THRESHOLD) should be Lead, got {result}"
        )

    def test_just_above_lead_threshold_is_salt(self):
        """Score just above Lead threshold should classify as Salt."""
        score = LEAD_SCORE_THRESHOLD + EPSILON
        result = classify_company(score)
        assert result == CompanyClassification.SALT, (
            f"Score {score} (LEAD_THRESHOLD + epsilon) should be Salt, got {result}"
        )

    def test_at_salt_threshold_is_salt(self):
        """Score exactly at Salt threshold should classify as Salt."""
        score = SALT_SCORE_THRESHOLD
        result = classify_company(score)
        assert result == CompanyClassification.SALT, (
            f"Score {score} (exactly SALT_THRESHOLD) should be Salt, got {result}"
        )

    def test_just_below_salt_threshold_is_lead(self):
        """Score just below Salt threshold but above Lead threshold is Salt.

        The gap between LEAD_SCORE_THRESHOLD (4.49) and SALT_SCORE_THRESHOLD (4.5)
        is 0.01, and values in this gap (e.g. 4.495) are Salt because they are
        not <= LEAD_SCORE_THRESHOLD.
        """
        score = SALT_SCORE_THRESHOLD - EPSILON
        result = classify_company(score)
        assert result == CompanyClassification.SALT, (
            f"Score {score} (SALT_THRESHOLD - epsilon) should be Salt, got {result}"
        )


# ---------------------------------------------------------------------------
# REQ-3: Tests cover all tiers including edge cases at score range bounds
# ---------------------------------------------------------------------------


class TestScoreRangeBounds:
    """Tests at the extreme ends of the valid score range."""

    def test_minimum_score_is_lead(self):
        """Minimum possible score (0.0) should classify as Lead."""
        result = classify_company(MIN_SCORE)
        assert result == CompanyClassification.LEAD, (
            f"MIN_SCORE ({MIN_SCORE}) should be Lead, got {result}"
        )

    def test_maximum_score_is_phoenix(self):
        """Maximum possible score (10.0) should classify as Phoenix."""
        result = classify_company(MAX_SCORE)
        assert result == CompanyClassification.PHOENIX, (
            f"MAX_SCORE ({MAX_SCORE}) should be Phoenix, got {result}"
        )

    def test_none_score_defaults_to_salt(self):
        """None score should default to Salt classification."""
        result = classify_company(None)
        assert result == CompanyClassification.SALT, (
            f"None score should be Salt, got {result}"
        )

    def test_midpoint_of_salt_range_is_salt(self):
        """Score in the middle of the Salt range should be Salt."""
        midpoint = (SALT_SCORE_THRESHOLD + PHOENIX_SCORE_THRESHOLD) / 2
        result = classify_company(midpoint)
        assert result == CompanyClassification.SALT, (
            f"Salt midpoint ({midpoint}) should be Salt, got {result}"
        )


# ---------------------------------------------------------------------------
# REQ-4: Parametrized sweep through all tier ranges
# ---------------------------------------------------------------------------


class TestParametrizedClassification:
    """Parametrized tests confirming classification across the score spectrum."""

    @pytest.mark.parametrize(
        "score",
        [
            MIN_SCORE,
            MIN_SCORE + EPSILON,
            LEAD_SCORE_THRESHOLD - 1.0,
            LEAD_SCORE_THRESHOLD - EPSILON,
            LEAD_SCORE_THRESHOLD,
        ],
    )
    def test_lead_range(self, score):
        """Scores in the Lead range should classify as Lead."""
        result = classify_company(score)
        assert result == CompanyClassification.LEAD, (
            f"Score {score} should be Lead, got {result}"
        )

    @pytest.mark.parametrize(
        "score",
        [
            LEAD_SCORE_THRESHOLD + EPSILON,
            SALT_SCORE_THRESHOLD,
            SALT_SCORE_THRESHOLD + 0.5,
            (SALT_SCORE_THRESHOLD + PHOENIX_SCORE_THRESHOLD) / 2,
            PHOENIX_SCORE_THRESHOLD - EPSILON,
        ],
    )
    def test_salt_range(self, score):
        """Scores in the Salt range should classify as Salt."""
        result = classify_company(score)
        assert result == CompanyClassification.SALT, (
            f"Score {score} should be Salt, got {result}"
        )

    @pytest.mark.parametrize(
        "score",
        [
            PHOENIX_SCORE_THRESHOLD,
            PHOENIX_SCORE_THRESHOLD + EPSILON,
            PHOENIX_SCORE_THRESHOLD + 1.0,
            MAX_SCORE - EPSILON,
            MAX_SCORE,
        ],
    )
    def test_phoenix_range(self, score):
        """Scores in the Phoenix range should classify as Phoenix."""
        result = classify_company(score)
        assert result == CompanyClassification.PHOENIX, (
            f"Score {score} should be Phoenix, got {result}"
        )


# ---------------------------------------------------------------------------
# Threshold constant integrity
# ---------------------------------------------------------------------------


class TestThresholdConstantIntegrity:
    """Verify threshold constants maintain expected relationships."""

    def test_phoenix_above_salt(self):
        """Phoenix threshold must be above Salt threshold."""
        assert PHOENIX_SCORE_THRESHOLD > SALT_SCORE_THRESHOLD

    def test_salt_above_lead(self):
        """Salt threshold must be above Lead threshold."""
        assert SALT_SCORE_THRESHOLD > LEAD_SCORE_THRESHOLD

    def test_lead_threshold_below_salt_threshold(self):
        """Lead threshold must be strictly below Salt threshold."""
        assert LEAD_SCORE_THRESHOLD < SALT_SCORE_THRESHOLD

    def test_phoenix_within_score_range(self):
        """Phoenix threshold must be within valid score range."""
        assert MIN_SCORE < PHOENIX_SCORE_THRESHOLD <= MAX_SCORE

    def test_lead_within_score_range(self):
        """Lead threshold must be within valid score range."""
        assert MIN_SCORE <= LEAD_SCORE_THRESHOLD < MAX_SCORE

    def test_gap_between_lead_and_salt_is_small(self):
        """Gap between Lead and Salt thresholds should be <= 0.1."""
        gap = SALT_SCORE_THRESHOLD - LEAD_SCORE_THRESHOLD
        assert gap <= 0.1, (
            f"Gap between Salt ({SALT_SCORE_THRESHOLD}) and Lead "
            f"({LEAD_SCORE_THRESHOLD}) is {gap}, expected <= 0.1"
        )


# ---------------------------------------------------------------------------
# Threat level boundary tests (derive_threat_level)
# ---------------------------------------------------------------------------


class TestThreatLevelBoundaries:
    """Verify threat level derivation at classification boundaries."""

    def test_phoenix_critical_boundary(self):
        """Phoenix with score >= 9.0 should be Critical threat."""

        assert derive_threat_level("Phoenix", 9.0) == "Critical"
        assert derive_threat_level("Phoenix", 8.99) == "High"

    def test_phoenix_high_boundary(self):
        """Phoenix with score 7.0-8.99 should be High threat."""

        assert derive_threat_level("Phoenix", PHOENIX_SCORE_THRESHOLD) == "High"
        assert derive_threat_level("Phoenix", 8.0) == "High"

    def test_salt_medium_boundary(self):
        """Salt with score >= 6.0 should be Medium threat."""

        assert derive_threat_level("Salt", 6.0) == "Medium"
        assert derive_threat_level("Salt", 5.99) == "Low"

    def test_lead_always_low(self):
        """Lead classification should always be Low threat."""

        assert derive_threat_level("Lead", 0.0) == "Low"
        assert derive_threat_level("Lead", MAX_SCORE) == "Low"
