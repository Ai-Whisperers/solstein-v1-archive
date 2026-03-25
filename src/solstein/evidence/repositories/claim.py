"""Claim repository for Neo4j evidence graph.

EPIC-022: Extracted from EvidenceGraph for modularity.
"""

import logging
from typing import Any

from ..models import Claim
from .base import EvidenceGraphRepository
from .company import CompanyRepository
from .source import SourceRepository

logger = logging.getLogger(__name__)


class ClaimRepository(EvidenceGraphRepository):
    """Repository for claim entity operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._company_repo = CompanyRepository(self.uri, self.user, self.password)
        self._source_repo = SourceRepository(self.uri, self.user, self.password)

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.netloc or url
        except Exception:
            return url

    def create(self, claim: Claim) -> None:
        """Create a claim and link it to company and source.

        Args:
            claim: Claim to create
        """
        # First ensure company exists
        self._company_repo.create(claim.entity_id, claim.entity_id)

        # Create source if not exists
        from ..models import SourceDocument

        source_doc = SourceDocument(
            url=claim.source_url,
            source_type=claim.source_type,
            title=claim.source_title,
            domain=self._extract_domain(claim.source_url),
        )
        self._source_repo.create(source_doc)

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

    def get_for_entity(
        self,
        entity_id: str,
        field: str | None = None,
        status: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Get claims for an entity with optional filters.

        Args:
            entity_id: Entity ID
            field: Optional field filter
            status: Optional status filter
            min_confidence: Minimum confidence threshold

        Returns:
            List of claim dictionaries
        """
        query = """
        MATCH (c:Company {id: $entity_id})-[:HAS_CLAIM]->(claim:Claim)
        WHERE claim.overall_confidence >= $min_confidence
        """

        if field:
            query += " AND claim.field = $field"
        if status:
            query += " AND claim.status = $status"

        query += """
        OPTIONAL MATCH (claim)-[:SOURCED_FROM]->(source:Source)
        RETURN {
            id: claim.id,
            field: claim.field,
            value: claim.value,
            unit: claim.unit,
            confidence: claim.overall_confidence,
            status: claim.status,
            source_url: source.url,
            source_title: source.title,
            extracted_at: claim.extracted_at
        } as claim
        ORDER BY claim.overall_confidence DESC
        """

        status_value = status.value if hasattr(status, "value") else status
        with self._get_session() as session:
            result = session.run(
                query,
                entity_id=entity_id,
                field=field,
                status=status_value,
                min_confidence=min_confidence,
            )
            return [dict(record["claim"]) for record in result]

    def update_status(self, claim_id: str, status: str, reason: str | None = None) -> None:
        """Update claim status.

        Args:
            claim_id: Claim ID
            status: New status
            reason: Optional reason for status change
        """
        query = """
        MATCH (c:Claim {id: $claim_id})
        SET c.status = $status,
            c.status_updated_at = datetime(),
            c.status_reason = $reason
        RETURN c
        """

        with self._get_session() as session:
            session.run(query, claim_id=claim_id, status=status, reason=reason)
            logger.info(f"Updated claim {claim_id} status to {status}")

    def get_evidence_lineage(self, claim_id: str) -> dict[str, Any]:
        """Get evidence lineage for a claim.

        Args:
            claim_id: Claim ID

        Returns:
            Lineage information
        """
        query = """
        MATCH (claim:Claim {id: $claim_id})
        OPTIONAL MATCH (claim)-[:SOURCED_FROM]->(source:Source)
        OPTIONAL MATCH (company:Company)-[:HAS_CLAIM]->(claim)
        OPTIONAL MATCH (claim)-[:CONTRADICTS]-(contradicting:Claim)
        OPTIONAL MATCH (claim)-[:SUPPORTS]-(supporting:Claim)

        RETURN {
            claim: claim,
            source: source,
            company: company,
            contradicting_claims: collect(DISTINCT contradicting),
            supporting_claims: collect(DISTINCT supporting)
        } as lineage
        """

        with self._get_session() as session:
            result = session.run(query, claim_id=claim_id)
            record = result.single()
            if record:
                lineage = record["lineage"]
                return {
                    "claim": dict(lineage["claim"]),
                    "source": dict(lineage["source"]) if lineage["source"] else None,
                    "company": dict(lineage["company"]) if lineage["company"] else None,
                    "contradicting_claims": [dict(c) for c in lineage["contradicting_claims"]],
                    "supporting_claims": [dict(c) for c in lineage["supporting_claims"]],
                }
            return {}
