"""Tests for per-source-type fact extractors in aggregate.py.

These tests use realistic Pydantic model_dump() fixtures to ensure
extractors correctly navigate the NESTED dict structures produced by
our domain models.  This prevents the class of bug where a developer
assumes raw API response shapes instead of our model_dump() output.

Root cause addressed: Nyx rewrote _extract_yahoo_finance using flat
top-level keys (content["revenue"]) instead of the correct nested
paths (content["financials"]["revenue"]).  These tests catch that
exact failure mode — a flat-key extraction silently returns no data.
"""

import pytest

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.research.aggregate import (
    _extract_crunchbase,
    _extract_exa_search,
    _extract_facts_from_source,
    _extract_generic,
    _extract_linkedin,
    _extract_news,
    _extract_patents,
    _extract_website,
    _extract_yahoo_finance,
)

# ---------------------------------------------------------------------------
# Fixtures — realistic model_dump() outputs
# ---------------------------------------------------------------------------


YAHOO_FINANCE_FIXTURE = {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NMS",
    "description": "Apple designs, manufactures, and markets smartphones and personal computers.",
    "founded": 1976,
    "headquarters": "Cupertino, CA",
    "website": "https://apple.com",
    "employees": 164000,
    "market_cap": 2_800_000_000_000,
    "pe_ratio": 28.5,
    "dividend_yield": 0.005,
    "financials": {
        "revenue": 394_328_000_000,
        "revenue_growth_yoy": 0.079,
        "profit_margin": 0.253,
        "ebitda": 130_541_000_000,
        "net_income": 99_803_000_000,
        "total_assets": None,
        "total_liabilities": None,
        "cash_position": None,
        "debt": None,
    },
    "growth": {
        "employee_count": 164000,
        "employee_growth": 0.02,
        "job_postings_count": 1500,
        "job_postings_growth": None,
        "ai_related_jobs": 350,
        "recent_hires": [],
        "office_expansion": [],
    },
    "ai": {
        "ai_score": 8,
        "ai_signal_strength": "strong",
        "ai_products": ["Siri", "Core ML"],
        "ai_partnerships": [],
        "ai_acquisitions": [],
        "ai_team_mentioned": True,
        "ml_products": [],
        "autonomous_features": False,
    },
    "technology": {
        "industry": "Consumer Electronics",
        "sector": "Technology",
        "sub_industry": None,
        "technology_stack": [],
        "deployment_model": None,
        "cloud_provider": None,
    },
    "products": {
        "description": None,
        "products": ["iPhone", "iPad", "Mac", "Apple Watch"],
        "services": ["Apple Music", "iCloud"],
        "target_markets": [],
        "competitors": ["Samsung", "Google"],
    },
    "news": None,
    "scorecard": None,
    "composite_score": None,
    "classification": None,
    "last_updated": None,
    "data_sources": ["yfinance"],
}

NEWS_FIXTURE = {
    "total_articles": 42,
    "sentiment_score": 0.65,
    "positive_count": 28,
    "negative_count": 5,
    "neutral_count": 9,
    "articles": [],
}

CRUNCHBASE_FIXTURE = {
    "total_raised": 250_000_000,
    "last_round_amount": 100_000_000,
    "last_round_valuation": 5_000_000_000,
    "num_rounds": 5,
    "last_round_stage": "Series D",
    "investors": ["Sequoia Capital", "a16z"],
}

PATENTS_FIXTURE = {
    "total_patents": 120,
    "ai_related_patents": 35,
    "top_categories": ["Machine Learning", "NLP", "Computer Vision"],
}

LINKEDIN_FIXTURE = {
    "employee_count": 5000,
    "employee_growth_pct": 0.15,
    "open_positions": 200,
    "ai_related_positions": 45,
}

WEBSITE_FIXTURE = {
    "main_products": ["Enterprise Platform", "Analytics Dashboard"],
    "tech_stack": ["React", "Python", "PostgreSQL"],
    "pricing_model": "subscription",
    "target_customers": ["Enterprise", "SMB"],
}


# ---------------------------------------------------------------------------
# Yahoo Finance extractor tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractYahooFinance:
    """Tests for _extract_yahoo_finance with CompanyResearch.model_dump() output."""

    def test_extracts_nested_financial_fields(self):
        """Financial metrics must be extracted from content['financials'], not top-level."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["revenue"] == 394_328_000_000
        assert facts["revenue_growth"] == 0.079
        assert facts["profit_margin"] == 0.253
        assert facts["ebitda"] == 130_541_000_000
        assert facts["net_income"] == 99_803_000_000

    def test_extracts_top_level_numeric_fields(self):
        """market_cap, pe_ratio, employees are top-level in CompanyResearch."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["market_cap"] == 2_800_000_000_000
        assert facts["pe_ratio"] == 28.5
        assert facts["employee_count"] == 164000
        assert facts["founded_year"] == 1976

    def test_extracts_string_facts(self):
        """description, headquarters, website, name, exchange are top-level strings."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["description"].startswith("Apple designs")
        assert facts["headquarters"] == "Cupertino, CA"
        assert facts["website"] == "https://apple.com"
        assert facts["name"] == "Apple Inc."
        assert facts["exchange"] == "NMS"

    def test_extracts_nested_growth_signals(self):
        """Growth metrics must be extracted from content['growth'], not top-level."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["employee_count"] in (164000,)  # from top-level or growth
        assert facts["employee_growth_pct"] == 0.02
        assert facts["open_positions"] == 1500
        assert facts["ai_related_positions"] == 350

    def test_extracts_nested_ai_assessment(self):
        """AI fields must be extracted from content['ai'], not top-level."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["ai_score"] == 8
        assert facts["ai_signal_strength"] == "strong"

    def test_extracts_nested_technology(self):
        """Industry/sector must be extracted from content['technology'], not top-level."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["industry"] == "Consumer Electronics"
        assert facts["sector"] == "Technology"

    def test_extracts_nested_products(self):
        """Products must be extracted from content['products']['products']."""
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert "iPhone" in facts["products"]
        assert "Mac" in facts["products"]

    def test_flat_key_access_returns_none(self):
        """REGRESSION GUARD: Flat key access for nested fields returns None.

        This test proves the exact bug Nyx introduced.  If someone rewrites
        the extractor to use content['revenue'] instead of
        content['financials']['revenue'], this test will catch it because
        the fixture has NO top-level 'revenue' key.
        """
        # The fixture has revenue ONLY inside 'financials', not at top level
        assert YAHOO_FINANCE_FIXTURE.get("revenue") is None
        assert YAHOO_FINANCE_FIXTURE.get("profit_margin") is None
        assert YAHOO_FINANCE_FIXTURE.get("ebitda") is None
        assert YAHOO_FINANCE_FIXTURE.get("eps") is None
        assert YAHOO_FINANCE_FIXTURE.get("industry") is None
        assert YAHOO_FINANCE_FIXTURE.get("sector") is None
        assert YAHOO_FINANCE_FIXTURE.get("tech_stack") is None

        # But the extractor correctly finds them via nested paths
        facts = dict(_extract_yahoo_finance(YAHOO_FINANCE_FIXTURE))
        assert facts["revenue"] == 394_328_000_000
        assert facts["profit_margin"] == 0.253
        assert facts["ebitda"] == 130_541_000_000
        assert facts["industry"] == "Consumer Electronics"
        assert facts["sector"] == "Technology"

    def test_handles_missing_sub_models(self):
        """Extractor must not crash when nested sub-models are None."""
        minimal = {
            "ticker": "TEST",
            "name": "Test Corp",
            "market_cap": 1_000_000,
            "financials": None,
            "growth": None,
            "ai": None,
            "technology": None,
            "products": None,
        }
        facts = dict(_extract_yahoo_finance(minimal))
        assert facts["market_cap"] == 1_000_000
        assert facts["name"] == "Test Corp"
        # No crash, no nested fields extracted
        assert "revenue" not in facts
        assert "ai_score" not in facts

    def test_global_market_enrichment_handling(self):
        """GlobalMarketEnrichment has top-level revenue + source_currency key."""
        global_market = {
            "source_currency": "USD",
            "revenue": 500_000_000,
            "market_cap": 2_000_000_000,
        }
        facts = _extract_yahoo_finance(global_market)
        fact_dict = dict(facts)
        assert fact_dict["revenue"] == 500_000_000
        assert fact_dict["market_cap"] == 2_000_000_000

    def test_total_field_count(self):
        """Full fixture should extract 20+ fields (regression guard for coverage)."""
        facts = _extract_yahoo_finance(YAHOO_FINANCE_FIXTURE)
        assert len(facts) >= 20, f"Expected 20+ facts, got {len(facts)}: {[f[0] for f in facts]}"


# ---------------------------------------------------------------------------
# Other extractor tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractNews:
    """Tests for _extract_news with PressCoverage fixture."""

    def test_extracts_all_fields(self):
        facts = dict(_extract_news(NEWS_FIXTURE))
        assert facts["article_count"] == 42
        assert facts["sentiment_score"] == 0.65
        assert facts["positive_article_count"] == 28
        assert facts["negative_article_count"] == 5

    def test_handles_empty_content(self):
        assert _extract_news({}) == []


@pytest.mark.unit
class TestExtractExaSearch:
    """Tests for _extract_exa_search."""

    def test_extracts_article_count(self):
        facts = dict(_extract_exa_search({"article_count": 15}))
        assert facts["article_count"] == 15

    def test_handles_empty_content(self):
        assert _extract_exa_search({}) == []


@pytest.mark.unit
class TestExtractCrunchbase:
    """Tests for _extract_crunchbase with FundingData fixture."""

    def test_extracts_all_fields(self):
        facts = dict(_extract_crunchbase(CRUNCHBASE_FIXTURE))
        assert facts["total_funding_raised"] == 250_000_000
        assert facts["last_round_amount"] == 100_000_000
        assert facts["valuation"] == 5_000_000_000
        assert facts["funding_rounds"] == 5
        assert facts["last_round_stage"] == "Series D"
        assert "Sequoia Capital" in facts["investors"]

    def test_handles_empty_content(self):
        assert _extract_crunchbase({}) == []


@pytest.mark.unit
class TestExtractPatents:
    """Tests for _extract_patents with PatentData fixture."""

    def test_extracts_all_fields(self):
        facts = dict(_extract_patents(PATENTS_FIXTURE))
        assert facts["total_patents"] == 120
        assert facts["ai_related_patents"] == 35
        assert "Machine Learning" in facts["patent_categories"]

    def test_handles_empty_content(self):
        assert _extract_patents({}) == []


@pytest.mark.unit
class TestExtractLinkedIn:
    """Tests for _extract_linkedin with LinkedInData fixture."""

    def test_extracts_all_fields(self):
        facts = dict(_extract_linkedin(LINKEDIN_FIXTURE))
        assert facts["employee_count"] == 5000
        assert facts["employee_growth_pct"] == 0.15
        assert facts["open_positions"] == 200
        assert facts["ai_related_positions"] == 45

    def test_handles_empty_content(self):
        assert _extract_linkedin({}) == []


@pytest.mark.unit
class TestExtractWebsite:
    """Tests for _extract_website with ProductInfo fixture."""

    def test_extracts_all_fields(self):
        facts = dict(_extract_website(WEBSITE_FIXTURE))
        assert "Enterprise Platform" in facts["products"]
        assert "React" in facts["tech_stack"]
        assert facts["pricing_model"] == "subscription"
        assert "Enterprise" in facts["target_customers"]

    def test_handles_empty_content(self):
        assert _extract_website({}) == []


@pytest.mark.unit
class TestExtractGeneric:
    """Tests for _extract_generic fallback."""

    def test_extracts_common_fields(self):
        content = {"name": "Test", "description": "A test", "website": "https://test.com"}
        facts = dict(_extract_generic(content))
        assert facts["name"] == "Test"
        assert facts["description"] == "A test"

    def test_handles_empty_content(self):
        assert _extract_generic({}) == []


# ---------------------------------------------------------------------------
# Source routing tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractFactsFromSource:
    """Tests for _extract_facts_from_source routing logic."""

    def test_routes_yahoo_finance(self):
        """Yahoo Finance source type routes to _extract_yahoo_finance."""
        source = RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="Yahoo Finance",
            raw_content=YAHOO_FINANCE_FIXTURE,
        )
        facts = _extract_facts_from_source(source)
        fact_dict = dict(facts)
        assert "revenue" in fact_dict
        assert fact_dict["revenue"] == 394_328_000_000

    def test_handles_list_content(self):
        """List content (e.g., article list) should return article_count.

        Uses model_construct() to bypass Pydantic validation since RawDataSource
        only accepts str|dict, but _extract_facts_from_source defensively handles
        list content at runtime (e.g., from manual construction or deserialization).
        """
        source = RawDataSource.model_construct(
            source_type=DataSourceType.EXA_SEARCH,
            source_name="exa",
            raw_content=[{"title": "Article 1"}, {"title": "Article 2"}],
        )
        facts = _extract_facts_from_source(source)
        assert facts == [("article_count", 2)]

    def test_handles_string_content(self):
        """String content should return empty list."""
        source = RawDataSource(
            source_type=DataSourceType.WEBSITE,
            source_name="website",
            raw_content="raw html string",
        )
        assert _extract_facts_from_source(source) == []

    def test_handles_none_content(self):
        """None content should return empty list.

        Uses model_construct() to bypass Pydantic validation since RawDataSource
        only accepts str|dict, but _extract_facts_from_source defensively handles
        None content at runtime.
        """
        source = RawDataSource.model_construct(
            source_type=DataSourceType.WEBSITE,
            source_name="website",
            raw_content=None,
        )
        assert _extract_facts_from_source(source) == []
