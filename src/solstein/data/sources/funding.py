"""Funding data sources for Solstein."""

from __future__ import annotations

import requests
from loguru import logger

from .models import FundingData
from .news import NewsSource


class FundingSource:
    """Crunchbase and public funding data source."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def get_funding_data(self, company_name: str) -> FundingData:
        """
        Get funding data.

        Note: Crunchbase requires API key. This uses free sources.
        Alternative: Use PitchBook (paid), or manual research.
        """
        if not self.api_key:
            # Try using public sources
            return self._get_public_funding_data(company_name)

        # If API key provided, use Crunchbase API
        url = f"https://api.crunchbase.com/v4/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_crunchbase_data(data)
        except Exception as e:
            logger.error(f"Error fetching Crunchbase data: {e}")

        return FundingData(company_name=company_name)

    def _get_public_funding_data(self, company_name: str) -> FundingData:
        """Get funding data from public sources."""
        # This is limited - mainly just recent news about funding
        news_source = NewsSource()
        news = news_source.get_news(company_name, days_back=180)

        total_raised = None
        rounds = []

        for article in news.articles:
            title = article.title.lower()
            if "funding" in title or "raised" in title or "series" in title:
                rounds.append(
                    {
                        "title": article.title,
                        "date": article.published_at,
                        "source": article.source,
                    }
                )

        return FundingData(
            company_name=company_name,
            total_raised=total_raised,
            last_round_amount=None,
            last_round_date=None,
            last_round_stage=None,
            last_round_valuation=None,
            investors=[],
            num_rounds=len(rounds),
        )

    def _parse_crunchbase_data(self, data: dict) -> FundingData:
        """Parse Crunchbase API response."""
        props = data.get("properties", {})

        return FundingData(
            company_name=props.get("name", ""),
            total_raised=props.get("total_funding"),
            last_round_amount=props.get("last_funding_amount"),
            last_round_date=props.get("last_funded_at"),
            last_round_stage=props.get("last_funding_stage"),
            last_round_valuation=props.get("valuation"),
            investors=[],
            num_rounds=props.get("funding_rounds", 0),
        )
