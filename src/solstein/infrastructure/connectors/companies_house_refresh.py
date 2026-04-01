from datetime import datetime, timezone
from typing import Any

from loguru import logger
from sqlalchemy import text

from solstein.data.connectors.companies_house_connector import CompaniesHouseConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.refresh import BaseRefreshConnector


class CompaniesHouseRefreshConnector(BaseRefreshConnector):
    """Companies House refresh connector for UK company data updates."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            source_name="companies_house",
            source_type="corporate_profile",
            db_manager=db_manager,
            confidence=0.93,  # Companies House is authoritative source
        )
        self.ch_connector: CompaniesHouseConnector = CompaniesHouseConnector()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch company profile facts from Companies House."""
        logger.info(f"Fetching Companies House facts for {len(company_ids)} companies")
        facts = []

        for company_id in company_ids:
            try:
                # Companies House company numbers are the IDs
                company_number = company_id

                try:
                    metrics = self.ch_connector.get_company_metrics(company_number)

                    # Convert to fact format
                    fact = self._convert_metrics_to_fact(metrics)
                    facts.append(fact)

                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to fetch {company_number}: {e}")
                    continue

            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to process company {company_id}: {e}")
                continue

        return facts

    def _convert_metrics_to_fact(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Convert Companies House metrics to fact dictionary."""
        # Extract profile metrics
        profile_metrics = {
            "company_name": metrics.get("company_name"),
            "company_status": metrics.get("company_status"),
            "jurisdiction": metrics.get("jurisdiction"),
            "company_type": metrics.get("company_type"),
            "incorporation_date": metrics.get("incorporation_date"),
            "sic_codes": metrics.get("sic_codes"),
            "accounts_last_period_start": metrics.get("accounts_last_period_start"),
            "accounts_last_period_end": metrics.get("accounts_last_period_end"),
            "accounts_last_type": metrics.get("accounts_last_type"),
            "accounts_next_due": metrics.get("accounts_next_due"),
            "accounts_next_overdue": metrics.get("accounts_next_overdue"),
            "confirmation_next_due": metrics.get("confirmation_next_due"),
            "confirmation_overdue": metrics.get("confirmation_overdue"),
        }

        # Create fact data
        fact_data = {
            "company_id": metrics.get("company_number"),
            "fact_type": "company_profile",
            "value": profile_metrics,
            "confidence": metrics.get("confidence", 0.93),
            "extracted_at": datetime.now(tz=timezone.utc),
            "source": "companies_house",
            "metadata": {
                "company_number": metrics.get("company_number"),
                "company_status": metrics.get("company_status"),
                "jurisdiction": metrics.get("jurisdiction"),
                "company_type": metrics.get("company_type"),
                "incorporation_date": metrics.get("incorporation_date"),
                "sic_codes": metrics.get("sic_codes"),
            },
        }

        return fact_data

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        """Filter Companies House facts to only return changed data since last refresh."""
        filtered_facts = []

        for fact in facts:
            # Check if any of the date fields are newer than last refresh
            value = fact["value"]
            date_fields = [
                value.get("incorporation_date"),
                value.get("accounts_last_period_start"),
                value.get("accounts_last_period_end"),
                value.get("accounts_next_due"),
                value.get("confirmation_next_due"),
            ]

            for date_str in date_fields:
                if date_str:
                    try:
                        fact_date = datetime.fromisoformat(date_str)
                        if fact_date > since:
                            filtered_facts.append(fact)
                            break
                    except Exception:  # noqa: BLE001
                        # If date parsing fails, include the fact
                        filtered_facts.append(fact)
                        break
            else:
                # No date fields or all parsing failed, include the fact
                filtered_facts.append(fact)

        return filtered_facts

    async def _fact_exists(self, company_id: str, fact_type: str) -> bool:
        """Check if a company profile fact already exists for company_id."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                text("""
                SELECT COUNT(*)
                FROM facts
                WHERE company_id = :cid
                AND fact_type = :ft
                AND source = 'companies_house'
                """),
                {"cid": company_id, "ft": fact_type},
            )
            return result.fetchone()[0] > 0
