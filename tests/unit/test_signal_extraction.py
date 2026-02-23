"""Tests for signal extraction framework.

Tests verify that signals are correctly defined, categorized, and extracted
from various agent data sources.
"""

from solstein.analytics.signals.extractors import (
    AggregateSignalExtractor,
    CompaniesHouseSignalExtractor,
    FinancialSignalExtractor,
    GitHubSignalExtractor,
    WebSearchSignalExtractor,
)
from solstein.analytics.signals.models import (
    Signal,
    SignalCategory,
    SignalDefinitions,
)


class TestSignalDefinitions:
    """Test suite for signal definitions."""

    def test_all_signals_defined(self):
        """Verify that signals are defined."""
        signals = SignalDefinitions.ALL_SIGNALS
        assert len(signals) > 50, f"Expected >50 signals, got {len(signals)}"

    def test_signal_category_distribution(self):
        """Verify that signals are distributed across 8 categories."""
        distribution = SignalDefinitions.get_category_distribution()
        assert len(distribution) == 8
        assert all(count > 0 for count in distribution.values())

    def test_growth_signals(self):
        """Verify growth signals are defined."""
        growth_signals = SignalDefinitions.get_signals_by_category(SignalCategory.GROWTH)
        assert len(growth_signals) >= 10
        assert any("Revenue" in s.name for s in growth_signals)
        assert any("User" in s.name for s in growth_signals)

    def test_financial_signals(self):
        """Verify financial signals are defined."""
        financial_signals = SignalDefinitions.get_signals_by_category(SignalCategory.FINANCIAL)
        assert len(financial_signals) >= 10
        assert any("Funding" in s.name for s in financial_signals)
        assert any("Burn" in s.name for s in financial_signals)

    def test_technical_signals(self):
        """Verify technical signals are defined."""
        technical_signals = SignalDefinitions.get_signals_by_category(SignalCategory.TECHNICAL)
        assert len(technical_signals) >= 10
        assert any("AI" in s.name for s in technical_signals)
        assert any("Architecture" in s.name for s in technical_signals)

    def test_hiring_signals(self):
        """Verify hiring signals are defined."""
        hiring_signals = SignalDefinitions.get_signals_by_category(SignalCategory.HIRING)
        assert len(hiring_signals) >= 10
        assert any("Headcount" in s.name for s in hiring_signals)
        assert any("Leadership" in s.name for s in hiring_signals)

    def test_product_signals(self):
        """Verify product signals are defined."""
        product_signals = SignalDefinitions.get_signals_by_category(SignalCategory.PRODUCT)
        assert len(product_signals) >= 10
        assert any("Feature" in s.name for s in product_signals)
        assert any("User" in s.name for s in product_signals)

    def test_market_signals(self):
        """Verify market signals are defined."""
        market_signals = SignalDefinitions.get_signals_by_category(SignalCategory.MARKET)
        assert len(market_signals) >= 10
        assert any("Market" in s.name for s in market_signals)
        assert any("Competitor" in s.name for s in market_signals)

    def test_operational_signals(self):
        """Verify operational signals are defined."""
        operational_signals = SignalDefinitions.get_signals_by_category(SignalCategory.OPERATIONAL)
        assert len(operational_signals) >= 10
        assert any("Compliance" in s.name for s in operational_signals)
        assert any("Uptime" in s.name for s in operational_signals)

    def test_strategic_signals(self):
        """Verify strategic signals are defined."""
        strategic_signals = SignalDefinitions.get_signals_by_category(SignalCategory.STRATEGIC)
        assert len(strategic_signals) >= 10
        assert any("Partnership" in s.name for s in strategic_signals)
        assert any("Series" in s.name for s in strategic_signals)

    def test_signal_count(self):
        """Verify signal count is accurate."""
        count = SignalDefinitions.get_signal_count()
        assert count > 50


class TestSignalObject:
    """Test suite for Signal objects."""

    def test_signal_creation(self):
        """Verify that signals can be created."""
        signal = Signal(
            name="Test Signal",
            category=SignalCategory.GROWTH,
            description="A test signal",
            value=7.5,
            confidence=0.9,
        )

        assert signal.name == "Test Signal"
        assert signal.category == SignalCategory.GROWTH
        assert signal.value == 7.5
        assert signal.confidence == 0.9

    def test_signal_to_dict(self):
        """Verify that signals can be converted to dictionaries."""
        signal = Signal(
            name="Test Signal",
            category=SignalCategory.GROWTH,
            description="A test signal",
            value=8.0,
            confidence=0.85,
        )

        signal_dict = signal.to_dict()

        assert signal_dict["name"] == "Test Signal"
        assert signal_dict["category"] == "growth"
        assert signal_dict["value"] == 8.0
        assert signal_dict["confidence"] == 0.85


class TestGitHubSignalExtractor:
    """Test suite for GitHub signal extraction."""

    def test_extract_github_stars(self):
        """Verify that GitHub stars signal is extracted."""
        extractor = GitHubSignalExtractor()
        data = {
            "repositories": [
                {"stars": 500},
                {"stars": 300},
                {"stars": 200},
            ]
        }

        signals = extractor.extract(data)

        assert any("Open Source" in s.name for s in signals)
        open_source_signal = next(s for s in signals if "Open Source" in s.name)
        assert open_source_signal.value > 0
        assert open_source_signal.confidence >= 0.7

    def test_extract_deployment_frequency(self):
        """Verify that deployment frequency signal is extracted."""
        extractor = GitHubSignalExtractor()
        data = {"activity": {"commits_per_month": 50}}

        signals = extractor.extract(data)

        assert any("Deployment" in s.name for s in signals)

    def test_extract_from_empty_data(self):
        """Verify that empty data returns no signals."""
        extractor = GitHubSignalExtractor()
        signals = extractor.extract({})

        assert len(signals) == 0

    def test_extract_multiple_signals(self):
        """Verify that multiple signals are extracted from complete data."""
        extractor = GitHubSignalExtractor()
        data = {
            "repositories": [{"stars": 1000}],
            "activity": {"commits_per_month": 100},
            "stats": {"total_contributors": 50},
        }

        signals = extractor.extract(data)

        assert len(signals) >= 2


class TestFinancialSignalExtractor:
    """Test suite for financial signal extraction."""

    def test_extract_funding(self):
        """Verify that funding signal is extracted."""
        extractor = FinancialSignalExtractor()
        data = {
            "total_funding": 5000000,
            "latest_round": {
                "size": 2000000,
                "valuation": 20000000,
            },
        }

        signals = extractor.extract(data)

        assert any("Funding" in s.name for s in signals)
        funding_signal = next(s for s in signals if "Total Funding" in s.name)
        assert funding_signal.text == "$5,000,000"

    def test_extract_runway(self):
        """Verify that runway signal is extracted."""
        extractor = FinancialSignalExtractor()
        data = {"runway_months": 18}

        signals = extractor.extract(data)

        assert any("Runway" in s.name for s in signals)


class TestCompaniesHouseSignalExtractor:
    """Test suite for Companies House signal extraction."""

    def test_extract_headcount(self):
        """Verify that headcount signal is extracted."""
        extractor = CompaniesHouseSignalExtractor()
        data = {"number_of_employees": 150}

        signals = extractor.extract(data)

        assert any("Headcount" in s.name for s in signals)

    def test_extract_revenue(self):
        """Verify that revenue signal is extracted."""
        extractor = CompaniesHouseSignalExtractor()
        data = {"revenue": 5000000}

        signals = extractor.extract(data)

        assert any("Revenue" in s.name for s in signals)
        revenue_signal = next(s for s in signals if "Revenue" in s.name)
        assert revenue_signal.confidence == 0.95


class TestWebSearchSignalExtractor:
    """Test suite for web search signal extraction."""

    def test_extract_press_mentions(self):
        """Verify that press mention signal is extracted."""
        extractor = WebSearchSignalExtractor()
        data = {"press_mentions": 25}

        signals = extractor.extract(data)

        assert any("Media" in s.name for s in signals)

    def test_extract_awards(self):
        """Verify that awards signal is extracted."""
        extractor = WebSearchSignalExtractor()
        data = {
            "industry_awards": [
                "Gartner Cool Vendor 2024",
                "Forrester Wave Leader 2024",
            ]
        }

        signals = extractor.extract(data)

        assert any("Award" in s.name for s in signals)

    def test_extract_product_reviews(self):
        """Verify that product review signal is extracted."""
        extractor = WebSearchSignalExtractor()
        data = {
            "product_reviews": [
                {"rating": 4.5},
                {"rating": 4.0},
                {"rating": 5.0},
            ]
        }

        signals = extractor.extract(data)

        assert any("Review" in s.name for s in signals)


class TestAggregateSignalExtractor:
    """Test suite for aggregate signal extraction."""

    def test_extract_all_sources(self):
        """Verify that signals are extracted from all sources."""
        extractor = AggregateSignalExtractor()
        agent_results = {
            "github": {
                "repositories": [{"stars": 1000}],
                "activity": {"commits_per_month": 50},
            },
            "financial": {"total_funding": 5000000},
            "companies_house": {"number_of_employees": 100, "revenue": 3000000},
            "web_search": {"press_mentions": 20},
        }

        signals = extractor.extract_all(agent_results)

        assert len(signals) > 5
        categories = {s.category for s in signals}
        assert len(categories) > 2

    def test_extract_by_single_agent(self):
        """Verify that signals can be extracted from a single agent."""
        extractor = AggregateSignalExtractor()
        github_data = {
            "repositories": [{"stars": 500}],
            "activity": {"commits_per_month": 30},
        }

        signals = extractor.extract_by_agent("github", github_data)

        assert len(signals) > 0
        assert all(s.source == "GitHub" for s in signals)

    def test_extract_unknown_agent(self):
        """Verify that unknown agents return empty signal list."""
        extractor = AggregateSignalExtractor()
        signals = extractor.extract_by_agent("unknown_agent", {})

        assert len(signals) == 0


class TestSignalCompleteness:
    """Test suite for signal completeness and validity."""

    def test_all_signals_have_category(self):
        """Verify that all signals have a category."""
        for signal in SignalDefinitions.ALL_SIGNALS:
            assert signal.category in SignalCategory
            assert signal.category.value in [
                "growth",
                "financial",
                "technical",
                "hiring",
                "product",
                "market",
                "operational",
                "strategic",
            ]

    def test_all_signals_have_description(self):
        """Verify that all signals have descriptions."""
        for signal in SignalDefinitions.ALL_SIGNALS:
            assert signal.description is not None
            assert len(signal.description) > 10

    def test_signal_names_are_unique(self):
        """Verify that signal names are unique."""
        names = [s.name for s in SignalDefinitions.ALL_SIGNALS]
        assert len(names) == len(set(names)), "Duplicate signal names found"
