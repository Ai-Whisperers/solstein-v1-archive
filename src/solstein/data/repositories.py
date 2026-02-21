
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from ..config import get_settings
from ..core.repositories import CompanyFilter, CompanyRepository
from ..data.loaders import CompetitorDataLoader
from ..domain.models import Company, FinancialMetric


class JsonFileRepository(CompanyRepository):
    """
    Repository implementation that reads from JSON files.
    """

    def __init__(self, data_dir: Path | None = None):
        self.settings = get_settings()
        self.data_dir = data_dir or self.settings.data.data_dir
        self._loader = CompetitorDataLoader(data_dir=self.data_dir)

    def _to_domain(self, raw_company: Company) -> Company:
        """Helper to ensure domain entity is returned (currently redundant for JSON loader but good for consistency)."""  # noqa: E501
        return raw_company

    def get_all(
        self,
        limit: int | None = None,
        offset: int = 0,
        filters: CompanyFilter | None = None,
    ) -> list[Company]:
        """Retrieve all companies from JSON storage."""
        # Load all (JSON doesn't support server-side pagination efficiently in this dummy impl)  # noqa: E501
        all_companies = self._loader.load_companies()

        if filters:
            filtered_results = []
            for company in all_companies:
                match = True
                if filters.tier and company.tier != filters.tier:
                    match = False
                if (
                    filters.industry
                    and company.industry
                    and filters.industry.lower() not in company.industry.lower()
                ):
                    match = False
                if filters.min_revenue and (
                    not company.financials.revenue
                    or company.financials.revenue < filters.min_revenue
                ):
                    match = False
                if filters.classification and company.classification != filters.classification:  # noqa: E501
                    match = False

                if match:
                    filtered_results.append(company)
            all_companies = filtered_results

        # Apply pagination
        return all_companies[offset : (offset + limit) if limit else None]

    def get_by_id(self, company_id: str) -> Company | None:
        """Retrieve a company by ID."""
        all_companies = self._loader.load_companies()
        for c in all_companies:
            if c.id == company_id:
                return c
        return None

    def save(self, company: Company) -> Company:
        """Simulate saving to JSON."""
        logger.info(f"Persisted company profile for {company.name} (Simulation)")
        return company

    def delete(self, company_id: str) -> bool:
        """Simulate deletion."""
        logger.info(f"Deleted company {company_id} (Simulation)")
        return True

    def search(self, query: str, field: str = "name") -> list[Company]:
        """Search companies in memory."""
        all_companies = self._loader.load_companies()
        query_lower = query.lower()
        results = []
        for c in all_companies:
            val = getattr(c, field, None)
            if val and isinstance(val, str) and query_lower in val.lower():
                results.append(c)
        return results


class SupabaseRepository(CompanyRepository):
    """
    Repository implementation that reads and writes from Supabase PostgreSQL.
    """

    def __init__(self) -> None:
        from ..core.supabase_client import get_supabase
        self.client = get_supabase()
        self.table_name = "companies"

    def _to_domain(self, record: dict[str, Any]) -> Company:
        """Helper to convert Supabase dict to Domain Entity."""
        data = record.copy()

        # Combine flat columns and JSONB legacy data
        fin_data = data.pop("financials", {}) or {}
        if isinstance(fin_data, str):
            fin_data = {} # Failsafe

        for key in ["revenue", "growth_rate", "profit_margin", "valuation", "employees", "funding_raised"]:  # noqa: E501
            if key in data:
                val = data.pop(key)
                if val is not None:
                    fin_data[key] = val

        financials = FinancialMetric(**fin_data)
        return Company(financials=financials, **data)

    def _to_record(self, company: Company) -> dict[str, Any]:
        data = company.model_dump()

        # Extract financials to flat competitive columns for Supabase
        fin_data = data.get("financials", {})
        for key in ["revenue", "growth_rate", "profit_margin", "valuation", "employees", "funding_raised"]:  # noqa: E501
            if key in fin_data:
                data[key] = fin_data[key]

        # Manually fix non-JSON serializable types
        if isinstance(data.get("last_updated"), datetime):
            data["last_updated"] = data["last_updated"].isoformat()

        # Fix Enums
        if data.get("tier"):
            data["tier"] = str(data["tier"])
        if data.get("threat_level"):
            data["threat_level"] = str(data["threat_level"])
        if data.get("ai_maturity"):
            data["ai_maturity"] = str(data["ai_maturity"])

        # Recursive fix for nested datetimes (like in ScoringExplanation)
        def json_safe(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: json_safe(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [json_safe(i) for i in obj]
            if isinstance(obj, datetime):
                return obj.isoformat()
            from enum import Enum
            if isinstance(obj, Enum):
                return obj.value
            return obj

        from typing import cast
        return cast("dict[str, Any]", json_safe(data))

    def get_all(
        self,
        limit: int | None = None,
        offset: int = 0,
        filters: CompanyFilter | None = None,
    ) -> list[Company]:
        """Retrieve all companies from Supabase, applying optional filters."""
        query = self.client.table(self.table_name).select("*")

        if filters:
            if filters.tier:
                query = query.eq("tier", filters.tier)
            if filters.industry:
                query = query.ilike("industry", f"%{filters.industry}%")
            if filters.classification:
                query = query.eq("classification", filters.classification)
            if filters.min_revenue:
                # Proper cast for JSONB field
                query = query.filter("financials->>revenue", "gte", str(filters.min_revenue))  # noqa: E501
            if filters.min_growth_score:
                query = query.gte("growth_score", filters.min_growth_score)
            if filters.max_growth_score:
                query = query.lte("growth_score", filters.max_growth_score)

        # Pagination
        if limit is not None:
            query = query.range(offset, offset + limit - 1)
        else:
            query = query.range(offset, offset + 1000) # Default safety  # noqa: E501

        response = query.execute()
        from typing import cast
        return [self._to_domain(cast("dict[str, Any]", record)) for record in response.data]  # noqa: E501

    def get_by_id(self, company_id: str) -> Company | None:
        """Retrieve a specific company by ID."""
        response = self.client.table(self.table_name).select("*").eq("id", company_id).execute()  # noqa: E501
        if not response.data:
            return None
        from typing import cast
        return self._to_domain(cast("dict[str, Any]", response.data[0]))

    def save(self, company: Company) -> Company:
        """Persist a company to Supabase (Upsert)."""
        record = self._to_record(company)
        self.client.table(self.table_name).upsert(record).execute()
        logger.info(f"Persisted company profile to Supabase: {company.name}")
        return company

    def delete(self, company_id: str) -> bool:
        """Delete a company from Supabase."""
        response = self.client.table(self.table_name).delete().eq("id", company_id).execute()  # noqa: E501
        logger.info(f"Deleted company {company_id} from Supabase")
        return len(response.data) > 0

    def search(self, query: str, field: str = "name") -> list[Company]:
        """Search companies using Supabase ilike."""
        response = self.client.table(self.table_name).select("*").ilike(field, f"%{query}%").execute()  # noqa: E501
        from typing import cast
        return [self._to_domain(cast("dict[str, Any]", record)) for record in response.data]  # noqa: E501
