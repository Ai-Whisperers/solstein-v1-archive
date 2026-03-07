"""Source repository for Neo4j evidence graph.

EPIC-022: Extracted from EvidenceGraph for modularity.
"""

import logging

from ..models import SourceDocument
from .base import EvidenceGraphRepository

logger = logging.getLogger(__name__)


class SourceRepository(EvidenceGraphRepository):
    """Repository for source entity operations."""

    def create(self, source: SourceDocument) -> None:
        """Create or update a source node.

        Args:
            source: Source document to create
        """
        query = """
        MERGE (s:Source {url: $url})
        SET s.title = $title,
            s.source_type = $source_type,
            s.domain = $domain,
            s.scraped_at = $scraped_at,
            s.content_hash = $content_hash,
            s.word_count = $word_count,
            s.language = $language,
            s.updated_at = datetime()
        RETURN s
        """

        with self._get_session() as session:
            session.run(
                query,
                url=source.url,
                title=source.title,
                source_type=source.source_type.value,
                domain=source.domain,
                scraped_at=source.scraped_at.isoformat(),
                content_hash=source.content_hash,
                word_count=source.word_count,
                language=source.language,
            )
            logger.info(f"Created/updated source: {source.url}")
