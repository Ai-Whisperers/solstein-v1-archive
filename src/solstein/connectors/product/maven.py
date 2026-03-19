"""Maven Central connector for Java packages."""

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class MavenCentralConnector(BaseConnector):
    """Connector for Maven Central (Java packages)."""

    BASE_URL = "https://search.maven.org/solrsearch/select"

    def __init__(self):
        config = SourceConfig(
            name="maven",
            base_url=self.BASE_URL,
            rate_limit=1000,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"q": "g:com.google.guava", "rows": 1}
                async with session.get(self.config.base_url, params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Maven Central: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "q": query,
                    "rows": kwargs.get("limit", 10),
                    "wt": "json",
                }

                async with session.get(self.config.base_url, params=params) as response:
                    data = await response.json()
                    docs = data.get("response", {}).get("docs", [])

                    raw_data_list = []
                    for doc in docs:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://search.maven.org/artifact/{doc.get('g')}/{doc.get('a')}",
                            raw_content=doc,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "group_id": doc.get("g"),
                                "artifact_id": doc.get("a"),
                                "version": doc.get("latestVersion"),
                                "source_type": "package_registry",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("response", {}).get("numFound", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            # entity_id should be in format "groupId:artifactId"
            parts = entity_id.split(":")
            if len(parts) != 2:
                return ConnectorResult(success=False, data=[], error_message="Invalid format. Use 'groupId:artifactId'")

            async with aiohttp.ClientSession() as session:
                params = {
                    "q": f"g:{parts[0]} AND a:{parts[1]}",
                    "rows": 1,
                    "wt": "json",
                }

                async with session.get(self.config.base_url, params=params) as response:
                    data = await response.json()
                    docs = data.get("response", {}).get("docs", [])

                    if not docs:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://search.maven.org/artifact/{parts[0]}/{parts[1]}",
                        raw_content=docs[0],
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "group_id": parts[0],
                            "artifact_id": parts[1],
                            "source_type": "package_registry",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "maven",
            "entity_type": "package",
            "group_id": content.get("g"),
            "artifact_id": content.get("a"),
            "version": content.get("latestVersion"),
            "url": raw_data.source_url,
            "timestamp": content.get("timestamp"),
            "version_count": content.get("versionCount"),
            "text": content.get("text"),
            "raw_data": content,
        }
