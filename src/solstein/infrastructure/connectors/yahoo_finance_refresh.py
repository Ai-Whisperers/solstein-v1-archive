"""Yahoo Finance refresh connector for market data updates.

Uses yfinance to fetch real-time market data and financial metrics.
Implements incremental refresh with ticker-based delta detection.
"""

import asyncio
from datetime import datetime
from typing import Any

from loguru import logger

from solstein.data.company_research import CompanyResearcher
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.infrastructure.refresh import BaseRefreshConnector


class YahooFinanceRefreshConnector(BaseRefreshConnector):
    """Yahoo Finance refresh connector for market data and financial metrics.

    Fetches comprehensive company data including:
    - Financial metrics (revenue, profit margin, etc.)
    - Market data (market cap, P/E ratio, etc.)
    - Growth metrics (revenue growth, earnings growth)
    - Company profile (employees, industry, sector)

    Confidence: 0.88 (highly authoritative for market data)
    """

    def __init__(self, db_manager):
        super().__init__(
            source_name="yahoo_finance",
            source_type="market_data",
            db_manager=db_manager,
            confidence=0.88,
        )
        self.researcher = CompanyResearcher()

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch market data facts from Yahoo Finance.

        Args:
            company_ids: List of company tickers (e.g., ['AAPL', 'MSFT'])
            start_date: Not used (Yahoo Finance always returns current data)
            end_date: Not used

        Returns:
            List of fact dictionaries with market and financial data
        """
        logger.info(f"Fetching Yahoo Finance data for {len(company_ids)} companies")
        facts = []

        for ticker in company_ids:
            try:
                profile = await asyncio.to_thread(self.researcher.research, ticker)

                # Create facts for different metric categories
                facts.extend(self._convert_profile_to_facts(ticker, profile))

            except Exception as e:
                logger.warning(f"Failed to fetch Yahoo Finance data for {ticker}: {e}")
                continue

        return facts

    def _convert_profile_to_facts(self, ticker: str, profile) -> list[dict[str, Any]]:
        """Convert CompanyProfile to list of fact dictionaries."""
        facts = []
        timestamp = datetime.now()
        financials = getattr(profile, "financials", None)
        technology = getattr(profile, "technology", None)
        growth = getattr(profile, "growth", None)

        # Market data fact
        market_data = {
            "market_cap": profile.market_cap,
            "enterprise_value": getattr(profile, "enterprise_value", None),
            "pe_ratio": profile.pe_ratio,
            "forward_pe": getattr(profile, "forward_pe", None),
            "peg_ratio": getattr(profile, "peg_ratio", None),
            "price_to_book": getattr(profile, "price_to_book", None),
            "price_to_sales": getattr(profile, "price_to_sales", None),
        }

        facts.append(
            {
                "company_id": ticker,
                "fact_type": "market_metrics",
                "value": {k: v for k, v in market_data.items() if v is not None},
                "confidence": self.confidence,
                "extracted_at": timestamp,
                "source": self.source_name,
                "metadata": {
                    "ticker": ticker,
                    "currency": profile.currency,
                    "exchange": profile.exchange,
                },
            }
        )

        # Financial performance fact
        financial_data = {
            "revenue": getattr(financials, "revenue", None),
            "revenue_growth": getattr(financials, "revenue_growth_yoy", None),
            "profit_margin": getattr(financials, "profit_margin", None),
            "operating_margin": getattr(profile, "operating_margin", None),
            "ebitda": getattr(financials, "ebitda", None),
            "net_income": getattr(financials, "net_income", None),
            "eps": getattr(profile, "eps", None),
        }

        facts.append(
            {
                "company_id": ticker,
                "fact_type": "financial_metrics",
                "value": {k: v for k, v in financial_data.items() if v is not None},
                "confidence": self.confidence,
                "extracted_at": timestamp,
                "source": self.source_name,
                "metadata": {
                    "ticker": ticker,
                    "fiscal_year": getattr(profile, "fiscal_year", None),
                },
            }
        )

        # Growth metrics fact
        growth_data = {
            "employee_growth": getattr(growth, "employee_growth", None),
            "job_postings_growth": getattr(growth, "job_postings_growth", None),
            "ai_related_jobs": getattr(growth, "ai_related_jobs", None),
            "revenue_growth": getattr(financials, "revenue_growth_yoy", None),
        }

        facts.append(
            {
                "company_id": ticker,
                "fact_type": "growth_metrics",
                "value": {k: v for k, v in growth_data.items() if v is not None},
                "confidence": self.confidence,
                "extracted_at": timestamp,
                "source": self.source_name,
                "metadata": {"ticker": ticker},
            }
        )

        # Company profile fact
        profile_data = {
            "name": profile.name,
            "industry": getattr(technology, "industry", None),
            "sector": getattr(technology, "sector", None),
            "employees": profile.employees,
            "website": str(profile.website) if profile.website else None,
            "country": None,
            "headquarters": getattr(profile, "headquarters", None),
        }

        facts.append(
            {
                "company_id": ticker,
                "fact_type": "company_profile",
                "value": {k: v for k, v in profile_data.items() if v is not None},
                "confidence": self.confidence,
                "extracted_at": timestamp,
                "source": self.source_name,
                "metadata": {
                    "ticker": ticker,
                    "exchange": profile.exchange,
                },
            }
        )

        return facts

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        """Filter facts to only return changed data since last refresh.

        For Yahoo Finance, market data changes frequently, so we always
        return facts but use hash comparison in base class to detect
        actual value changes.
        """
        # Use parent class hash-based comparison
        return await super()._filter_delta(facts, since)

    def get_authority(self) -> SourceAuthority:
        """Return Yahoo Finance authority level."""
        return SourceAuthority.YAHOO_FINANCE

    def supports_incremental(self) -> bool:
        """Yahoo Finance supports incremental refresh via hash comparison."""
        return True
