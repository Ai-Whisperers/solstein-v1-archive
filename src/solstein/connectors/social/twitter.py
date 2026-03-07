"""Twitter/X connector for social data."""

import logging
from datetime import datetime
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class TwitterConnector(BaseConnector):
    """Connector for Twitter/X API (requires API v2 bearer token)."""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: Optional[str] = None):
        config = SourceConfig(
            name="twitter",
            base_url=self.BASE_URL,
            api_key=bearer_token,
            rate_limit=300,  # per 15 minutes for search
        )
        super().__init__(config)
        self._headers = {}
        if bearer_token:
            self._headers["Authorization"] = f"Bearer {bearer_token}"

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("Twitter bearer token not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/users/by/username/twitter", headers=self._headers
                ) as response:
                    return response.status in [200, 404]  # 404 means API works
        except Exception as e:
            logger.error(f"Failed to connect to Twitter: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(success=False, data=[], error_message="Bearer token required")

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "max_results": min(kwargs.get("limit", 10), 100),
                    "tweet.fields": "created_at,author_id,public_metrics",
                }

                async with session.get(
                    f"{self.config.base_url}/tweets/search/recent", headers=self._headers, params=params
                ) as response:
                    data = await response.json()

                    if "errors" in data:
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=str(data.get("errors")),
                        )

                    tweets = data.get("data", [])

                    raw_data_list = []
                    for tweet in tweets:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://twitter.com/i/web/status/{tweet.get('id')}",
                            raw_content=tweet,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "tweet_id": tweet.get("id"),
                                "author_id": tweet.get("author_id"),
                                "source_type": "social_post",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=len(raw_data_list),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        metrics = content.get("public_metrics", {})

        return {
            "source": "twitter",
            "entity_type": "social_post",
            "text": content.get("text"),
            "url": raw_data.source_url,
            "tweet_id": content.get("id"),
            "author_id": content.get("author_id"),
            "created_at": content.get("created_at"),
            "retweets": metrics.get("retweet_count"),
            "replies": metrics.get("reply_count"),
            "likes": metrics.get("like_count"),
            "quotes": metrics.get("quote_count"),
            "raw_data": content,
        }
