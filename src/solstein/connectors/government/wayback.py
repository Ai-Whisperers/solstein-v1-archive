"""Wayback Machine connector for archived web pages."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class WaybackMachineConnector(BaseConnector):
    """Connector for Internet Archive Wayback Machine."""

    BASE_URL = "https://web.archive.org/web"
    CDX_URL = "https://web.archive.org/cdx/search/cdx"

    def __init__(self):
        config = SourceConfig(
            name="wayback",
            base_url=self.BASE_URL,
            rate_limit=15,  # Be polite to IA
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/20150101/https://example.com") as response:
                    return response.status in [200, 404]
        except Exception as e:
            logger.error(f"Failed to connect to Wayback Machine: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for snapshots of a URL."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "url": query,
                    "output": "json",
                    "limit": kwargs.get("limit", 10),
                }

                async with session.get(self.CDX_URL, params=params) as response:
                    data = await response.json()

                    # CDX returns array with headers as first row
                    if len(data) <= 1:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    headers = data[0]
                    snapshots = data[1:]

                    raw_data_list = []
                    for snapshot in snapshots:
                        snapshot_dict = dict(zip(headers, snapshot))
                        timestamp = snapshot_dict.get("timestamp")
                        urlkey = snapshot_dict.get("urlkey")

                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"{self.config.base_url}/{timestamp}if_/https://{snapshot_dict.get('original')}",
                            raw_content=snapshot_dict,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "timestamp": timestamp,
                                "urlkey": urlkey,
                                "source_type": "archive",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=len(snapshots),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get specific snapshot by URL and timestamp."""
        return ConnectorResult(success=False, data=[], error_message="Use search with URL")

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        timestamp = raw_data.metadata.get("timestamp", "")

        # Parse timestamp: YYYYMMDDHHMMSS
        if len(timestamp) >= 14:
            dt = datetime.strptime(timestamp[:14], "%Y%m%d%H%M%S")
        else:
            dt = None

        return {
            "source": "wayback",
            "entity_type": "web_archive",
            "url": content.get("original"),
            "archive_url": raw_data.source_url,
            "timestamp": timestamp,
            "datetime": dt,
            "status_code": content.get("statuscode"),
            "mimetype": content.get("mimetype"),
            "raw_data": content,
        }
