"""
Task 10: AI Maturity Consistency Tests

Verify that AI maturity levels are consistent with AI scores.
Fixes contradictions like 'Strong' maturity with 0/10 score.
"""

import pytest

from solstein.data.unified_loader import UnifiedCompanyLoader
from solstein.domain.models import AIMaturity


class TestAIMaturityConsistency:
    """Test AI maturity and score consistency."""

    @pytest.fixture
    def loader(self):
        """Load unified companies."""
        return UnifiedCompanyLoader()

    @pytest.fixture
    def companies(self, loader):
        """Get all unified companies."""
        return loader.load_unified_companies()

    def test_eneve_ai_maturity_consistency(self, companies):
        """Test that Eneve has consistent AI maturity and score."""
        eneve = next((c for c in companies if "Eneve" in c.name), None)
        assert eneve is not None, "Eneve not found"

        # Eneve should have 'Strong' AI maturity
        assert eneve.ai_maturity == AIMaturity.STRONG

        # AI score should NOT be 0 (was the bug)
        assert eneve.ai_score is not None
        assert eneve.ai_score > 0, "AI score should be > 0 for 'Strong' maturity"

        # AI score should be reasonable for 'Strong' maturity (6-8 range)
        assert 6 <= eneve.ai_score <= 8, f"AI score {eneve.ai_score} not in expected range for 'Strong' maturity"

    def test_no_strong_maturity_with_zero_score(self, companies):
        """Test that no 'Strong' or 'Very Strong' maturity companies have 0 score."""
        strong_or_very_strong = [c for c in companies if c.ai_maturity in [AIMaturity.STRONG, AIMaturity.VERY_STRONG]]

        for company in strong_or_very_strong:
            # If AI score is present, it should not be 0
            if company.ai_score is not None:
                assert company.ai_score != 0, (
                    f"{company.name} has {company.ai_maturity} maturity but 0 AI score (contradiction)"
                )

    def test_ai_score_range_valid(self, companies):
        """Test that all AI scores are in valid 0-10 range."""
        for company in companies:
            if company.ai_score is not None:
                assert 0 <= company.ai_score <= 10, f"{company.name} has invalid AI score {company.ai_score}"

    def test_ai_maturity_consistency_across_dataset(self, companies):
        """Test that AI maturity and score are generally consistent."""
        # Group by AI maturity
        by_maturity = {}
        for company in companies:
            if company.ai_maturity not in by_maturity:
                by_maturity[company.ai_maturity] = []
            by_maturity[company.ai_maturity].append(company)

        # Check that higher maturity levels have higher average scores
        maturity_order = [
            AIMaturity.NONE,
            AIMaturity.LOW,
            AIMaturity.MODERATE,
            AIMaturity.STRONG,
            AIMaturity.VERY_STRONG,
        ]

        avg_scores = {}
        for maturity in maturity_order:
            if maturity in by_maturity:
                companies_with_scores = [c for c in by_maturity[maturity] if c.ai_score is not None]
                if companies_with_scores:
                    avg_scores[maturity] = sum(c.ai_score for c in companies_with_scores) / len(companies_with_scores)

        # Verify that average scores increase with maturity (where data exists)
        prev_avg = -1
        for maturity in maturity_order:
            if maturity in avg_scores:
                assert avg_scores[maturity] >= prev_avg, (
                    f"Average AI score for {maturity} ({avg_scores[maturity]}) should be >= previous ({prev_avg})"
                )
                prev_avg = avg_scores[maturity]
