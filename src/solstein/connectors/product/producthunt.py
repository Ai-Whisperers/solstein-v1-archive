"""Product Hunt connector for product launches."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class ProductHuntConnector(BaseConnector):
    """Connector for Product Hunt (requires API token)."""

    BASE_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self, api_token: str | None = None):
        config = SourceConfig(
            name="producthunt",
            base_url=self.BASE_URL,
            api_key=api_token,
            rate_limit=100,  # per hour
        )
        super().__init__(config)
        self._headers = {}
        if api_token:
            self._headers["Authorization"] = f"Bearer {api_token}"

    async def connect(self) -> bool:
        if not self.config.api_key:
            logger.warning("Product Hunt API token not provided")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                # Simple query to test connection
                query = {"query": "{ viewer { user { name } } }"}
                async with session.post(self.config.base_url, headers=self._headers, json=query) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Product Hunt: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        if not self.config.api_key:
            return ConnectorResult(
                success=False,
                data=[],
                error_message="API token required",
            )

        try:
            async with aiohttp.ClientSession() as session:
                # Search for posts
                graphql_query = {
                    "query": f"""
                    {{
                        posts(search: "{query}", first: {kwargs.get("limit", 10)}) {{
                            edges {{
                                node {{
                                    id
                                    name
                                    tagline
                                    description
                                    url
                                    votesCount
                                    commentsCount
                                    createdAt
                                    maker {{
                                        name
                                    }}
                                    topics {{
                                        edges {{
                                            node {{
                                                name
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                    """
                }

                async with session.post(self.config.base_url, headers=self._headers, json=graphql_query) as response:
                    data = await response.json()

                    posts = data.get("data", {}).get("posts", {}).get("edges", [])

                    raw_data_list = []
                    for edge in posts:
                        post = edge.get("node", {})
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=post.get("url"),
                            raw_content=post,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "post_id": post.get("id"),
                                "votes": post.get("votesCount"),
                                "source_type": "product_launch",
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
        topics = [edge.get("node", {}).get("name") for edge in content.get("topics", {}).get("edges", [])]

        return {
            "source": "producthunt",
            "entity_type": "product_launch",
            "name": content.get("name"),
            "tagline": content.get("tagline"),
            "description": content.get("description"),
            "url": content.get("url"),
            "votes": content.get("votesCount"),
            "comments": content.get("commentsCount"),
            "created_at": content.get("createdAt"),
            "maker": content.get("maker", {}).get("name"),
            "topics": topics,
            "raw_data": content,
        }
