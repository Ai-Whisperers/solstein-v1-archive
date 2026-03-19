"""GitLab connector for repositories."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class GitLabConnector(BaseConnector):
    """Connector for GitLab API."""

    BASE_URL = "https://gitlab.com/api/v4"

    def __init__(self, private_token: Optional[str] = None):
        config = SourceConfig(
            name="gitlab",
            base_url=self.BASE_URL,
            api_key=private_token,
            rate_limit=2000,  # per minute for authenticated requests
        )
        super().__init__(config)
        self._headers = {}
        if private_token:
            self._headers["Private-Token"] = private_token

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/version", headers=self._headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to GitLab: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "search": query,
                    "per_page": kwargs.get("limit", 10),
                }

                async with session.get(
                    f"{self.config.base_url}/projects", headers=self._headers, params=params
                ) as response:
                    projects = await response.json()

                    if isinstance(projects, dict) and "error" in projects:
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message=projects.get("error"),
                        )

                    raw_data_list = []
                    for project in projects:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=project.get("web_url"),
                            raw_content=project,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "project_id": project.get("id"),
                                "namespace": project.get("namespace", {}).get("name"),
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
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/projects/{entity_id}", headers=self._headers
                ) as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    project = await response.json()

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=project.get("web_url"),
                        raw_content=project,
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "project_id": project.get("id"),
                            "namespace": project.get("namespace", {}).get("name"),
                            "source_type": "code_repository",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "gitlab",
            "entity_type": "code_repository",
            "name": content.get("name"),
            "full_name": content.get("path_with_namespace"),
            "url": content.get("web_url"),
            "description": content.get("description"),
            "stars": content.get("star_count"),
            "forks": content.get("forks_count"),
            "open_issues": content.get("open_issues_count"),
            "created_at": content.get("created_at"),
            "last_activity": content.get("last_activity_at"),
            "namespace": content.get("namespace", {}).get("name"),
            "visibility": content.get("visibility"),
            "raw_data": content,
        }
