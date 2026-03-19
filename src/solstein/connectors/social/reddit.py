"""Reddit connector for discussions and communities."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class RedditConnector(BaseConnector):
    """Connector for Reddit (requires API credentials)."""

    BASE_URL = "https://www.reddit.com"
    OAUTH_URL = "https://oauth.reddit.com"

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        config = SourceConfig(
            name="reddit",
            base_url=self.BASE_URL,
            rate_limit=60,  # per minute
        )
        super().__init__(config)
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None

    async def connect(self) -> bool:
        """Test connection to Reddit."""
        try:
            # Reddit is accessible without auth for read-only
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/r/technology.json", headers={"User-Agent": "Solstein-Research/1.0"}
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Reddit: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search Reddit posts."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "limit": kwargs.get("limit", 10),
                    "sort": "relevance",
                    "t": "all",
                }

                async with session.get(
                    f"{self.config.base_url}/search.json",
                    headers={"User-Agent": "Solstein-Research/1.0"},
                    params=params,
                ) as response:
                    data = await response.json()

                    posts = data.get("data", {}).get("children", [])

                    raw_data_list = []
                    for post in posts:
                        post_data = post.get("data", {})
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://reddit.com{post_data.get('permalink')}",
                            raw_content=post_data,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "post_id": post_data.get("id"),
                                "subreddit": post_data.get("subreddit"),
                                "author": post_data.get("author"),
                                "source_type": "social_discussion",
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
        """Get post by ID."""
        return ConnectorResult(success=False, data=[], error_message="Not implemented")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "reddit",
            "entity_type": "social_discussion",
            "title": content.get("title"),
            "url": content.get("url"),
            "permalink": f"https://reddit.com{content.get('permalink')}",
            "author": content.get("author"),
            "subreddit": content.get("subreddit"),
            "score": content.get("score"),
            "upvotes": content.get("ups"),
            "downvotes": content.get("downs"),
            "num_comments": content.get("num_comments"),
            "created_at": datetime.fromtimestamp(content.get("created_utc", 0)),
            "is_self": content.get("is_self"),
            "selftext": content.get("selftext"),
            "raw_data": content,
        }
