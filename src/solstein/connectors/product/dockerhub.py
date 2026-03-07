"""Docker Hub connector for container images."""

import logging
from datetime import datetime
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class DockerHubConnector(BaseConnector):
    """Connector for Docker Hub."""

    BASE_URL = "https://hub.docker.com/v2"

    def __init__(self):
        config = SourceConfig(
            name="dockerhub",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/repositories/library/nginx") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Docker Hub: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "page_size": kwargs.get("limit", 10),
                }

                async with session.get(f"{self.config.base_url}/search/repositories", params=params) as response:
                    data = await response.json()
                    results = data.get("results", [])

                    raw_data_list = []
                    for repo in results:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://hub.docker.com/r/{repo.get('repo_name')}",
                            raw_content=repo,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "repo_name": repo.get("repo_name"),
                                "namespace": repo.get("namespace"),
                                "source_type": "container_image",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("count", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/repositories/{entity_id}") as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://hub.docker.com/r/{entity_id}",
                        raw_content=data,
                        extracted_at=datetime.utcnow(),
                        metadata={
                            "repo_name": data.get("name"),
                            "namespace": data.get("namespace"),
                            "source_type": "container_image",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "dockerhub",
            "entity_type": "container_image",
            "name": content.get("name"),
            "namespace": content.get("namespace"),
            "description": content.get("description"),
            "url": raw_data.source_url,
            "star_count": content.get("star_count"),
            "pull_count": content.get("pull_count"),
            "is_official": content.get("is_official"),
            "is_private": content.get("is_private"),
            "last_updated": content.get("last_updated"),
            "raw_data": content,
        }
