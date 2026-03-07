"""
Neo4j Evidence Graph - Graph database client for claims and relationships.

This module provides the Neo4j integration for EPIC-042.

FREE tools used:
- Neo4j Community Edition (free)
- neo4j Python driver
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError

from .models import Claim, ClaimStatus, SourceDocument, Contradiction, SourceType

logger = logging.getLogger(__name__)


class EvidenceGraph:
    """
    Neo4j-based evidence graph for storing claims and their relationships.

    Schema:
    - (:Company {id, name, ...})
    - (:Claim {id, field, value, confidence, status, ...})
    - (:Source {url, type, title, ...})
    - (:Contradiction {id, severity, status})

    Relationships:
    - (:Company)-[:HAS_CLAIM]->(:Claim)
    - (:Claim)-[:SOURCED_FROM]->(:Source)
    - (:Claim)-[:CONTRADICTS]->(:Claim)
    - (:Claim)-[:SUPPORTS]->(:Claim)
    - (:Contradiction)-[:INVOLVES]->(:Claim)
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "solstein123",
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """Connect to Neo4j database."""
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connection
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
            # Unique constraints
            "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT source_url IF NOT EXISTS FOR (s:Source) REQUIRE s.url IS UNIQUE",
            "CREATE CONSTRAINT contradiction_id IF NOT EXISTS FOR (c:Contradiction) REQUIRE c.id IS UNIQUE",
        ]

        indexes = [
            # Performance indexes
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

    def create_company(self, company_id: str, name: str, **properties) -> None:
        """Create or update a company node."""
        query = """
        MERGE (c:Company {id: $company_id})
        SET c.name = $name,
            c.updated_at = datetime(),
            c += $properties
        RETURN c
        """

        with self._get_session() as session:
            session.run(query, company_id=company_id, name=name, properties=properties)
            logger.info(f"Created/updated company: {company_id}")

    def create_source(self, source: SourceDocument) -> None:
        """Create or update a source node."""
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

    def create_claim(self, claim: Claim) -> None:
        """Create a claim and link it to company and source."""
        # First ensure company exists
        self.create_company(claim.entity_id, claim.entity_id)

        # Create source if not exists
        source_doc = SourceDocument(
            url=claim.source_url,
            source_type=claim.source_type,
            title=claim.source_title,
            domain=self._extract_domain(claim.source_url),
        )
        self.create_source(source_doc)

        # Create claim and relationships
        query = """
        MATCH (co:Company {id: $entity_id})
        MATCH (so:Source {url: $source_url})
        
        CREATE (c:Claim {
            id: $claim_id,
            field: $field,
            value: $value,
            unit: $unit,
            snippet: $snippet,
            snippet_location: $snippet_location,
            page_section: $page_section,
            extracted_at: $extracted_at,
            extraction_method: $extraction_method,
            status: $status,
            overall_confidence: $overall_confidence,
            created_at: datetime()
        })
        
        CREATE (co)-[:HAS_CLAIM]->(c)
        CREATE (c)-[:SOURCED_FROM]->(so)
        
        RETURN c
        """

        with self._get_session() as session:
            session.run(
                query,
                entity_id=claim.entity_id,
                source_url=claim.source_url,
                claim_id=str(claim.id),
                field=claim.field,
                value=str(claim.value),
                unit=claim.unit,
                snippet=claim.snippet,
                snippet_location=claim.snippet_location,
                page_section=claim.page_section,
                extracted_at=claim.extracted_at.isoformat(),
                extraction_method=claim.extraction_method,
                status=claim.status.value,
                overall_confidence=claim.overall_confidence,
            )
            logger.info(f"Created claim: {claim.id} for {claim.entity_id}.{claim.field}")

    def create_contradiction(self, contradiction: Contradiction) -> None:
        """Create a contradiction and link to involved claims."""
        # First create the contradiction node
        query1 = """
        CREATE (c:Contradiction {
            id: $contradiction_id,
            field: $field,
            severity: $severity,
            status: $status,
            detected_at: $detected_at
        })
        RETURN c
        """
        
        # Link contradiction to claims
        query2 = """
        MATCH (c:Contradiction {id: $contradiction_id})
        MATCH (claim:Claim)
        WHERE claim.id IN $claim_ids
        CREATE (c)-[:INVOLVES]->(claim)
        """
        
        # Create CONTRADICTS relationships between claim pairs
        query3 = """
        MATCH (c1:Claim)
        WHERE c1.id IN $claim_ids
        WITH c1
        MATCH (c2:Claim)
        WHERE c2.id IN $claim_ids AND c2.id > c1.id
        CREATE (c1)-[:CONTRADICTS {contradiction_id: $contradiction_id}]->(c2)
        """

        with self._get_session() as session:
            # Create contradiction
            session.run(
                query1,
                contradiction_id=str(contradiction.id),
                field=contradiction.field,
                severity=contradiction.severity,
                status=contradiction.status,
                detected_at=contradiction.detected_at.isoformat(),
            )
            
            # Link to claims
            session.run(
                query2,
                contradiction_id=str(contradiction.id),
                claim_ids=[str(cid) for cid in contradiction.claim_ids],
            )
            
            # Create pairwise CONTRADICTS relationships
            session.run(
                query3,
                contradiction_id=str(contradiction.id),
                claim_ids=[str(cid) for cid in contradiction.claim_ids],
            )
            
            logger.info(f"Created contradiction: {contradiction.id}")

    def get_claims_for_entity(
        self,
        entity_id: str,
        field: Optional[str] = None,
        status: Optional[ClaimStatus] = None,
        min_confidence: float = 0.0,
    ) -> list[dict]:
        """Get claims for an entity with optional filters."""
        query = """
        MATCH (co:Company {id: $entity_id})-[:HAS_CLAIM]->(c:Claim)
        WHERE c.overall_confidence >= $min_confidence
        """

        params = {
            "entity_id": entity_id,
            "min_confidence": min_confidence,
        }

        if field:
            query += " AND c.field = $field"
            params["field"] = field

        if status:
            query += " AND c.status = $status"
            params["status"] = status.value

        query += """
        OPTIONAL MATCH (c)-[:SOURCED_FROM]->(s:Source)
        RETURN c {
            .*,
            source_url: s.url,
            source_type: s.source_type,
            source_title: s.title
        } as claim
        ORDER BY c.overall_confidence DESC, c.extracted_at DESC
        """

        with self._get_session() as session:
            result = session.run(query, **params)
            return [record["claim"] for record in result]

    def get_contradictions_for_entity(self, entity_id: str) -> list[dict]:
        """Get all contradictions involving an entity's claims."""
        query = """
        MATCH (co:Company {id: $entity_id})-[:HAS_CLAIM]->(c:Claim)
        MATCH (c)<-[:INVOLVES]-(con:Contradiction)
        RETURN DISTINCT con {
            .*,
            claim_count: SIZE((con)-[:INVOLVES]->(:Claim))
        } as contradiction
        ORDER BY con.severity DESC, con.detected_at DESC
        """

        with self._get_session() as session:
            result = session.run(query, entity_id=entity_id)
            return [record["contradiction"] for record in result]

    def get_evidence_lineage(self, claim_id: str) -> dict:
        """Get full evidence lineage for a claim."""
        query = """
        MATCH (c:Claim {id: $claim_id})
        MATCH (co:Company)-[:HAS_CLAIM]->(c)
        MATCH (c)-[:SOURCED_FROM]->(s:Source)
        
        OPTIONAL MATCH (c)-[:CONTRADICTS]-(conflicting:Claim)
        OPTIONAL MATCH (c)-[:SUPPORTS]-(supporting:Claim)
        
        WITH c, co, s,
             collect(DISTINCT conflicting) as conflicting_claims,
             collect(DISTINCT supporting) as supporting_claims
        
        RETURN {
            claim: c {.*},
            company: co {.*},
            source: s {.*},
            conflicting_claims: [x in conflicting_claims WHERE x IS NOT NULL | x {.*}],
            supporting_claims: [x in supporting_claims WHERE x IS NOT NULL | x {.*}]
        } as lineage
        """

        with self._get_session() as session:
            result = session.run(query, claim_id=claim_id)
            record = result.single()
            return record["lineage"] if record else {}

    def update_claim_status(
        self,
        claim_id: str,
        status: ClaimStatus,
        reviewed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Update claim status (e.g., after review)."""
        query = """
        MATCH (c:Claim {id: $claim_id})
        SET c.status = $status,
            c.reviewed_at = datetime(),
            c.reviewed_by = $reviewed_by,
            c.review_notes = $notes,
            c.updated_at = datetime()
        RETURN c
        """

        with self._get_session() as session:
            session.run(
                query,
                claim_id=claim_id,
                status=status.value,
                reviewed_by=reviewed_by,
                notes=notes,
            )
            logger.info(f"Updated claim {claim_id} status to {status.value}")

    def get_entity_evidence_summary(self, entity_id: str) -> dict:
        """Get evidence summary statistics for an entity."""
        query = """
        MATCH (co:Company {id: $entity_id})-[:HAS_CLAIM]->(c:Claim)
        
        OPTIONAL MATCH (c)<-[:INVOLVES]-(con:Contradiction)
        
        WITH co, 
             COUNT(c) as total_claims,
             AVG(c.overall_confidence) as avg_confidence,
             collect(DISTINCT c.field) as fields,
             COUNT(CASE WHEN c.status = 'pending' THEN 1 END) as pending_count,
             COUNT(CASE WHEN c.status = 'accepted' THEN 1 END) as accepted_count,
             COUNT(CASE WHEN c.status = 'rejected' THEN 1 END) as rejected_count,
             COUNT(CASE WHEN c.status = 'conflicting' THEN 1 END) as conflicting_count,
             COUNT(DISTINCT con) as contradiction_count
        
        RETURN {
            entity_id: co.id,
            total_claims: total_claims,
            avg_confidence: avg_confidence,
            fields: fields,
            pending_count: pending_count,
            accepted_count: accepted_count,
            rejected_count: rejected_count,
            conflicting_count: conflicting_count,
            contradiction_count: contradiction_count
        } as summary
        """

        with self._get_session() as session:
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            return record["summary"] if record else {}

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return parsed.netloc or "unknown"


if __name__ == "__main__":
    # Test the evidence graph
    graph = EvidenceGraph()

    try:
        # Initialize schema
        graph.init_schema()

        # Create test company
        graph.create_company("test-company-001", "TestCorp", industry="Software", headquarters="San Francisco, CA")

        # Create test claim
        from .models import create_claim, SourceType

        claim = create_claim(
            entity_id="test-company-001",
            field="revenue",
            value=1000000,
            source_url="https://testcorp.com/about",
            snippet="Our revenue reached $1M in 2024",
            source_type=SourceType.WEBSITE,
        )
        claim.overall_confidence = 0.85

        graph.create_claim(claim)

        # Get claims
        claims = graph.get_claims_for_entity("test-company-001")
        print(f"Found {len(claims)} claims")

        # Get summary
        summary = graph.get_entity_evidence_summary("test-company-001")
        print(f"Evidence summary: {summary}")

        print("✅ Evidence graph test passed!")

    finally:
        graph.close()
