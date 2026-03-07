"""PyPI connector for Python packages."""

import logging
from datetime import datetime
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class PyPIConnector(BaseConnector):
    """Connector for PyPI (Python Package Index)."""

    BASE_URL = "https://pypi.org/pypi"

    def __init__(self):
        config = SourceConfig(
            name="pypi",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/requests/json") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to PyPI: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        # PyPI doesn't have a search API, use simple index
        logger.info(f"PyPI search not available via API: {query}")
        return ConnectorResult(success=True, data=[], total_found=0)

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/{entity_id}/json") as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()
                    info = data.get("info", {})

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://pypi.org/project/{entity_id}",
                        raw_content=data,
                        extracted_at=datetime.utcnow(),
                        metadata={
                            "package_name": entity_id,
                            "version": info.get("version"),
                            "source_type": "package_registry",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        info = content.get("info", {})

        return {
            "source": "pypi",
            "entity_type": "package",
            "name": info.get("name"),
            "version": info.get("version"),
            "description": info.get("summary"),
            "long_description": info.get("description"),
            "url": raw_data.source_url,
            "author": info.get("author"),
            "author_email": info.get("author_email"),
            "license": info.get("license"),
            "keywords": info.get("keywords", "").split(",") if info.get("keywords") else [],
            "homepage": info.get("home_page"),
            "repository": info.get("project_urls", {}).get("Source") if info.get("project_urls") else None,
            "downloads_last_month": info.get("downloads", {}).get("last_month")
            if isinstance(info.get("downloads"), dict)
            else None,
            "raw_data": content,
        }
