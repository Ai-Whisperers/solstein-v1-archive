"""
Scoring Deduplication Verification Tests
Verifies that all duplicate scoring logic has been eliminated.
"""
import subprocess


class TestScoringDeduplication:
    """Verify scoring functions are implemented exactly once."""

    def test_merge_facts_into_financials_single_definition(self):
        """_merge_facts_into_financials should be defined in exactly one file."""
        result = subprocess.run(
            ["grep", "-r", "def _merge_facts_into_financials", "src/solstein/analytics/", "--include=*.py"],
            capture_output=True,
            text=True,
            cwd="/tmp/solstein"
        )
        matches = [line for line in result.stdout.strip().split("\n") if line and "__pycache__" not in line]
        assert len(matches) == 1, f"Expected 1 definition, found {len(matches)}: {matches}"
        assert "_shared.py" in matches[0], f"Should be in _shared.py, found: {matches}"

    def test_confidence_to_level_single_definition(self):
        """_confidence_to_level should be defined in exactly one file."""
        result = subprocess.run(
            ["grep", "-r", "def confidence_to_level", "src/solstein/analytics/", "--include=*.py"],
            capture_output=True,
            text=True,
            cwd="/tmp/solstein"
        )
        matches = [line for line in result.stdout.strip().split("\n") if line and "__pycache__" not in line]
        assert len(matches) == 1, f"Expected 1 definition, found {len(matches)}: {matches}"
        assert "_shared.py" in matches[0], f"Should be in _shared.py, found: {matches}"

    def test_scorer_files_import_from_shared(self):
        """All scorer files should import helpers from _shared."""
        from solstein.analytics.scorers._shared import confidence_to_level
        from solstein.analytics.scorers._shared import merge_facts_into_financials as shared_merge
        from solstein.analytics.scorers.financial_health import merge_facts_into_financials as fh_merge
        from solstein.analytics.scorers.growth_momentum import merge_facts_into_financials as gm_merge

        # Verify they are the same functions (not duplicates)
        assert fh_merge is shared_merge
        assert gm_merge is shared_merge
        assert confidence_to_level.__name__ == "confidence_to_level"


class TestScoringDelegation:
    """Verify analytics/scoring.py delegates to scorers."""

    def test_scoring_does_not_implement_local_scorers(self):
        """scoring.py should not re-implement scoring logic."""
        result = subprocess.run(
            ["grep", "-E", "class.*Scorer.*:$", "src/solstein/analytics/scoring.py"],
            capture_output=True,
            text=True,
            cwd="/tmp/solstein"
        )
        # GrowthScorer is allowed (it's a facade that delegates)
        assert "GrowthScorer" in result.stdout
        # But it should delegate to the real scorers
        with open("/tmp/solstein/src/solstein/analytics/scoring.py") as f:
            content = f.read()
            assert "GrowthMomentumScorer" in content
            assert "FinancialHealthScorer" in content
            assert "CompetitivePositionScorer" in content


class TestSharedUtilities:
    """Verify shared utilities work correctly."""

    def test_confidence_to_level_boundaries(self):
        """Test confidence_to_level returns correct levels."""
        from solstein.analytics.scorers._shared import confidence_to_level
        from solstein.domain.models import ConfidenceLevel

        assert confidence_to_level(1.0) == ConfidenceLevel.CONFIRMED
        assert confidence_to_level(0.95) == ConfidenceLevel.CONFIRMED
        assert confidence_to_level(0.9) == ConfidenceLevel.CONFIRMED
        assert confidence_to_level(0.89) == ConfidenceLevel.ESTIMATED
        assert confidence_to_level(0.8) == ConfidenceLevel.ESTIMATED
        assert confidence_to_level(0.7) == ConfidenceLevel.ESTIMATED
        assert confidence_to_level(0.69) == ConfidenceLevel.UNKNOWN
        assert confidence_to_level(0.5) == ConfidenceLevel.UNKNOWN
        assert confidence_to_level(0.0) == ConfidenceLevel.UNKNOWN
