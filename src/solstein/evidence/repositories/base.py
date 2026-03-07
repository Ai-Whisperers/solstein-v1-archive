"""Base repository for Neo4j evidence graph.

EPIC-022: Extracted from EvidenceGraph for modularity.
"""

import logging
from typing import Optional

from neo4j import Driver, GraphDatabase, Session
from neo4j.exceptions import Neo4jError

logger = logging.getLogger(__name__)


class EvidenceGraphRepository:
    """Base repository for Neo4j evidence graph operations.

    Provides connection management and common utilities for all
    entity-specific repositories.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """Connect to Neo4j database."""
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Neo4jError as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")

    def _get_session(self) -> Session:
        """Get a Neo4j session."""
        if not self._driver:
            self.connect()
        return self._driver.session()

    def init_schema(self) -> None:
        """Initialize the graph schema with constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE",
            "CREATE CONSTRAINT contradiction_id IF NOT EXISTS FOR (c:Contradiction) REQUIRE c.id IS UNIQUE",
        ]

        indexes = [
            "CREATE INDEX claim_field IF NOT EXISTS FOR (c:Claim) ON (c.field)",
            "CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status)",
            "CREATE INDEX claim_entity IF NOT EXISTS FOR (c:Claim) ON (c.entity_id)",
            "CREATE INDEX source_type IF NOT EXISTS FOR (s:Source) ON (s.source_type)",
            "CREATE INDEX claim_confidence IF NOT EXISTS FOR (c:Claim) ON (c.overall_confidence)",
        ]

        with self._get_session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint[:50]}...")
                except Neo4jError as e:
                    logger.warning(f"Constraint may already exist: {e}")

            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Created index: {index[:50]}...")
                except Neo4jError as e:
                    logger.warning(f"Index may already exist: {e}")

        logger.info("Schema initialization complete")

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.netloc or url
        except Exception:
            return url
