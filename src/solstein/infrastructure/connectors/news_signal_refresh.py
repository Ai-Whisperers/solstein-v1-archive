from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from solstein.data.connectors.news_signal_detector import NewsSignalDetector


from solstein.infrastructure.refresh import BaseRefreshConnector


class NewsSignalRefreshConnector(BaseRefreshConnector):
    """News Signal refresh connector for market signal updates."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__(
            source_name="news_signal",
            source_type="market_signal",
            db_manager=db_manager,
            confidence=0.72,  # News signals have moderate confidence
        )
        self.news_detector: NewsSignalDetector = NewsSignalDetector()

    async def fetch_facts(
        self,
        company_ids: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch market signals from news articles."""
        logger.info(f"Fetching news signals for {len(company_ids)} companies")
        facts = []

        for company_id in company_ids:
            try:
                # Extract company name from company_id (assuming format: name-<ticker>)
                company_name = company_id.split("-")[0]

                try:
                    # Detect all signal types
                    funding_signals = self.news_detector.detect_funding_signal(company_name)
                    partnership_signals = self.news_detector.detect_partnership_signal(company_name)
                    key_hire_signals = self.news_detector.detect_key_hire_signal(company_name)

                    # Convert all signals to facts
                    for signal in funding_signals + partnership_signals + key_hire_signals:
                        fact = self._convert_signal_to_fact(signal)
                        facts.append(fact)

                except Exception as e:
                    logger.warning(f"Failed to fetch signals for {company_name}: {e}")
                    continue

            except Exception as e:
                logger.error(f"Failed to process company {company_id}: {e}")
                continue

        return facts

    def _convert_signal_to_fact(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert news signal to fact dictionary."""
        # Extract signal metrics
        signal_metrics = {
            "signal_type": signal.get("signal_type"),
            "title": signal.get("title"),
            "description": signal.get("description"),
            "source": signal.get("source"),
            "url": signal.get("url"),
            "published_at": signal.get("published_at"),
            "signal_date": signal.get("signal_date"),
        }

        # Create fact data
        fact_data = {
            "company_id": signal.get("company_name"),
            "fact_type": "market_signal",
            "value": signal_metrics,
            "confidence": signal.get("confidence", 0.72),
            "extracted_at": datetime.now(),
            "source": "news_signal",
            "metadata": {
                "signal_type": signal.get("signal_type"),
                "source": signal.get("source"),
                "url": signal.get("url"),
                "published_at": signal.get("published_at"),
                "signal_date": signal.get("signal_date"),
            },
        }

        return fact_data

    async def _filter_delta(self, facts: List[Dict[str, Any]], since: datetime) -> List[Dict[str, Any]]:
        """Filter news signals to only return changed data since last refresh."""
        filtered_facts = []

        for fact in facts:
            # Check if signal_date is newer than last refresh
            value = fact["value"]
            signal_date_str = value.get("signal_date")

            if signal_date_str:
                try:
                    signal_date = datetime.fromisoformat(signal_date_str)
                    if signal_date > since:
                        filtered_facts.append(fact)
                except Exception:
                    # If date parsing fails, include the fact
                    filtered_facts.append(fact)
            else:
                # No signal_date, include the fact
                filtered_facts.append(fact)

        return filtered_facts

    async def _fact_exists(self, company_id: str, fact_type: str) -> bool:
        """Check if a market signal fact already exists for company_id."""
        async with self.db_manager.session() as session:
            result = await session.execute(
                """
                SELECT COUNT(*) 
                FROM facts 
                WHERE company_id = :cid 
                AND fact_type = :ft 
                AND source = 'news_signal'
                """,
                {"cid": company_id, "ft": fact_type},
            )
            return result.fetchone()[0] > 0
