from datetime import datetime, timezone
from typing import Any

from loguru import logger

from solstein.data.connectors.sec_edgar_connector import SECEdgarConnector as SECConnector
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.refresh import BaseRefreshConnector


class SECEDGARRefreshConnector(BaseRefreshConnector):
    """SEC EDGAR refresh connector for incremental financial data updates."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            source_name="sec_edgar",
            source_type="financial",
            db_manager=db_manager,
            confidence=0.95,  # SEC is authoritative source
        )
        self.sec_connector: SECConnector = SECConnector()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch financial facts from SEC EDGAR for companies."""
        logger.info(f"Fetching SEC EDGAR facts for {len(company_ids)} companies")
        facts = []

        if end_date is None or start_date is None:
            end_date = datetime.now(timezone.utc)
            start_date = end_date.replace(year=end_date.year - 3)

        for company_id in company_ids:
            try:
                # Extract ticker from company_id (assuming format: ticker-<name>)
                ticker = company_id.split("-")[0]

                # Fetch 10-K filings for the last 3 years
                for year in range(end_date.year, start_date.year - 1, -1):
                    try:
                        # Fetch 10-K filing
                        result = self.sec_connector.fetch_filing(ticker, year, "10-K")

                        # Convert to fact format
                        fact = self._convert_filing_to_fact(result)
                        facts.append(fact)

                    except Exception as e:
                        logger.warning(f"Failed to fetch {ticker} {year} 10-K: {e}")
                        continue

                # Fetch 10-Q filings for the last quarter
                try:
                    current_year = datetime.now().year
                    current_quarter = (datetime.now().month - 1) // 3 + 1

                    for quarter in range(current_quarter, 0, -1):
                        # SEC EDGAR doesn't support quarter-based fetching directly,
                        # so we use the most recent filing available
                        result = self.sec_connector.fetch_filing(ticker, current_year, "10-Q")
                        fact = self._convert_filing_to_fact(result)
                        facts.append(fact)
                        break  # Only need most recent

                except Exception as e:
                    logger.warning(f"Failed to fetch {ticker} recent 10-Q: {e}")
                    continue

            except Exception as e:
                logger.error(f"Failed to process company {company_id}: {e}")
                continue

        return facts

    def _convert_filing_to_fact(self, filing: dict[str, Any]) -> dict[str, Any]:
        """Convert SEC EDGAR filing to fact dictionary."""
        # Extract financial metrics
        metrics = {
            "revenue": filing.get("revenue"),
            "gross_margin": filing.get("gross_margin"),
            "ebitda": filing.get("ebitda"),
            "cash_position": filing.get("cash_position"),
            "form_type": filing.get("form_type"),
            "filing_date": filing.get("filing_date"),
            "report_date": filing.get("report_date"),
        }

        # Create fact data
        fact_data = {
            "company_id": filing.get("ticker"),
            "fact_type": "financial_report",
            "value": metrics,
            "confidence": filing.get("confidence", 0.95),
            "extracted_at": datetime.now(),
            "source": "sec_edgar",
            "metadata": {
                "accession_no": filing.get("accession_no"),
                "form_type": filing.get("form_type"),
                "report_date": filing.get("report_date"),
                "filing_date": filing.get("filing_date"),
            },
        }

        return fact_data

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        """Filter SEC EDGAR facts to only return changed data since last refresh."""
        filtered_facts = []

        for fact in facts:
            # Check if report_date is newer than last refresh
            report_date = fact["value"].get("report_date")
            if report_date:
                try:
                    report_dt = datetime.fromisoformat(report_date)
                    if report_dt > since:
                        filtered_facts.append(fact)
                except Exception:
                    # If date parsing fails, include the fact
                    filtered_facts.append(fact)
            else:
                # No report_date, include the fact
                filtered_facts.append(fact)

        return filtered_facts

    async def _fact_exists(self, company_id: str, fact_type: str) -> bool:
        """Check if a financial fact already exists for company_id."""
        # For SEC EDGAR, we check by company_id and fact_type
        async with self.db_manager.session() as session:
            result = await session.execute(
                """
                SELECT COUNT(*) 
                FROM facts 
                WHERE company_id = :cid 
                AND fact_type = :ft 
                AND source = 'sec_edgar'
                """,
                {"cid": company_id, "ft": fact_type},
            )
            return result.fetchone()[0] > 0
