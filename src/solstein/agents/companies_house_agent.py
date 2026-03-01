"""Companies House agent for UK company financial data.

Retrieves official financial data from UK Companies House registry
for UK-registered companies and their subsidiaries.
"""

import asyncio

from datetime import datetime, timezone

import requests

from ..domain.models import DataSourceType
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .resilience import COMPANIES_HOUSE_RETRY_CONFIG, CircuitBreaker, call_with_retry


class CompaniesHouseAgent(BaseDataGatheringAgent):
    """Agent for gathering data from UK Companies House."""

    def __init__(self):
        """Initialize Companies House agent."""
        super().__init__("CompaniesHouseAgent", DataSourceType.COMPANY_FILINGS)
        from solstein.config import get_settings
        settings = get_settings()
        self.api_key = settings.companies_house_api_key
        self.api_base = "https://api.company-information.service.gov.uk"
        self.headers = {"User-Agent": "Solstein-AI"}

        self.circuit_breaker = CircuitBreaker(failure_threshold=4, recovery_timeout=90.0, name="CompaniesHouseAPI")

    async def gather(self, company_name: str, context: dict) -> AgentTaskResult:
        """Gather Companies House data for a company."""
        start_time = datetime.now(timezone.utc)
        result = AgentTaskResult(
            agent_name=self.agent_name,
            source_type=self.source_type,
            success=False,
        )

        try:
            self.log_info(f"Starting Companies House research for {company_name}")

            if not self.api_key:
                self.log_warning("Companies House API not configured")
                result.coverage_gaps.append("Companies House API not configured")
                result.success = False
                result.error_message = "Companies House API not configured"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            company_num = await self._search_company_by_name(company_name)
            if not company_num:
                self.log_warning(f"Company not found in Companies House: {company_name}")
                result.coverage_gaps.append("Company not found in Companies House")
                result.success = False
                result.error_message = "Company not found in Companies House"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            company_data = await self._fetch_company_details(company_num)
            if not company_data:
                result.coverage_gaps.append("Could not fetch company details")
                result.success = False
                result.error_message = "Could not fetch company details from Companies House"
                result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
                return result

            raw_source = self._create_raw_source(
                raw_content=company_data,
                source_name=f"Companies House: {company_data.get('company_name', 'unknown')}",
                url=f"https://beta.companieshouse.gov.uk/company/{company_num}",
                confidence=0.99,
                extraction_method="companies_house_api",
                metadata={
                    "company_number": company_num,
                    "incorporation_date": company_data.get("date_of_creation"),
                    "status": company_data.get("company_status"),
                },
            )
            result.raw_sources.append(raw_source)

            financials_data = await self._fetch_latest_financials(company_num)
            if financials_data:
                raw_source = self._create_raw_source(
                    raw_content=financials_data,
                    source_name=f"Companies House Filings: {company_num}",
                    url=f"https://beta.companieshouse.gov.uk/company/{company_num}/filing-history",
                    confidence=0.99,
                    extraction_method="companies_house_filings",
                )
                result.raw_sources.append(raw_source)

            result.extracted_facts.extend(self._extract_facts_from_company_data(company_data, financials_data))

            result.success = True
            self.log_info(f"Successfully gathered Companies House data for {company_name}")

        except Exception as e:
            self.log_error(f"Error gathering Companies House data: {e}")
            result.error_message = str(e)
            result.success = False

        finally:
            result.execution_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return result

    async def _search_company_by_name(self, company_name: str) -> str | None:
        """Search for company by name and return company number."""
        self.log_info(f"Searching Companies House for: {company_name}")

        try:
            company_num = await call_with_retry(
                asyncio.to_thread,
                self._api_search_company,
                company_name,
                retry_config=COMPANIES_HOUSE_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"search_company[{company_name}]",
            )
            if company_num:
                self.log_info(f"Found company number: {company_num}")
            return company_num
        except Exception as e:
            self.log_error(f"Error searching company: {e}")
            return None

    def _api_search_company(self, company_name: str) -> str | None:
        """API call to search for company."""
        try:
            url = f"{self.api_base}/search/companies"
            params = {
                "q": company_name,
                "items_per_page": 10,
            }

            resp = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10,
                auth=(self.api_key or "", ""),
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    company_num = items[0].get("company_number")
                    self.log_info(f"Found company: {items[0].get('title')}")
                    return company_num
            else:
                self.log_warning(f"Search error {resp.status_code}")
        except Exception as e:
            self.log_warning(f"Error searching: {e}")

        return None

    async def _fetch_company_details(self, company_num: str) -> dict | None:
        """Fetch company details from Companies House."""
        self.log_info(f"Fetching company details: {company_num}")

        try:
            data = await call_with_retry(
                asyncio.to_thread,
                self._api_get_company,
                company_num,
                retry_config=COMPANIES_HOUSE_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"get_company[{company_num}]",
            )
            return data
        except Exception as e:
            self.log_error(f"Error fetching company details: {e}")
            return None

    def _api_get_company(self, company_num: str) -> dict | None:
        """API call to get company details."""
        try:
            url = f"{self.api_base}/company/{company_num}"

            resp = requests.get(
                url,
                headers=self.headers,
                timeout=10,
                auth=(self.api_key or "", ""),
            )
            if resp.status_code == 200:
                return resp.json()
            else:
                self.log_warning(f"Get company error {resp.status_code}")
        except Exception as e:
            self.log_warning(f"Error getting company: {e}")

        return None

    async def _fetch_latest_financials(self, company_num: str) -> dict | None:
        """Fetch latest financial filing."""
        self.log_info(f"Fetching financials for: {company_num}")

        try:
            data = await call_with_retry(
                asyncio.to_thread,
                self._api_get_financials,
                company_num,
                retry_config=COMPANIES_HOUSE_RETRY_CONFIG,
                circuit_breaker=self.circuit_breaker,
                name=f"get_financials[{company_num}]",
            )
            return data
        except Exception as e:
            self.log_error(f"Error fetching financials: {e}")
            return None

    def _api_get_financials(self, company_num: str) -> dict | None:
        """API call to get financial filing."""
        try:
            url = f"{self.api_base}/company/{company_num}/filing-history"
            params = {
                "category": "accounts",
                "items_per_page": 5,
            }

            resp = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10,
                auth=(self.api_key or "", ""),
            )
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                if items:
                    return {
                        "filings_found": len(items),
                        "latest_filing": items[0],
                    }
            else:
                self.log_warning(f"Get financials error {resp.status_code}")
        except Exception as e:
            self.log_warning(f"Error getting financials: {e}")

        return None

    def _extract_facts_from_company_data(self, company_data: dict, financials_data: dict | None) -> list:
        """Extract facts from Companies House data."""
        facts = []

        if company_data.get("company_name"):
            facts.append(
                self._create_fact(
                    fact_type="company_name",
                    value=company_data["company_name"],
                    confidence=0.99,
                    sources_used=["Companies House"],
                )
            )

        if company_data.get("registered_office_address"):
            address = company_data["registered_office_address"]
            country = address.get("country", "UK")
            facts.append(
                self._create_fact(
                    fact_type="headquarters",
                    value=country,
                    confidence=0.99,
                    sources_used=["Companies House"],
                )
            )

        if company_data.get("company_status"):
            facts.append(
                self._create_fact(
                    fact_type="company_status",
                    value=company_data["company_status"],
                    confidence=0.99,
                    sources_used=["Companies House"],
                )
            )

        if company_data.get("date_of_creation"):
            facts.append(
                self._create_fact(
                    fact_type="founding_date",
                    value=company_data["date_of_creation"],
                    confidence=0.99,
                    sources_used=["Companies House"],
                )
            )

        if company_data.get("sic_codes"):
            facts.append(
                self._create_fact(
                    fact_type="business_classification",
                    value=company_data["sic_codes"],
                    confidence=0.99,
                    sources_used=["Companies House"],
                )
            )

        if financials_data and financials_data.get("filings_found"):
            facts.append(
                self._create_fact(
                    fact_type="latest_filing_available",
                    value=True,
                    confidence=0.99,
                    sources_used=["Companies House Filings"],
                )
            )

        return facts
