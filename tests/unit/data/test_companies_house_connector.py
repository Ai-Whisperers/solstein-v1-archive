import pytest

from solstein.data.connectors.companies_house_connector import (
    CompaniesHouseCompanyNotFoundError,
    CompaniesHouseConnector,
    CompaniesHouseNotConfiguredError,
)


def test_companies_house_connector_reads_api_key_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("COMPANIES_HOUSE_API_KEY", "env-key")
    connector = CompaniesHouseConnector(api_key=None)
    assert connector.api_key == "env-key"


def test_companies_house_connector_param_overrides_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("COMPANIES_HOUSE_API_KEY", "env-key")
    connector = CompaniesHouseConnector(api_key="param-key")
    assert connector.api_key == "param-key"


def test_companies_house_connector_defaults_api_base():
    connector = CompaniesHouseConnector(api_key="x")
    assert connector.api_base == CompaniesHouseConnector.DEFAULT_API_BASE


def test_search_company_by_name_validates_input():
    connector = CompaniesHouseConnector(api_key="x")
    with pytest.raises(ValueError):
        connector.search_company_by_name("  ")


def test_fetch_company_details_validates_input():
    connector = CompaniesHouseConnector(api_key="x")
    with pytest.raises(ValueError):
        connector.fetch_company_details(" ")


def test_search_company_by_name_requires_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)
    connector = CompaniesHouseConnector(api_key=None)
    with pytest.raises(CompaniesHouseNotConfiguredError):
        connector.search_company_by_name("Acme")


def test_search_company_by_name_happy_path(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/search/companies?q=Acme&items_per_page=5",
        json={"items": [{"company_number": "01234567"}]},
        status_code=200,
    )
    assert connector.search_company_by_name("Acme") == "01234567"


def test_search_company_by_name_not_found(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/search/companies?q=Nope&items_per_page=5",
        json={"items": []},
        status_code=200,
    )
    with pytest.raises(CompaniesHouseCompanyNotFoundError):
        connector.search_company_by_name("Nope")


def test_fetch_company_details_404(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/company/01234567",
        json={"error": "not found"},
        status_code=404,
    )
    with pytest.raises(CompaniesHouseCompanyNotFoundError):
        connector.fetch_company_details("01234567")


def test_get_company_metrics_extracts_fields(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/company/01234567",
        json={
            "company_name": "ACME LTD",
            "company_status": "active",
            "jurisdiction": "england-wales",
            "type": "ltd",
            "date_of_creation": "2020-01-01",
            "sic_codes": ["62020"],
            "accounts": {
                "last_accounts": {
                    "period_start_on": "2023-01-01",
                    "period_end_on": "2023-12-31",
                    "type": "full",
                },
                "next_accounts": {"due_on": "2024-09-30", "overdue": False},
            },
            "confirmation_statement": {"next_due": "2024-06-30", "overdue": False},
        },
        status_code=200,
    )
    metrics = connector.get_company_metrics("01234567")
    assert metrics["company_number"] == "01234567"
    assert metrics["company_name"] == "ACME LTD"
    assert metrics["accounts_last_type"] == "full"
    assert metrics["accounts_next_overdue"] is False
    assert metrics["sic_codes"] == ["62020"]
    assert metrics["confidence"] == pytest.approx(connector.DEFAULT_CONFIDENCE)


def test_get_company_metrics_handles_missing_optional_sections(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/company/76543210",
        json={"company_name": "NO ACCOUNTS LTD", "company_status": "active"},
        status_code=200,
    )
    metrics = connector.get_company_metrics("76543210")
    assert metrics["company_name"] == "NO ACCOUNTS LTD"
    assert metrics["accounts_last_period_end"] is None
    assert metrics["confirmation_next_due"] is None


def test_get_company_metrics_dissolved_company(httpx_mock):
    connector = CompaniesHouseConnector(api_key="k")
    httpx_mock.add_response(
        method="GET",
        url="https://api.company-information.service.gov.uk/company/99999999",
        json={"company_name": "DISSOLVED LTD", "company_status": "dissolved"},
        status_code=200,
    )
    metrics = connector.get_company_metrics("99999999")
    assert metrics["company_status"] == "dissolved"
