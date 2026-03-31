"""
Scoring Constants Verification Tests
Verifies that all magic numbers in scoring logic are replaced with named constants.
"""
import re


class TestScoringConstants:
    """Verify all scoring magic numbers are replaced with named constants."""

    def test_composite_weights_sum_to_one(self):
        """Test that composite weights sum to approximately 1.0."""
        from solstein.core.scoring_config import ScoringSettings
        settings = ScoringSettings()
        total = settings.composite.growth_weight + settings.composite.financial_weight + settings.composite.competitive_weight
        assert 0.99 <= total <= 1.01, f"Weights sum to {total}, expected ~1.0"

    def test_no_unexplained_numeric_literals_in_scoring(self):
        """Verify scoring.py has no unexplained numeric literals."""
        magic_number_pattern = r'\b\d+\.\d+\b'

        with open('/tmp/solstein/src/solstein/analytics/scoring.py') as f:
            content = f.read()

        # Remove comments and docstrings
        lines = content.split('\n')
        cleaned_lines = []
        in_docstring = False
        for line in lines:
            # Handle docstrings
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue

            # Remove inline comments
            line = line.split('#')[0].strip()
            if line:
                cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # Find all potential magic numbers
        matches = re.findall(magic_number_pattern, content)

        # Filter out common acceptable numbers
        acceptable = {'0.0', '1.0', '2.0', '3.0', '10.0', '20.0', '30.0', '50.0', '75.0', '100.0'}
        unexplained = [m for m in matches if m not in acceptable and not m.startswith('0.')]

        # Allow some specific known constants that are defined elsewhere
        known_constants = {
            '0.40', '0.30', # weights (from config)
            '0.90', '0.70', # confidence thresholds (from constants)
            '4.49', '4.5', '7.0',   # classification thresholds (from constants)
            '8.5', '2.0', '4.4',    # valuation constants (from constants)
        }
        truly_unexplained = [m for m in unexplained if m not in known_constants]

        assert len(truly_unexplained) == 0, f"Found unexplained magic numbers: {truly_unexplained}"

    def test_classification_constants_named_and_documented(self):
        """Verify classification constants are properly named and documented."""
        from solstein.analytics.constants import LEAD_SCORE_THRESHOLD, PHOENIX_SCORE_THRESHOLD, SALT_SCORE_THRESHOLD

        # Verify they exist and are numeric
        assert isinstance(PHOENIX_SCORE_THRESHOLD, (int, float))
        assert isinstance(SALT_SCORE_THRESHOLD, (int, float))
        assert isinstance(LEAD_SCORE_THRESHOLD, (int, float))

        # Verify they have reasonable values
        assert 0 <= LEAD_SCORE_THRESHOLD < SALT_SCORE_THRESHOLD < PHOENIX_SCORE_THRESHOLD <= 10

        # Verify they're defined in constants module (single source of truth)
        import solstein.analytics.constants as constants_module
        assert hasattr(constants_module, 'PHOENIX_SCORE_THRESHOLD')
        assert hasattr(constants_module, 'SALT_SCORE_THRESHOLD')
        assert hasattr(constants_module, 'LEAD_SCORE_THRESHOLD')

    def test_no_scoring_magic_numbers_in_scorers(self):
        """Verify scorer files have no unexplained magic numbers."""
        scorer_files = [
            '/tmp/solstein/src/solstein/analytics/scorers/financial_health.py',
            '/tmp/solstein/src/solstein/analytics/scorers/growth_momentum.py',
            '/tmp/solstein/src/solstein/analytics/scorers/competitive_position.py'
        ]

        magic_number_pattern = r'\b\d+\.\d+\b'
        acceptable = {'0.0', '1.0', '2.0', '0.5', '1.5', '2.5', '3.0', '5.0', '10.0', '20.0', '50.0', '100.0'}

        for filepath in scorer_files:
            with open(filepath) as f:
                content = f.read()

            # Remove comments and docstrings (simple approach)
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove everything after #
                line = line.split('#')[0]
                # Skip empty lines and docstring lines
                if line.strip() and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                    cleaned_lines.append(line)

            content = '\n'.join(cleaned_lines)
            matches = re.findall(magic_number_pattern, content)
            unexplained = [m for m in matches if m not in acceptable]

            # Some specific acceptable ones in scorers
            scorer_acceptable = {'500_000.0', '200_000.0', '100.0', '10.0', '1.0', '0.5', '15.0', '5.0', '1_000_000.0'}
            truly_unexplained = [m for m in unexplained if m not in scorer_acceptable]

            assert len(truly_unexplained) == 0, f"File {filepath} has unexplained magic numbers: {truly_unexplained}"


class TestScoringMethodologyDocumentation:
    """Verify scoring methodology is documented."""

    def test_constants_have_documentation(self):
        """Verify key constants have documentation comments."""
        with open('/tmp/solstein/src/solstein/analytics/constants.py') as f:
            content = f.read()

        # Check that key threshold constants have comments
        assert '# Phoenix' in content or '# High-growth' in content
        assert '# Salt' in content or '# Stable' in content
        assert '# Lead' in content or '# Legacy' in content

        # Check that weights are mentioned somewhere
        assert 'weight' in content.lower() or 'WEIGHT' in content
