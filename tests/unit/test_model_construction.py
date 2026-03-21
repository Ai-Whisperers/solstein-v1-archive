"""Model construction smoke tests — Phase 0 enforcement gate.

Instantiates every core domain model with correct field names.
If these fail, schema drift has re-occurred.
"""

from datetime import datetime, timezone

import pytest

from solstein.domain.models import (
    AggregatedFact,
    Company,
    DataSourceType,
    FinancialMetric,
    RawDataSource,
    SignalExtraction,
)


def test_financial_metric_with_revenue():
    fm = FinancialMetric(revenue=1_000_000.0)
    assert fm.revenue == 1_000_000.0


def test_financial_metric_with_employees():
    fm = FinancialMetric(employees=500)
    assert fm.employees == 500


def test_financial_metric_allow_empty():
    fm = FinancialMetric(allow_empty_primary=True)
    assert fm.revenue is None
    assert fm.employees is None


def test_financial_metric_requires_primary():
    with pytest.raises(Exception):
        FinancialMetric()  # no revenue, no employees, allow_empty_primary=False


def test_company_minimal():
    c = Company(id="test-co", name="Test Company")
    assert c.id == "test-co"
    assert c.name == "Test Company"
    assert c.financials is not None  # default_factory sets allow_empty_primary=True


def test_company_with_financials():
    fm = FinancialMetric(revenue=500_000.0)
    c = Company(id="test-co2", name="Test Co 2", financials=fm)
    assert c.financials.revenue == 500_000.0


def test_raw_data_source_minimal():
    rds = RawDataSource(
        source_type=DataSourceType.NEWS,
        source_name="TechCrunch",
        raw_content="Article text here",
    )
    assert rds.source_name == "TechCrunch"
    assert rds.url is None


def test_raw_data_source_full():
    rds = RawDataSource(
        source_type=DataSourceType.NEWS,
        source_name="Reuters",
        raw_content="Full article",
        url="https://reuters.com/article",
        publication_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        metadata={"company_name": "Acme", "content_hash": "abc123"},
    )
    assert rds.url == "https://reuters.com/article"
    assert rds.metadata["company_name"] == "Acme"


def test_aggregated_fact_minimal():
    af = AggregatedFact(fact_type="revenue", value=1_000_000.0)
    assert af.fact_type == "revenue"
    assert af.value == 1_000_000.0
    assert af.sources_used == []


def test_aggregated_fact_with_sources():
    af = AggregatedFact(
        fact_type="employees",
        value=250,
        confidence=0.9,
        sources_used=["LinkedIn", "Companies House"],
    )
    assert len(af.sources_used) == 2
    assert af.confidence == 0.9


def test_signal_extraction_minimal():
    se = SignalExtraction(
        signal_name="revenue_growth",
        signal_value=0.25,
        calculation_method="direct_extraction",
    )
    assert se.signal_name == "revenue_growth"
    assert se.calculation_method == "direct_extraction"


def test_signal_extraction_full():
    se = SignalExtraction(
        signal_name="ai_maturity",
        signal_value="Strong",
        signal_confidence=0.85,
        source_facts=["ai_products", "ai_patents"],
        calculation_method="enum_classification",
        reasoning="Multiple AI products detected across 2 sources.",
    )
    assert se.signal_confidence == 0.85
    assert len(se.source_facts) == 2


def test_data_source_type_web_search_exists():
    """Regression test for ISSUE-224 — DataSourceType.WEB_SEARCH must exist."""
    assert DataSourceType.WEB_SEARCH == "web_search"
