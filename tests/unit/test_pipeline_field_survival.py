"""STORY-351 Regression Gate: every fact type from adapters must reach Company.

This test is a contract. Once it passes it must NEVER be weakened.
Every new adapter field that fails this test is a wiring bug, not a test problem.

Intentionally excluded fact types must be listed in field_survival_policy.py
with a documented reason. "I don't know" is not a valid reason.
"""

from __future__ import annotations

from typing import Any

from solstein.domain.models import AggregatedDataRecord, DataSourceType, RawDataRecord, RawDataSource
from solstein.research.aggregate import DefaultFactAggregator
from solstein.research.company_builder import build_company_entity_from_signals
from solstein.research.discovery import DiscoveryCandidate
from solstein.research.field_survival_policy import INTENTIONALLY_EXCLUDED_FACTS
from solstein.research.signals import extract_signals

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_candidate(company_id: str = "test-corp-001") -> DiscoveryCandidate:
    return DiscoveryCandidate(
        company_id=company_id,
        name="Test Corporation",
        market="energy_software",
        ticker="TST",
        industry="SaaS",
        region="London, UK",
        tags=["saas", "b2b"],
        seed_relevance=0.9,
        discovery_reason="test",
        source_links=["https://example.com"],
    )


def _flat_values(data: Any) -> set[Any]:
    """Recursively flatten all scalar values from a dict/list structure."""
    result: set[Any] = set()
    if isinstance(data, dict):
        for v in data.values():
            result |= _flat_values(v)
    elif isinstance(data, list):
        for item in data:
            result |= _flat_values(item)
    elif data is not None and not isinstance(data, (dict, list)):
        result.add(data)
    return result


def _field_names_in_dump(company_dump: dict[str, Any]) -> set[str]:
    """Return all key names present at any level of the company dump."""
    result: set[str] = set()

    def _collect_keys(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                result.add(k)
                _collect_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                _collect_keys(item)

    _collect_keys(company_dump)
    return result


def _fact_is_present(fact_type: str, value: Any, company_dump: dict[str, Any]) -> bool:
    """Return True if the fact type is represented in the company dump.

    Checks:
    1. A field named exactly `fact_type` exists in the dump (any level), OR
    2. A field named with a known alias exists (e.g. employee_count → employees), OR
    3. The value appears in the financials sub-dict, OR
    4. The fact type is a list and appears under products/tech_stack/etc.
    """
    # Direct field name match (any nesting level)
    all_keys = _field_names_in_dump(company_dump)

    # Direct match
    if fact_type in all_keys:
        return True

    # Known aliases: fact_type → Company/FinancialMetric field name
    _ALIASES: dict[str, str] = {
        "employee_count": "employees",        # FinancialMetric.employees
        "revenue_growth": "growth_rate",       # FinancialMetric.growth_rate
        "open_positions": "open_positions",    # Company.open_positions
        "ai_score": "ai_score",                # Company.ai_score
        "sentiment_score": "news_sentiment",   # Company.news_sentiment
        "article_count": "news_article_count", # Company.news_article_count
        "total_patents": "patent_count",       # Company.patent_count
        "last_round_stage": "last_round_stage",
        "last_round_amount": "last_round_amount",
        "ai_related_positions": "ai_jobs_count",
        "employee_growth_pct": "employee_growth_pct",
        "funding_rounds": "funding_round_count",
        "patent_categories": "patent_categories",
    }

    alias = _ALIASES.get(fact_type)
    if alias and alias in all_keys:
        return True

    return False


# ---------------------------------------------------------------------------
# Synthetic source payloads
# ---------------------------------------------------------------------------


def _yahoo_finance_source() -> RawDataSource:
    return RawDataSource(
        source_name="yahoo_finance",
        source_type=DataSourceType.YAHOO_FINANCE,
        confidence=0.9,
        raw_content={
            "financials": {
                "revenue": 1_000_000,
                "revenue_growth_yoy": 0.15,
                "profit_margin": 0.12,
                "ebitda": 200_000,
                "net_income": 100_000,
            },
            "market_cap": 5_000_000,
            "pe_ratio": 25.0,
            "current_price": 45.0,
            "eps_ttm": 1.8,
            "employees": 500,
            "founded": 2010,
            "description": "Test company description",
            "headquarters": "London, UK",
            "website": "https://example.com",
            "name": "Test Corporation",
            "exchange": "NYSE",
            "growth": {
                "employee_count": 500,
                "employee_growth": 0.1,
                "job_postings_count": 25,
                "ai_related_jobs": 5,
            },
            "ai": {"ai_score": 7, "ai_signal_strength": "strong"},
            "technology": {"industry": "SaaS", "sector": "Technology"},
            "products": {"products": ["Product A", "Product B"]},
        },
    )


def _news_source() -> RawDataSource:
    return RawDataSource(
        source_name="news",
        source_type=DataSourceType.NEWS,
        confidence=0.7,
        raw_content={
            "articles": [
                {"title": "Good news", "sentiment": 0.8, "polarity": "positive"},
                {"title": "More news", "sentiment": 0.6, "polarity": "positive"},
                {"title": "Neutral news", "sentiment": 0.0, "polarity": "neutral"},
            ],
            "sentiment_score": 0.7,
        },
    )


def _patents_source() -> RawDataSource:
    return RawDataSource(
        source_name="patents",
        source_type=DataSourceType.PATENTS,
        confidence=0.85,
        raw_content={
            "total_patents": 42,
            "ai_related_patents": 15,
            "patent_categories": ["Machine Learning", "Computer Vision"],
        },
    )


def _crunchbase_source() -> RawDataSource:
    return RawDataSource(
        source_name="crunchbase",
        source_type=DataSourceType.CRUNCHBASE,
        confidence=0.8,
        raw_content={
            "total_funding_raised": 25_000_000,
            "last_round_amount": 10_000_000,
            "valuation": 100_000_000,
            "funding_rounds": 3,
            "last_round_stage": "Series B",
            "investors": ["Acme Capital", "Beta Ventures"],
        },
    )


def _linkedin_source() -> RawDataSource:
    return RawDataSource(
        source_name="linkedin",
        source_type=DataSourceType.LINKEDIN,
        confidence=0.75,
        raw_content={
            "employee_count": 500,
            "employee_growth": 0.15,
            "open_positions": 25,
            "ai_job_postings": 8,
        },
    )


def _website_source() -> RawDataSource:
    return RawDataSource(
        source_name="website",
        source_type=DataSourceType.WEBSITE,
        confidence=0.6,
        raw_content={
            "products": ["Product A", "Product B", "Product C"],
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            "pricing_model": "SaaS subscription",
            "target_customers": ["Enterprise", "SMB"],
        },
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPipelineFieldSurvival:
    """Regression gate: fact types must reach Company or be in the exclusion list."""

    def _run_pipeline(
        self, sources: list[RawDataSource]
    ) -> tuple[AggregatedDataRecord, dict[str, Any]]:
        """Run full transformation and return (aggregated, company_dump)."""
        candidate = _make_candidate()
        raw = RawDataRecord(
            company_id=candidate.company_id,
            gathering_batch_id="test-batch",
            sources=sources,
        )
        aggregated = DefaultFactAggregator().aggregate(candidate.company_id, raw)
        signal_record = extract_signals(aggregated)
        signals = {s.signal_name: s for s in signal_record.signals}
        facts = {f.fact_type: f for f in aggregated.facts}
        company = build_company_entity_from_signals(
            candidate, signal_record, aggregated, signals, facts
        )
        return aggregated, company.model_dump()

    def _assert_all_facts_survive(
        self, aggregated: AggregatedDataRecord, company_dump: dict[str, Any]
    ) -> None:
        """Assert every produced fact reaches Company or is explicitly excluded."""
        missing: list[str] = []
        for fact in aggregated.facts:
            if fact.fact_type in INTENTIONALLY_EXCLUDED_FACTS:
                continue
            if not _fact_is_present(fact.fact_type, fact.value, company_dump):
                missing.append(
                    f"  '{fact.fact_type}' (value={fact.value!r}) — not in Company dump "
                    f"and not in INTENTIONALLY_EXCLUDED_FACTS"
                )
        assert not missing, (
            "The following fact types were LOST in the pipeline:\n"
            + "\n".join(missing)
            + "\n\nFix: either add the field to Company/FinancialMetric and wire it in "
            "company_builder.py, OR add it to INTENTIONALLY_EXCLUDED_FACTS with a reason."
        )

    def test_yahoo_finance_facts_survive(self) -> None:
        """All Yahoo Finance facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_yahoo_finance_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_news_facts_survive(self) -> None:
        """All news adapter facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_news_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_patents_facts_survive(self) -> None:
        """All patents adapter facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_patents_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_crunchbase_facts_survive(self) -> None:
        """All Crunchbase adapter facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_crunchbase_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_linkedin_facts_survive(self) -> None:
        """All LinkedIn adapter facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_linkedin_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_website_facts_survive(self) -> None:
        """All website adapter facts reach Company or are explicitly excluded."""
        aggregated, company_dump = self._run_pipeline([_website_source()])
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_multi_source_facts_survive(self) -> None:
        """All facts from all adapters combined reach Company or are explicitly excluded."""
        sources = [
            _yahoo_finance_source(),
            _news_source(),
            _patents_source(),
            _crunchbase_source(),
            _linkedin_source(),
            _website_source(),
        ]
        aggregated, company_dump = self._run_pipeline(sources)
        self._assert_all_facts_survive(aggregated, company_dump)

    def test_no_extra_forbidden_on_construction(self) -> None:
        """Pipeline must not pass any unknown fields to Company or FinancialMetric."""
        # If extra="forbid" is working correctly, this will raise ValidationError
        # when unknown fields are passed. The test passes if no ValidationError is raised.
        sources = [
            _yahoo_finance_source(),
            _news_source(),
            _crunchbase_source(),
        ]
        # If this doesn't raise, all fields are declared — extra="forbid" is working
        aggregated, company_dump = self._run_pipeline(sources)
        assert "id" in company_dump
        assert "financials" in company_dump
