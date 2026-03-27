"""Bitbucket connector for repositories."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class BitbucketConnector(BaseConnector):
    """Connector for Bitbucket API."""

    BASE_URL = "https://api.bitbucket.org/2.0"

    def __init__(self, username: str | None = None, app_password: str | None = None):
        config = SourceConfig(
            name="bitbucket",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)
        self._auth = None
        if username and app_password:
            import aiohttp

            self._auth = aiohttp.BasicAuth(username, app_password)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/user", auth=self._auth) as response:
                    return response.status in [200, 401]  # 401 means API works but needs auth
        except Exception as e:
            logger.error(f"Failed to connect to Bitbucket: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"q": f'name~"{query}"', "pagelen": kwargs.get("limit", 10)}

                async with session.get(
                    f"{self.config.base_url}/repositories/{query}", params=params, auth=self._auth
                ) as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()
                    repos = data.get("values", [])

                    raw_data_list = []
                    for repo in repos:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=repo.get("links", {}).get("html", {}).get("href"),
                            raw_content=repo,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "repo_uuid": repo.get("uuid"),
                                "full_name": repo.get("full_name"),
                                "source_type": "code_repository",
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

        return {
            "source": "bitbucket",
            "entity_type": "code_repository",
            "name": content.get("name"),
            "full_name": content.get("full_name"),
            "url": content.get("links", {}).get("html", {}).get("href"),
            "description": content.get("description"),
            "language": content.get("language"),
            "created_on": content.get("created_on"),
            "updated_on": content.get("updated_on"),
            "is_private": content.get("is_private"),
            "owner": content.get("owner", {}).get("username"),
            "raw_data": content,
        }
