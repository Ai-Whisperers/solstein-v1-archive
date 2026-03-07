"""LinkedIn data sources for Solstein."""

from __future__ import annotations

from .models import LinkedInData
from .news import NewsSource


class LinkedInSource:
    """LinkedIn hiring data source (estimates from news)."""

    def get_linkedin_data(self, company_name: str) -> LinkedInData:
        """
        Get LinkedIn hiring data.

        Note: LinkedIn has strict anti-scraping. Options:
        1. Use official LinkedIn API (requires partnership)
        2. Use third-party services (may violate ToS)
        3. Estimate from job postings elsewhere

        This returns placeholder - real implementation requires
        API integration or manual research.
        """
        # Try to find from news
        news_source = NewsSource()
        news = news_source.get_news(company_name, days_back=90)

        ai_related = 0
        for article in news.articles:
            title = article.title.lower()
            if any(w in title for w in ["hiring", "jobs", "recruit", "expansion"]):
                if any(w in title for w in ["ai", "engineer", "developer", "data"]):
                    ai_related += 1

        return LinkedInData(
            company_name=company_name,
            employee_count=None,
            employee_growth_pct=None,
            open_positions=None,
            ai_related_positions=ai_related,
            recent_hires=[],
            company_size=None,
        )
