"""arXiv connector for academic papers."""

import logging
from datetime import datetime, timezone
from typing import Any

import feedparser

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class ArxivConnector(BaseConnector):
    """Connector for arXiv papers."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, config: SourceConfig | None = None):
        if config is None:
            config = SourceConfig(
                name="arxiv",
                base_url=self.BASE_URL,
                rate_limit=30,
            )
        super().__init__(config)

    async def connect(self) -> bool:
        try:
            feed = feedparser.parse(f"{self.BASE_URL}?search_query=all:test&max_results=1")
            return len(feed.entries) >= 0
        except Exception as e:
            logger.error(f"Failed to connect to arXiv: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        try:
            search_query = query.replace(" ", "+")
            url = f"{self.BASE_URL}?search_query=all:{search_query}&max_results={kwargs.get('limit', 10)}"

            feed = feedparser.parse(url)
            entries = feed.entries

            raw_data_list = []
            for entry in entries:
                raw_data = RawData(
                    source_name=self.config.name,
                    source_url=entry.get("link"),
                    raw_content=entry,
                    extracted_at=datetime.now(timezone.utc),
                    metadata={
                        "paper_id": entry.get("id"),
                        "published": entry.get("published"),
                        "source_type": "academic_paper",
                    },
                )
                raw_data_list.append(raw_data)

            return ConnectorResult(
                success=True,
                data=raw_data_list,
                total_found=len(entries),
            )
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        try:
            url = f"{self.BASE_URL}?id_list={entity_id}"
            feed = feedparser.parse(url)

            if not feed.entries:
                return ConnectorResult(success=True, data=[], total_found=0)

            raw_data = RawData(
                source_name=self.config.name,
                source_url=feed.entries[0].get("link"),
                raw_content=feed.entries[0],
                extracted_at=datetime.now(timezone.utc),
                metadata={"paper_id": entity_id, "source_type": "academic_paper"},
            )

            return ConnectorResult(success=True, data=[raw_data], total_found=1)
        except Exception as e:
            return ConnectorResult(success=False, data=[], error_message=str(e))

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        content = raw_data.raw_content
        return {
            "source": "arxiv",
            "entity_type": "academic_paper",
            "title": content.get("title"),
            "url": content.get("link"),
            "abstract": content.get("summary"),
            "published_date": content.get("published"),
            "authors": [author.get("name") for author in content.get("authors", [])],
            "categories": [tag.get("term") for tag in content.get("tags", [])],
            "doi": content.get("arxiv_doi"),
            "raw_data": content,
        }
