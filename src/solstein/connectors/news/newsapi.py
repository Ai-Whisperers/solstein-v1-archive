"""NewsAPI connector for news articles."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class NewsAPIConnector(BaseConnector):
    """Connector for NewsAPI (free tier: 100 requests/day)."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str | None = None):
        config = SourceConfig(
            name="newsapi",
            base_url=self.BASE_URL,
            api_key=api_key,
            rate_limit=100,  # Daily limit for free tier
        )
        super().__init__(config)

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("NewsAPI key not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                params = {"apiKey": self.config.api_key, "q": "test", "pageSize": 1}
                async with session.get(f"{self.config.base_url}/everything", params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to NewsAPI: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="API key required")

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "apiKey": self.config.api_key,
                    "q": query,
                    "pageSize": kwargs.get("limit", 10),
                    "language": kwargs.get("language", "en"),
                    "sortBy": "relevancy",
                }

                if "from_date" in kwargs:
                    params["from"] = kwargs["from_date"]
                if "to_date" in kwargs:
                    params["to"] = kwargs["to_date"]

                async with session.get(f"{self.config.base_url}/everything", params=params) as response:
                    data = await response.json()

                    if data.get("status") != "ok":
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=data.get("message", "Unknown error"),
                        )

                    articles = data.get("articles", [])

                    raw_data_list = []
                    for article in articles:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=article.get("url"),
                            raw_content=article,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "source": article.get("source", {}).get("name"),
                                "author": article.get("author"),
                                "published_at": article.get("publishedAt"),
                                "source_type": "news",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("totalResults", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="NewsAPI doesn't support ID-based retrieval")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "newsapi",
            "entity_type": "news_article",
            "title": content.get("title"),
            "url": content.get("url"),
            "author": content.get("author"),
            "published_date": content.get("publishedAt"),
            "description": content.get("description"),
            "content_preview": content.get("content"),
            "source_name": content.get("source", {}).get("name"),
            "raw_content": content,
        }
