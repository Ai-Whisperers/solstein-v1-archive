from __future__ import annotations

import os

import httpx


class CompaniesHouseNotConfiguredError(RuntimeError):
    pass


class CompaniesHouseCompanyNotFoundError(RuntimeError):
    pass


class CompaniesHouseConnector:
    DEFAULT_API_BASE: str = "https://api.company-information.service.gov.uk"
    DEFAULT_CONFIDENCE: float = 0.93

    def __init__(
        self,
        api_key: str | None = None,
        *,
        api_base: str | None = None,
        user_agent: str | None = None,
    ):
        self.api_key: str | None = api_key or os.getenv("COMPANIES_HOUSE_API_KEY")
        self.api_base: str = api_base or self.DEFAULT_API_BASE
        self.user_agent: str = user_agent or "Solstein/0.1 (contact: contact@ai-whisperers.com)"

    def search_company_by_name(self, company_name: str) -> str:
        if not company_name.strip():
            raise ValueError("company_name is required")

        data = self._get_json(
            "/search/companies",
            params={"q": company_name, "items_per_page": "5"},
        )
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise CompaniesHouseCompanyNotFoundError(f"Company not found: {company_name!r}")

        first = items[0]
        if not isinstance(first, dict):
            raise RuntimeError("Unexpected Companies House response shape")

        company_number = first.get("company_number")
        if not isinstance(company_number, str) or not company_number.strip():
            raise RuntimeError("Missing company_number in Companies House response")

        return company_number

    def fetch_company_details(self, company_number: str) -> dict[str, object]:
        if not company_number.strip():
            raise ValueError("company_number is required")

        data = self._get_json(f"/company/{company_number}")
        return dict(data)

    def get_company_metrics(self, company_number: str) -> dict[str, object]:
        company_profile = self.fetch_company_details(company_number)
        metrics = self._extract_metrics(company_profile)
        metrics["company_number"] = company_number
        metrics["confidence"] = self.DEFAULT_CONFIDENCE
        return metrics

    def _get_json(self, path: str, *, params: dict[str, str] | None = None) -> dict[str, object]:
        if not self.api_key:
            raise CompaniesHouseNotConfiguredError("Missing COMPANIES_HOUSE_API_KEY")

        url = f"{self.api_base}{path}"
        try:
            response = httpx.get(
                url,
                params=params,
                auth=(self.api_key, ""),
                headers={"User-Agent": self.user_agent},
                timeout=15.0,
            )
        except Exception as e:
            raise RuntimeError(f"Companies House request failed: {path}") from e

        if response.status_code == 401:
            raise CompaniesHouseNotConfiguredError("Companies House API key rejected (401)")
        if response.status_code == 404:
            raise CompaniesHouseCompanyNotFoundError(f"Resource not found: {path}")
        if response.status_code == 429:
            raise RuntimeError("Companies House rate limit (429)")
        if response.status_code >= 500:
            raise RuntimeError(f"Companies House server error ({response.status_code})")

        try:
            data = response.json()
        except Exception as e:
            raise RuntimeError("Companies House invalid JSON response") from e

        if not isinstance(data, dict):
            raise RuntimeError("Companies House unexpected response type")

        return data

    def _extract_metrics(self, company_profile: dict[str, object]) -> dict[str, object]:
        accounts = company_profile.get("accounts")
        confirmation = company_profile.get("confirmation_statement")

        accounts_obj = accounts if isinstance(accounts, dict) else {}
        confirmation_obj = confirmation if isinstance(confirmation, dict) else {}

        last_accounts = accounts_obj.get("last_accounts")
        last_accounts_obj = last_accounts if isinstance(last_accounts, dict) else {}
        next_accounts = accounts_obj.get("next_accounts")
        next_accounts_obj = next_accounts if isinstance(next_accounts, dict) else {}

        sic_codes = company_profile.get("sic_codes")
        if isinstance(sic_codes, list):
            sic_codes_out: list[str] = [str(x) for x in sic_codes if isinstance(x, str)]
        else:
            sic_codes_out = []

        return {
            "company_name": company_profile.get("company_name"),
            "company_status": company_profile.get("company_status"),
            "jurisdiction": company_profile.get("jurisdiction"),
            "company_type": company_profile.get("type"),
            "incorporation_date": company_profile.get("date_of_creation"),
            "sic_codes": sic_codes_out,
            "accounts_last_period_start": last_accounts_obj.get("period_start_on"),
            "accounts_last_period_end": last_accounts_obj.get("period_end_on"),
            "accounts_last_type": last_accounts_obj.get("type"),
            "accounts_next_due": next_accounts_obj.get("due_on"),
            "accounts_next_overdue": next_accounts_obj.get("overdue"),
            "confirmation_next_due": confirmation_obj.get("next_due"),
            "confirmation_overdue": confirmation_obj.get("overdue"),
        }
