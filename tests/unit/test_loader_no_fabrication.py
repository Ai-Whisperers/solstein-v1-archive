from solstein.data.loaders import CompetitorDataLoader


def test_loader_does_not_fabricate_currency_ambiguous_values() -> None:
    loader = CompetitorDataLoader()

    assert loader._parse_funding_amount("2B") is None
    assert loader._parse_valuation("3B") is None
