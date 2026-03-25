"""Regression tests for audit fixes applied in March 2026."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.infrastructure.connectors.funding_refresh import FundingRefreshConnector
from solstein.infrastructure.connectors.linkedin_refresh import LinkedInRefreshConnector
from solstein.infrastructure.connectors.yahoo_finance_refresh import YahooFinanceRefreshConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.intelligence.deep_analyzer import DeepAnalysisGenerator, DeepAnalysisReport
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
