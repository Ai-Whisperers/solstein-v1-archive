"""PatentsView connector for USPTO patent data."""

import logging
from datetime import datetime
from typing import Any

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class PatentsViewConnector(BaseConnector):
    """Connector for USPTO PatentsView API."""

    BASE_URL = "https://api.patentsview.org/patents/query"

    def __init__(self):
        config = SourceConfig(
            name="patentsview",
            base_url=self.BASE_URL,
            rate_limit=45,
        )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                json_data = {"q": {"patent_number": "10000000"}, "f": ["patent_number", "patent_title"]}
                async with session.post(self.config.base_url, json=json_data) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to PatentsView: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            async with aiohttp.ClientSession() as session:
                json_data = {
                    "q": {"_text": {"patent_title": query}},
                    "f": [
                        "patent_number",
                        "patent_title",
                        "patent_date",
                        "patent_abstract",
                        "assignee_organization",
                    ],
                    "o": {"per_page": kwargs.get("limit", 10)},
                }

                async with session.post(self.config.base_url, json=json_data) as response:
                    data = await response.json()
                    patents = data.get("patents", [])

                    raw_data_list = []
                    for patent in patents:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://patents.uspto.gov/patent/{patent.get('patent_number')}",
                            raw_content=patent,
                            extracted_at=datetime.utcnow(),
                            metadata={
                                "patent_number": patent.get("patent_number"),
                                "patent_date": patent.get("patent_date"),
                                "source_type": "patent",
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
                json_data = {"q": {"patent_number": entity_id}, "f": ["*"]}

                async with session.post(self.config.base_url, json=json_data) as response:
                    data = await response.json()
                    patents = data.get("patents", [])

                    if not patents:
                        return ConnectorResult(success=True, data=[], total_found=0)

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://patents.uspto.gov/patent/{entity_id}",
                        raw_content=patents[0],
                        extracted_at=datetime.utcnow(),
                        metadata={
                            "patent_number": entity_id,
                            "source_type": "patent",
                        },
                    )

                    return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content

        assignees = content.get("assignees", [])
        assignee_name = assignees[0].get("assignee_organization") if assignees else None

        return {
            "source": "patentsview",
            "entity_type": "patent",
            "patent_number": content.get("patent_number"),
            "title": content.get("patent_title"),
            "abstract": content.get("patent_abstract"),
            "date": content.get("patent_date"),
            "assignee": assignee_name,
            "url": f"https://patents.uspto.gov/patent/{content.get('patent_number')}",
            "raw_data": content,
        }
