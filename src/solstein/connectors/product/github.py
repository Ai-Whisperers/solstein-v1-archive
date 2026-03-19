"""GitHub connector for repository data."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class GitHubConnector(BaseConnector):
    """Connector for GitHub API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, api_token: Optional[str] = None):
        config = SourceConfig(
            name="github",
            base_url=self.BASE_URL,
            api_key=api_token,
            rate_limit=60 if not api_token else 5000,
        )
        super().__init__(config)
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-Research",
        }
        if api_token:
            self._headers["Authorization"] = f"token {api_token}"

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/rate_limit", headers=self._headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to GitHub: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": kwargs.get("limit", 10),
                }

                async with session.get(
                    f"{self.config.base_url}/search/repositories", headers=self._headers, params=params
                ) as response:
                    if response.status == 403:
                        return ConnectorResult(
                            success=False,
                            data=[],
                            error_message="Rate limit exceeded",
                        )

                    data = await response.json()
                    items = data.get("items", [])

                    raw_data_list = []
                    for repo in items:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=repo.get("html_url"),
                            raw_content=repo,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "repo_id": repo.get("id"),
                                "owner": repo.get("owner", {}).get("login"),
                                "language": repo.get("language"),
                                "source_type": "code_repository",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("total_count", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/repos/{entity_id}", headers=self._headers) as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=data.get("html_url"),
                        raw_content=data,
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "repo_id": data.get("id"),
                            "owner": data.get("owner", {}).get("login"),
                            "language": data.get("language"),
                            "source_type": "code_repository",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        return {
            "source": "github",
            "entity_type": "code_repository",
            "name": content.get("name"),
            "full_name": content.get("full_name"),
            "url": content.get("html_url"),
            "description": content.get("description"),
            "language": content.get("language"),
            "stars": content.get("stargazers_count"),
            "forks": content.get("forks_count"),
            "open_issues": content.get("open_issues_count"),
            "created_at": content.get("created_at"),
            "updated_at": content.get("updated_at"),
            "owner": content.get("owner", {}).get("login"),
            "topics": content.get("topics", []),
            "raw_metrics": {
                "watchers": content.get("watchers_count"),
                "subscribers": content.get("subscribers_count"),
            },
        }
