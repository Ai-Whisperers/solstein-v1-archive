"""
Task 7: Deterministic Scoring Engine Tests

Ensures that the scoring engine produces identical results across multiple runs.
This is critical for reproducibility and auditability of company assessments.
"""

import pytest

from solstein.analytics.scoring import GrowthScorer
from solstein.data.unified_loader import UnifiedCompanyLoader


class TestDeterministicScoring:
    """Test suite for deterministic scoring."""

    @pytest.fixture
    def scorer(self):
        """Create a scorer instance."""
        return GrowthScorer()

    @pytest.fixture
    def unified_companies(self):
        """Load unified companies."""
        loader = UnifiedCompanyLoader()
        return loader.load_unified_companies()

    @pytest.fixture
    def eneve(self, unified_companies):
        """Get Eneve company."""
        return [c for c in unified_companies if "eneve" in c.name.lower()][0]

    def test_eneve_scoring_consistency_10_runs(self, scorer, eneve):
        """Test that Eneve produces identical scores across 10 runs."""
        scores = []
        for _ in range(10):
            scored = scorer.calculate_scores(eneve)
            scores.append(
                {
                    "growth": scored.growth_score,
                    "financial": scored.financial_health_score,
                    "competitive": scored.competitive_position_score,
                    "composite": scored.composite_score,
                }
            )

        # All scores should be identical
        for i in range(1, len(scores)):
            assert scores[i]["growth"] == scores[0]["growth"], (
                f"Growth score variance detected: {scores[0]['growth']} vs {scores[i]['growth']}"
            )
            assert scores[i]["financial"] == scores[0]["financial"], (
                f"Financial score variance detected: {scores[0]['financial']} vs {scores[i]['financial']}"
            )
            assert scores[i]["competitive"] == scores[0]["competitive"], (
                f"Competitive score variance detected: {scores[0]['competitive']} vs {scores[i]['competitive']}"
            )
            assert scores[i]["composite"] == scores[0]["composite"], (
                f"Composite score variance detected: {scores[0]['composite']} vs {scores[i]['composite']}"
            )

    def test_all_companies_deterministic_5_runs(self, scorer, unified_companies):
        """Test that all companies produce deterministic scores across 5 runs."""
        # Test a sample of companies (not all 200+ to keep test fast)
        sample_companies = unified_companies[:20]

        for company in sample_companies:
            scores = []
            for _ in range(5):
                scored = scorer.calculate_scores(company)
                scores.append(scored.composite_score)

            # All scores should be identical
            for i in range(1, len(scores)):
                assert scores[i] == scores[0], (
                    f"{company.name}: Composite score variance detected: {scores[0]} vs {scores[i]}"
                )

    def test_scoring_variance_below_threshold(self, scorer, eneve):
        """Test that scoring variance is below acceptable threshold (<0.2)."""
        scores = []
        for _ in range(10):
            scored = scorer.calculate_scores(eneve)
            scores.append(scored.composite_score)

        variance = max(scores) - min(scores)
        assert variance < 0.2, f"Scoring variance {variance} exceeds threshold of 0.2"

    def test_identical_input_identical_output(self, scorer, eneve):
        """Test that identical input always produces identical output."""
        # Score the same company twice
        scored1 = scorer.calculate_scores(eneve)
        scored2 = scorer.calculate_scores(eneve)

        # All scores should match exactly
        assert scored1.growth_score == scored2.growth_score
        assert scored1.financial_health_score == scored2.financial_health_score
        assert scored1.competitive_position_score == scored2.competitive_position_score
        assert scored1.composite_score == scored2.composite_score

    def test_scoring_breakdown_deterministic(self, scorer, eneve):
        """Test that scoring breakdown is deterministic."""
        breakdown1 = scorer.calculate_scores(eneve).scoring_breakdown
        breakdown2 = scorer.calculate_scores(eneve).scoring_breakdown

        # Breakdowns should be identical
        assert breakdown1 == breakdown2, f"Scoring breakdown variance detected:\n{breakdown1}\nvs\n{breakdown2}"

    def test_no_random_state_dependency(self, scorer, eneve):
        """Test that scoring doesn't depend on random state."""
        import random

        # Set different random seeds and verify scoring is still deterministic
        scores = []
        for seed in [42, 123, 999]:
            random.seed(seed)
            scored = scorer.calculate_scores(eneve)
            scores.append(scored.composite_score)

        # All scores should be identical regardless of random seed
        for i in range(1, len(scores)):
            assert scores[i] == scores[0], f"Scoring depends on random state: {scores[0]} vs {scores[i]}"

    def test_scoring_reproducible_across_scorer_instances(self, eneve):
        """Test that scoring is reproducible across different scorer instances."""
        scorer1 = GrowthScorer()
        scorer2 = GrowthScorer()

        scored1 = scorer1.calculate_scores(eneve)
        scored2 = scorer2.calculate_scores(eneve)

        assert scored1.composite_score == scored2.composite_score, (
            f"Scoring differs across scorer instances: {scored1.composite_score} vs {scored2.composite_score}"
        )

    def test_company_copy_produces_same_score(self, scorer, eneve):
        """Test that scoring a copy of a company produces the same score."""
        from copy import deepcopy

        eneve_copy = deepcopy(eneve)

        scored_original = scorer.calculate_scores(eneve)
        scored_copy = scorer.calculate_scores(eneve_copy)

        assert scored_original.composite_score == scored_copy.composite_score, (
            f"Scoring differs for copy: {scored_original.composite_score} vs {scored_copy.composite_score}"
        )

    def test_scoring_components_deterministic(self, scorer, eneve):
        """Test that all scoring components are deterministic."""
        components1 = scorer.calculate_scores(eneve).scoring_breakdown
        components2 = scorer.calculate_scores(eneve).scoring_breakdown

        # All component scores should match
        for key in components1:
            assert components1[key] == components2[key], (
                f"Component {key} variance: {components1[key]} vs {components2[key]}"
            )

    def test_large_batch_deterministic(self, scorer, unified_companies):
        """Test that scoring a large batch is deterministic."""
        # Score all companies twice
        batch1 = [scorer.calculate_scores(c).composite_score for c in unified_companies[:50]]
        batch2 = [scorer.calculate_scores(c).composite_score for c in unified_companies[:50]]

        # All scores should match
        for i, (score1, score2) in enumerate(zip(batch1, batch2, strict=False)):
            assert score1 == score2, f"Batch score {i} variance: {score1} vs {score2}"

    def test_scoring_explanation_deterministic(self, scorer, eneve):
        """Test that scoring explanations are deterministic."""
        scored1 = scorer.calculate_scores(eneve)
        scored2 = scorer.calculate_scores(eneve)

        # Explanations should be identical
        assert scored1.scoring_breakdown == scored2.scoring_breakdown
