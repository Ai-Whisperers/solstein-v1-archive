"""npm registry connector for JavaScript packages."""

import logging
from datetime import datetime
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class NPMConnector(BaseConnector):
    """Connector for npm registry."""

    BASE_URL = "https://registry.npmjs.org"

    def __init__(self):
        config = SourceConfig(
            name="npm",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/react") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to npm: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            # npm search API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://registry.npmjs.org/-/v1/search", params={"text": query, "size": kwargs.get("limit", 10)}
                ) as response:
                    data = await response.json()
                    packages = data.get("objects", [])

                    raw_data_list = []
                    for pkg in packages:
                        package = pkg.get("package", {})
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://npmjs.com/package/{package.get('name')}",
                            raw_content=package,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "package_name": package.get("name"),
                                "version": package.get("version"),
                                "source_type": "package_registry",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("total", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/{entity_id}") as response:
                    if response.status == 404:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    data = await response.json()

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://npmjs.com/package/{entity_id}",
                        raw_content=data,
                        extracted_at=datetime.utcnow(),
                        metadata={
                            "package_name": entity_id,
                            "version": data.get("dist-tags", {}).get("latest"),
                            "source_type": "package_registry",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "npm",
            "entity_type": "package",
            "name": content.get("name"),
            "version": raw_data.metadata.get("version"),
            "description": content.get("description"),
            "url": raw_data.source_url,
            "author": content.get("author", {}).get("name")
            if isinstance(content.get("author"), dict)
            else content.get("author"),
            "license": content.get("license"),
            "keywords": content.get("keywords", []),
            "repository": content.get("repository", {}).get("url")
            if isinstance(content.get("repository"), dict)
            else content.get("repository"),
            "downloads_weekly": content.get("downloads", {}).get("weekly")
            if isinstance(content.get("downloads"), dict)
            else None,
            "raw_data": content,
        }
