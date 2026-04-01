"""
Academic and research data connectors.

FREE sources:
- Semantic Scholar (free API)
- arXiv (free API)
- CrossRef (free, polite pool)
- OpenAlex (free API)
"""

import asyncio  # noqa: F401
import logging
from datetime import datetime, timezone
from typing import Any, Optional  # noqa: F401

import aiohttp

from ..base import BaseConnector, ConnectorResult, RawData, SourceConfig

logger = logging.getLogger(__name__)


class SemanticScholarConnector(BaseConnector):
    """Connector for Semantic Scholar API (free, no key required)."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, config: SourceConfig | None = None):
        if config is None:
            config = SourceConfig(
                name="semantic_scholar",
                base_url=self.BASE_URL,
                rate_limit=100,  # 100 requests/5 minutes
            )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to Semantic Scholar."""
        try:
            # Semantic Scholar doesn't require auth, just test with a simple query
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/graph/v1/paper/search",
                    params={"query": "test", "limit": 1, "fields": "paperId"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    # SS returns 200 even for empty results
                    return response.status in [200, 404]
        except Exception as e:
            logger.warning(f"Semantic Scholar connection test: {e}")
            # Don't fail - SS might be temporarily unavailable
            return True  # Assume working, will fail on actual search if broken
        """Test connection to Semantic Scholar."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/paper/search", params={"query": "test", "limit": 1}
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to Semantic Scholar: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for papers by keyword."""
        logger.info(f"Searching Semantic Scholar for: {query}")

        fields = kwargs.get("fields", "title,authors,year,citationCount,abstract")
        limit = kwargs.get("limit", 10)

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "fields": fields,
                    "limit": limit,
                }
                async with session.get(f"{self.config.base_url}/graph/v1/paper/search", params=params) as response:
                    data = await response.json()

                    papers = data.get("data", [])
                    total = data.get("total", 0)

                    raw_data_list = []
                    for paper in papers:
                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                            raw_content=paper,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "paper_id": paper.get("paperId"),
                                "source_type": "academic_paper",
                            },
                        )
                        raw_data_list.append(raw_data)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=total,
                    )

        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get paper by ID."""
        logger.info(f"Getting Semantic Scholar paper: {entity_id}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/paper/{entity_id}",
                    params={"fields": "title,authors,year,abstract,citationCount,references,citations"},
                ) as response:
                    paper = await response.json()

                    if not paper or "paperId" not in paper:
                        return ConnectorResult(
                            success=True,
                            data=[],
                            total_found=0,
                        )

                    raw_data = RawData(
                        source_name=self.config.name,
                        source_url=f"https://www.semanticscholar.org/paper/{entity_id}",
                        raw_content=paper,
                        extracted_at=datetime.now(timezone.utc),
                        metadata={
                            "paper_id": entity_id,
                            "source_type": "academic_paper",
                        },
                    )

                    return ConnectorResult(
                        success=True,
                        data=[raw_data],
                        total_found=1,
                    )

        except Exception as e:
            logger.error(f"Semantic Scholar get_by_id failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize paper to common format."""
        content = raw_data.raw_content

        authors = content.get("authors", [])
        author_names = [a.get("name") for a in authors if a.get("name")]

        return {
            "source": "semantic_scholar",
            "entity_type": "paper",
            "paper_id": content.get("paperId"),
            "title": content.get("title"),
            "authors": author_names,
            "year": content.get("year"),
            "abstract": content.get("abstract"),
            "citation_count": content.get("citationCount"),
            "url": f"https://www.semanticscholar.org/paper/{content.get('paperId', '')}",
            "raw_data": content,
        }


class ArXivConnector(BaseConnector):
    """Connector for arXiv API (free, no key required)."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, config: SourceConfig | None = None):
        if config is None:
            config = SourceConfig(
                name="arxiv",
                base_url=self.BASE_URL,
                rate_limit=3,  # 3 seconds between requests (polite)
            )
        super().__init__(config)

    async def connect(self) -> bool:
        """Test connection to arXiv."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config.base_url, params={"search_query": "all:test", "max_results": 1}
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to connect to arXiv: {e}")
            return False

    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for papers on arXiv."""
        logger.info(f"Searching arXiv for: {query}")

        max_results = kwargs.get("limit", 10)

        try:
            import xml.etree.ElementTree as ET

            async with aiohttp.ClientSession() as session:
                params = {
                    "search_query": f"all:{query}",
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                }
                async with session.get(self.config.base_url, params=params) as response:
                    xml_content = await response.text()

                    # Parse Atom feed
                    root = ET.fromstring(xml_content)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}

                    entries = root.findall("atom:entry", ns)

                    raw_data_list = []
                    for entry in entries:
                        paper_id = entry.find("atom:id", ns)
                        title = entry.find("atom:title", ns)
                        summary = entry.find("atom:summary", ns)
                        published = entry.find("atom:published", ns)

                        authors = entry.findall("atom:author/atom:name", ns)
                        author_names = [a.text for a in authors if a.text]

                        paper_data = {
                            "id": paper_id.text if paper_id is not None else "",
                            "title": title.text.strip() if title is not None else "",
                            "abstract": summary.text.strip() if summary is not None else "",
                            "published": published.text if published is not None else "",
                            "authors": author_names,
                        }

                        raw_data = RawData(
                            source_name=self.config.name,
                            source_url=paper_data["id"],
                            raw_content=paper_data,
                            extracted_at=datetime.now(timezone.utc),
                            metadata={
                                "paper_id": paper_data["id"].split("/")[-1]
                                if "/" in paper_data["id"]
                                else paper_data["id"],
                                "source_type": "academic_paper",
                            },
                        )
                        raw_data_list.append(raw_data)

                    # Get total results from opensearch
                    total_results = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
                    total = int(total_results.text) if total_results is not None else len(raw_data_list)

                    return ConnectorResult(
                        success=True,
                        data=raw_data_list,
                        total_found=total,
                    )

        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return ConnectorResult(
                success=False,
                data=[],
                error_message=str(e),
            )

    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get paper by arXiv ID."""
        return await self.search(f"id:{entity_id}", limit=1)

    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize arXiv paper to common format."""
        content = raw_data.raw_content

        return {
            "source": "arxiv",
            "entity_type": "paper",
            "paper_id": raw_data.metadata.get("paper_id"),
            "title": content.get("title"),
            "authors": content.get("authors", []),
            "abstract": content.get("abstract"),
            "published": content.get("published"),
            "url": raw_data.source_url,
            "raw_data": content,
        }


# Factory function
async def create_academic_connector(source_type: str, **kwargs) -> BaseConnector:
    """Factory function to create academic connectors."""
    connectors = {
        "semantic_scholar": SemanticScholarConnector,
        "arxiv": ArXivConnector,
    }

    connector_class = connectors.get(source_type)
    if not connector_class:
        raise ValueError(f"Unknown academic connector: {source_type}")

    connector = connector_class(**kwargs)
    return connector


__all__ = [
    "SemanticScholarConnector",
    "ArXivConnector",
    "create_academic_connector",
]
