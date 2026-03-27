"""App Store connector for iOS apps."""

import logging
from datetime import datetime, timezone
from typing import Any

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class AppStoreConnector(BaseConnector):
    """Connector for Apple App Store (using iTunes Search API)."""

    BASE_URL = "https://itunes.apple.com/search"

    def __init__(self):
        config = SourceConfig(
            name="appstore",
            base_url=self.BASE_URL,
            rate_limit=100,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {"term": "facebook", "entity": "software", "limit": 1}
                async with session.get(self.config.base_url, params=params) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to App Store: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {
                    "term": query,
                    "entity": "software",
                    "limit": kwargs.get("limit", 10),
                }

                async with session.get(self.config.base_url, params=params) as response:
                    # iTunes API returns text/javascript, not application/json
                    text = await response.text()
                    import json

                    data = json.loads(text)
                    results = data.get("results", [])

                    raw_data_list = []
                    for app in results:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=app.get("trackViewUrl"),
                            raw_content=app,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "app_id": app.get("trackId"),
                                "bundle_id": app.get("bundleId"),
                                "developer": app.get("artistName"),
                                "source_type": "mobile_app",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=data.get("resultCount", 0),
                    )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get app by ID."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                params = {"id": entity_id, "entity": "software"}
                async with session.get(self.config.base_url, params=params) as response:
                    data = await response.json()
                    results = data.get("results", [])

                    if not results:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=results[0].get("trackViewUrl"),
                        raw_content=results[0],
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "app_id": entity_id,
                            "bundle_id": results[0].get("bundleId"),
                            "source_type": "mobile_app",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        return {
            "source": "appstore",
            "entity_type": "mobile_app",
            "name": content.get("trackName"),
            "app_id": content.get("trackId"),
            "bundle_id": content.get("bundleId"),
            "description": content.get("description"),
            "url": content.get("trackViewUrl"),
            "developer": content.get("artistName"),
            "developer_id": content.get("artistId"),
            "price": content.get("price"),
            "currency": content.get("currency"),
            "rating": content.get("averageUserRating"),
            "rating_count": content.get("userRatingCount"),
            "version": content.get("version"),
            "release_date": content.get("releaseDate"),
            "current_version_release": content.get("currentVersionReleaseDate"),
            "genres": content.get("genres", []),
            "screenshot_urls": content.get("screenshotUrls", []),
            "raw_data": content,
        }
