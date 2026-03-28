"""Tests that parsers do not fabricate values from ambiguous currency strings.

STORY-044: Updated to use module-level parse functions instead of removed
private methods on CompetitorDataLoader.
"""

from solstein.data.parsers import parse_funding_amount, parse_valuation


def test_parser_does_not_fabricate_currency_ambiguous_values() -> None:
    """Ambiguous currency strings like '2B' should return None, not a guess."""
    assert parse_funding_amount("2B") is None
    assert parse_valuation("3B") is None
