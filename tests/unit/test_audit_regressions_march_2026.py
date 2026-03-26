"""Regression tests for audit fixes applied in March 2026."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request

from solstein.adapters.enrichment.funding_unified import FundingUnifiedAdapter
from solstein.adapters.enrichment.patents_unified import PatentsUnifiedAdapter
from solstein.adapters.enrichment.web_search_unified import WebSearchUnifiedAdapter
from solstein.api.schemas.enrichment import BatchEnrichmentRequest
from solstein.domain.models import DataSourceType
from solstein.infrastructure.connectors.funding_refresh import FundingRefreshConnector
from solstein.infrastructure.connectors.global_market_refresh import GlobalMarketRefreshConnector
from solstein.infrastructure.connectors.linkedin_refresh import LinkedInRefreshConnector
from solstein.infrastructure.connectors.news_refresh import NewsRefreshConnector
from solstein.infrastructure.connectors.website_refresh import WebsiteRefreshConnector
from solstein.infrastructure.connectors.yahoo_finance_refresh import YahooFinanceRefreshConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.intelligence.deep_analyzer import DeepAnalysisGenerator, DeepAnalysisReport
from solstein.monitoring.business_metrics import BusinessMetricsCollector
from solstein.worker.base import FactIngestionPayload


@pytest.fixture
def mock_db_manager() -> MagicMock:
    return MagicMock(spec=DatabaseManager)


@pytest.mark.asyncio
async def test_funding_refresh_handles_missing_total_raised_without_crashing(mock_db_manager: MagicMock) -> None:
    connector = FundingRefreshConnector(mock_db_manager, crunchbase_key="test-key")
    connector.client.get_funding_data = AsyncMock(
        return_value=SimpleNamespace(
            total_raised=None,
            num_rounds=2,
            latest_round=None,
        )
    )

    facts = await connector.fetch_facts(["acme"])

    assert len(facts) == 1
    assert facts[0]["fact_type"] == "funding_summary"
    assert facts[0]["value"]["average_round_size"] == 0


@pytest.mark.asyncio
async def test_linkedin_refresh_treats_none_ai_related_positions_as_zero(mock_db_manager: MagicMock) -> None:
    connector = LinkedInRefreshConnector(mock_db_manager, news_api_key="test-key")
    connector.client.get_linkedin_data = MagicMock(
        return_value=SimpleNamespace(
            ai_related_positions=None,
        )
    )

    facts = await connector.fetch_facts(["acme"])

    assert len(facts) == 1
    assert facts[0]["fact_type"] == "hiring_signals"
    assert facts[0]["value"]["ai_related_positions"] == 0
    assert facts[0]["value"]["has_hiring_activity"] is False


@pytest.mark.asyncio
async def test_yahoo_finance_refresh_reads_company_research_nested_fields(mock_db_manager: MagicMock) -> None:
    connector = YahooFinanceRefreshConnector(mock_db_manager)
    connector.researcher = MagicMock()
    connector.researcher.research = MagicMock(
        return_value=SimpleNamespace(
            market_cap=123456789,
            pe_ratio=14.2,
            name="Acme Energy",
            employees=125,
            website="https://acme.example",
            headquarters="Berlin, Germany",
            currency="USD",
            exchange="NASDAQ",
            financials=SimpleNamespace(
                revenue=42_000_000.0,
                revenue_growth_yoy=0.25,
                profit_margin=0.18,
                ebitda=8_000_000.0,
                net_income=4_000_000.0,
            ),
            technology=SimpleNamespace(
                industry="Energy Software",
                sector="Software",
            ),
            growth=SimpleNamespace(
                employee_growth=0.10,
                job_postings_growth=0.15,
                ai_related_jobs=6,
            ),
        )
    )

    facts = await connector.fetch_facts(["ACME"])

    assert len(facts) == 4
    by_type = {fact["fact_type"]: fact for fact in facts}
    assert by_type["financial_metrics"]["value"]["revenue"] == 42_000_000.0
    assert by_type["financial_metrics"]["value"]["revenue_growth"] == 0.25
    assert by_type["growth_metrics"]["value"]["ai_related_jobs"] == 6
    assert by_type["company_profile"]["value"]["industry"] == "Energy Software"
    assert by_type["company_profile"]["value"]["headquarters"] == "Berlin, Germany"


def test_deep_analyzer_generate_from_dict_returns_report_object() -> None:
    generator = DeepAnalysisGenerator()

    report = generator.generate_from_dict(
        "Acme Energy",
        {
            "basic_info": {
                "description": "AI-native energy trading and analytics platform",
                "headquarters": "Berlin, Germany",
                "employees": 125,
                "website": "https://acme.example",
                "founded_year": 2019,
            },
            "data_sources": [
                {"url": "https://acme.example"},
                {"url": "https://docs.acme.example/platform"},
            ],
        },
    )

    assert isinstance(report, DeepAnalysisReport)
    assert report.company.name == "Acme Energy"
    assert isinstance(report.executive_assessment, str)
    assert isinstance(report.product_offering, str)
    assert isinstance(report.key_insights, list)
    assert report.key_insights


def test_fact_ingestion_payload_accepts_type_alias() -> None:
    payload = FactIngestionPayload.model_validate(
        {
            "company_id": "acme",
            "type": "market_metrics",
            "value": {"market_cap": 123},
            "confidence": 0.8,
        }
    )

    assert payload.company_id == "acme"
    assert payload.fact_type == "market_metrics"
    assert payload.confidence == 0.8


def test_fact_ingestion_payload_rejects_invalid_confidence() -> None:
    with pytest.raises(Exception):
        FactIngestionPayload.model_validate(
            {
                "company_id": "acme",
                "fact_type": "market_metrics",
                "value": {"market_cap": 123},
                "confidence": 1.5,
            }
        )


@pytest.mark.asyncio
async def test_global_market_refresh_handles_missing_currency_without_crashing(
    mock_db_manager: MagicMock,
) -> None:
    connector = GlobalMarketRefreshConnector(mock_db_manager)
    connector.loader.get_stock_data = MagicMock(
        return_value=SimpleNamespace(
            ticker="ACME",
            exchange="NASDAQ",
            source_currency=None,
            price_date="2026-03-25",
            current_price=12.5,
            market_cap=100_000_000,
            eps_ttm=1.2,
            revenue=42_000_000,
        )
    )

    facts = await connector.fetch_facts(["ACME"])

    assert len(facts) == 2
    assert facts[0]["value"]["market_cap"] == 100_000_000
    assert facts[0]["metadata"]["source_currency"] is None


@pytest.mark.asyncio
async def test_news_refresh_skips_none_coverage_without_attribute_errors(mock_db_manager: MagicMock) -> None:
    connector = NewsRefreshConnector(mock_db_manager, news_api_key="test-key")
    connector.client.get_news = MagicMock(return_value=None)

    facts = await connector.fetch_facts(["acme"])

    assert facts == []


@pytest.mark.asyncio
async def test_website_refresh_fetches_facts_when_websites_are_available(mock_db_manager: MagicMock) -> None:
    connector = WebsiteRefreshConnector(mock_db_manager)
    connector.client.scrape_company_website = AsyncMock(
        return_value=SimpleNamespace(
            main_products=["Grid AI"],
            tech_stack=["Python", "Postgres"],
        )
    )

    facts = await connector.fetch_facts_with_websites({"acme": "https://acme.example"})

    assert len(facts) == 2
    assert facts[0]["fact_type"] == "website_products"
    assert facts[1]["fact_type"] == "tech_stack"


def test_funding_unified_adapter_uses_valid_datasource_type() -> None:
    adapter = FundingUnifiedAdapter(crunchbase_api_key=None)

    raw = adapter.enrich(company_id="acme", company_name="Acme")

    assert raw.source_type == DataSourceType.CRUNCHBASE


def test_web_search_unified_adapter_uses_valid_datasource_type() -> None:
    adapter = WebSearchUnifiedAdapter()

    assert adapter.source_type == DataSourceType.EXA_SEARCH


def test_patents_unified_discover_builds_valid_discovery_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "solstein.adapters.enrichment.patents_unified.search_company_patents",
        MagicMock(
            return_value=SimpleNamespace(
                total_patents=3,
                ai_related_patents=1,
                recent_patents=[],
                top_categories=["ai"],
                source="uspto_peds",
            )
        ),
    )
    adapter = PatentsUnifiedAdapter()

    candidates = adapter.discover(market="energy software", seed_company="Acme", max_results=5)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.company_id
    assert candidate.market == "energy software"
    assert isinstance(candidate.source_links, list)


@pytest.mark.asyncio
async def test_batch_enrichment_partial_status_uses_schema_valid_partial(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMPANIES_HOUSE_API_KEY", "test-key")

    from solstein.api.routers import enrichment_batch as enrichment_batch_module

    request_data = BatchEnrichmentRequest(company_ids=["acme", "beta"], batch_size=2)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/companies/enrich/batch",
        "headers": [(b"x-client-id", b"test-client")],
        "client": ("127.0.0.1", 12345),
    }
    request = Request(scope)

    monkeypatch.setattr(enrichment_batch_module, "rate_limiter", SimpleNamespace(is_allowed=lambda _: True))
    monkeypatch.setattr(
        enrichment_batch_module,
        "input_validator",
        SimpleNamespace(validate_company_id=lambda _: (True, None)),
    )
    monkeypatch.setattr(
        enrichment_batch_module,
        "unified_loader",
        SimpleNamespace(
            enrich_batch=lambda companies, batch_size: [
                SimpleNamespace(id="acme", enrichment_errors=[]),
                SimpleNamespace(id="beta", enrichment_errors=["timeout"]),
            ]
        ),
    )

    response = await enrichment_batch_module.enrich_batch(request_data, request)

    assert response.status == "partial"
    assert response.failed_count == 1


@pytest.mark.asyncio
async def test_business_metrics_collector_uses_live_companyrecord_columns() -> None:
    class FakeResult:
        def __init__(self, scalar_value=None, rows=None):
            self._scalar_value = scalar_value
            self._rows = rows or []

        def scalar(self):
            return self._scalar_value

        def fetchall(self):
            return self._rows

    session = AsyncMock()
    session.execute = AsyncMock(
        side_effect=[
            FakeResult(scalar_value=5),
            FakeResult(rows=[("lead", 3), (None, 2)]),
            FakeResult(rows=[("Tier 1", 2), (None, 3)]),
            FakeResult(scalar_value=7.4),
            FakeResult(scalar_value=4),
        ]
    )

    metrics = await BusinessMetricsCollector(session).collect_company_metrics()

    assert metrics.total == 5
    assert metrics.avg_data_quality == 7.4
    assert metrics.processed_per_hour == 4
    assert metrics.by_classification["unknown"] == 2
