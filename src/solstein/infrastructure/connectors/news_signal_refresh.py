import asyncio
from datetime import datetime, timezone
from typing import Any

from loguru import logger
from sqlalchemy import text

from solstein.data.connectors.news_signal_detector import NewsSignalDetector
from solstein.infrastructure.database import DatabaseManager
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
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch market signals from news articles."""
        logger.info(f"Fetching news signals for {len(company_ids)} companies")
        facts = []

        for company_id in company_ids:
            try:
                # Extract company name from company_id (assuming format: name-<ticker>)
                company_name = company_id.split("-")[0]

                try:
                    # Detect all signal types
                    funding_signals, partnership_signals, key_hire_signals = await asyncio.gather(
                        self.news_detector.detect_funding_signal(company_name),
                        self.news_detector.detect_partnership_signal(company_name),
                        self.news_detector.detect_key_hire_signal(company_name),
                    )

                    # Convert all signals to facts
                    for signal in funding_signals + partnership_signals + key_hire_signals:
                        fact = self._convert_signal_to_fact(signal)
                        facts.append(fact)

                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to fetch signals for {company_name}: {e}")
                    continue

            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to process company {company_id}: {e}")
                continue

        return facts

    def _convert_signal_to_fact(self, signal: Any) -> dict[str, Any]:
        """Convert news signal (Signal dataclass) to fact dictionary."""
        raw = getattr(signal, "raw_data", {}) or {}
        # Extract signal metrics using attribute access for Signal dataclass fields,
        # falling back to raw_data for fields not on the dataclass
        signal_metrics = {
            "signal_type": signal.signal_type,
            "title": raw.get("title"),
            "description": signal.description,
            "source": signal.source,
            "url": raw.get("url"),
            "published_at": raw.get("published_at"),
            "signal_date": raw.get("signal_date"),
        }

        # Create fact data
        fact_data = {
            "company_id": signal.company_name,
            "fact_type": "market_signal",
            "value": signal_metrics,
            "confidence": getattr(signal, "confidence", 0.72),
            "extracted_at": datetime.now(tz=timezone.utc),
            "source": "news_signal",
            "metadata": {
                "signal_type": signal.signal_type,
                "source": signal.source,
                "url": raw.get("url"),
                "published_at": raw.get("published_at"),
                "signal_date": raw.get("signal_date"),
            },
        }

        return fact_data

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
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
                except Exception:  # noqa: BLE001
                    # If date parsing fails, include the fact
                    filtered_facts.append(fact)
            else:
                # No signal_date, include the fact
                filtered_facts.append(fact)

        return filtered_facts

    async def _fact_exists(self, company_id: str, fact_type: str) -> bool:
        """Check if a market signal fact already exists for company_id."""
        async with self.db_manager.get_session() as session:
            result = await session.execute(
                text("""
                SELECT COUNT(*)
                FROM facts
                WHERE company_id = :cid
                AND fact_type = :ft
                AND source = 'news_signal'
                """),
                {"cid": company_id, "ft": fact_type},
            )
            return result.fetchone()[0] > 0
