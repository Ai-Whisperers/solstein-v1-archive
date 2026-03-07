"""Patent data sources for Solstein."""

from __future__ import annotations

import json

import requests
from loguru import logger

from .models import PatentData


class PatentSource:
    """PatentsView API data source."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self._base_url = "https://search.patentsview.org/api/v1"

    async def get_patent_data(self, company_name: str) -> PatentData:
        """
        Get patent data for a company using PatentsView API.

        Uses the PatentsView PatentSearch API to fetch patent information.
        API Docs: https://search.patentsview.org/docs/
        Rate limit: 45 requests/minute
        """
        if not self.api_key:
            logger.warning("PatentsView API key not configured")
            return self._empty_patent_data(company_name)

        ai_keywords = [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural network",
            "natural language processing",
            "computer vision",
            "nlp",
            "ml",
            "ai",
            "algorithm",
            "predictive model",
            "data science",
            "automation",
        ]

        try:
            headers = {"X-Api-Key": self.api_key}

            query = {
                "_text_any": {"assignee_organization": company_name},
            }

            params = {
                "q": json.dumps(query),
                "f": json.dumps(
                    [
                        "patent_id",
                        "patent_title",
                        "patent_date",
                        "patent_abstract",
                        "assignee_organization",
                        "inventor_first_name",
                        "inventor_last_name",
                    ]
                ),
                "s": json.dumps([{"patent_date": "desc"}]),
                "o": json.dumps({"size": 50}),
            }

            response = requests.get(
                f"{self._base_url}/patent",
                headers=headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 403:
                logger.error("PatentsView API key invalid or forbidden")
                return self._empty_patent_data(company_name)

            if response.status_code != 200:
                logger.error(f"PatentsView API error: {response.status_code}")
                return self._empty_patent_data(company_name)

            data = response.json()

            total_patents = data.get("total_hits", 0)
            patents = data.get("patents", [])

            recent_patents = []
            ai_related_count = 0

            for patent in patents[:10]:
                patent_title = patent.get("patent_title", "").lower()
                patent_abstract = patent.get("patent_abstract", "").lower()

                combined_text = patent_title + " " + patent_abstract
                is_ai = any(ai_kw in combined_text for ai_kw in ai_keywords)
                if is_ai:
                    ai_related_count += 1

                recent_patents.append(
                    {
                        "patent_id": patent.get("patent_id"),
                        "title": patent.get("patent_title"),
                        "date": patent.get("patent_date"),
                        "abstract": patent.get("patent_abstract")[:200] + "..."
                        if patent.get("patent_abstract")
                        else None,
                    }
                )

            return PatentData(
                company_name=company_name,
                total_patents=total_patents,
                recent_patents=recent_patents,
                ai_related_patents=ai_related_count,
                top_patent_categories=[],
            )

        except requests.exceptions.Timeout:
            logger.error("PatentsView API request timed out")
            return self._empty_patent_data(company_name)
        except Exception as e:
            logger.error(f"Error fetching patent data: {e}")
            return self._empty_patent_data(company_name)

    def _empty_patent_data(self, company_name: str) -> PatentData:
        """Return empty patent data."""
        return PatentData(
            company_name=company_name,
            total_patents=0,
            recent_patents=[],
            ai_related_patents=0,
            top_patent_categories=[],
        )
