"""
Evidence Service - Main service for evidence collection and management.

This module provides the high-level API for EPIC-042.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .models import Claim, ClaimStatus, EvidenceReadiness, SourceDocument
from .graph import EvidenceGraph
from .vector_store import EvidenceVectorStore
from .crawler import EvidenceCrawler, CrawlResult

logger = logging.getLogger(__name__)


class EvidenceService:
    """
    Main service for evidence collection, storage, and retrieval.

    Combines Neo4j graph, Qdrant vector search, and web crawling.
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "solstein123",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
    ):
        self.graph = EvidenceGraph(neo4j_uri, neo4j_user, neo4j_password)
        self.vector_store = EvidenceVectorStore(qdrant_host, qdrant_port)
        self.crawler = EvidenceCrawler()

        self._initialized = False

    def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return

        # Connect to databases
        self.graph.connect()
        self.vector_store.connect()

        # Initialize schemas
        self.graph.init_schema()
        self.vector_store.init_collection()

        self._initialized = True
        logger.info("Evidence service initialized")

    def close(self) -> None:
        """Close all connections."""
        self.graph.close()
        self._initialized = False
        logger.info("Evidence service closed")

    async def research_company(
        self,
        company_id: str,
        website_url: str,
        max_pages: int = 5,
    ) -> dict:
        """
        Research a company by crawling its website and extracting claims.

        This is the main entry point for company research.
        """
        if not self._initialized:
            self.initialize()

        logger.info(f"Starting research for {company_id} at {website_url}")

        # Crawl website
        self.crawler.max_pages = max_pages
        crawl_results = await self.crawler.crawl_company_website(
            company_id=company_id,
            start_url=website_url,
        )

        successful_crawls = [r for r in crawl_results if r.success]
        logger.info(f"Successfully crawled {len(successful_crawls)} pages")

        # Extract claims from crawled content
        all_claims: list[Claim] = []
        for result in successful_crawls:
            claims = self.crawler.extract_claims_from_content(result, company_id)
            all_claims.extend(claims)

        logger.info(f"Extracted {len(all_claims)} claims")

        # Store claims
        stored_claims = 0
        for claim in all_claims:
            try:
                # Store in Neo4j
                self.graph.create_claim(claim)

                # Index in Qdrant
                self.vector_store.index_claim(claim)

                stored_claims += 1
            except Exception as e:
                logger.error(f"Failed to store claim {claim.id}: {e}")

        logger.info(f"Stored {stored_claims} claims")

        # Detect contradictions
        contradictions = self._detect_contradictions(company_id)

        # Calculate evidence readiness
        readiness = self.calculate_evidence_readiness(company_id)

        return {
            "company_id": company_id,
            "pages_crawled": len(successful_crawls),
            "claims_extracted": len(all_claims),
            "claims_stored": stored_claims,
            "contradictions_detected": len(contradictions),
            "evidence_readiness": readiness,
        }

    def _detect_contradictions(self, company_id: str) -> list[dict]:
        """Detect contradictions for a company's claims."""
        # Get all claims for the company
        claims = self.graph.get_claims_for_entity(company_id)

        contradictions = []

        # Group claims by field
        by_field: dict[str, list[dict]] = {}
        for claim in claims:
            field = claim.get("field")
            if field:
                by_field.setdefault(field, []).append(claim)

        # Check for contradictions within each field
        for field, field_claims in by_field.items():
            if len(field_claims) < 2:
                continue

            # Find claims with different values
            values = {}
            for claim in field_claims:
                value = claim.get("value")
                if value:
                    values.setdefault(value, []).append(claim)

            # If multiple different values exist, it's a contradiction
            if len(values) > 1:
                from .models import Contradiction

                con = Contradiction(
                    claim_ids=[c.get("id") for c in field_claims],
                    field=field,
                    values=list(values.keys()),
                    severity="high" if field in ["revenue", "employee_count"] else "medium",
                )

                self.graph.create_contradiction(con)
                contradictions.append(
                    {
                        "field": field,
                        "values": list(values.keys()),
                        "severity": con.severity,
                    }
                )

        return contradictions

    def calculate_evidence_readiness(self, company_id: str) -> EvidenceReadiness:
        """Calculate evidence readiness for a company."""
        summary = self.graph.get_entity_evidence_summary(company_id)

        readiness = EvidenceReadiness(
            entity_id=company_id,
            total_claims=summary.get("total_claims", 0),
            avg_confidence=summary.get("avg_confidence", 0.0),
            pending_claims=summary.get("pending_count", 0),
            conflicting_claims=summary.get("conflicting_count", 0),
        )

        # Determine readiness level
        if readiness.total_claims == 0:
            readiness.level = "insufficient"
        elif readiness.avg_confidence < 0.5:
            readiness.level = "needs_more"
        elif readiness.conflicting_claims > 0:
            readiness.level = "decision_support"
        else:
            readiness.level = "investment_ready"

        return readiness

    def get_claims(
        self,
        company_id: str,
        field: Optional[str] = None,
        status: Optional[ClaimStatus] = None,
    ) -> list[dict]:
        """Get claims for a company."""
        if not self._initialized:
            self.initialize()

        return self.graph.get_claims_for_entity(company_id, field, status)

    def search_claims(
        self,
        query: str,
        company_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search claims semantically."""
        if not self._initialized:
            self.initialize()

        return self.vector_store.search_similar_claims(
            query=query,
            entity_id=company_id,
            limit=limit,
        )

    def get_evidence_lineage(self, claim_id: str) -> dict:
        """Get full evidence lineage for a claim."""
        if not self._initialized:
            self.initialize()

        return self.graph.get_evidence_lineage(claim_id)


# Singleton instance for easy access
_evidence_service: Optional[EvidenceService] = None


def get_evidence_service() -> EvidenceService:
    """Get or create the evidence service singleton."""
    global _evidence_service
    if _evidence_service is None:
        _evidence_service = EvidenceService()
    return _evidence_service
