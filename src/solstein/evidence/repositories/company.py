"""Company repository for Neo4j evidence graph.

EPIC-022: Extracted from EvidenceGraph for modularity.
"""

import logging
from typing import Any

from .base import EvidenceGraphRepository

logger = logging.getLogger(__name__)


class CompanyRepository(EvidenceGraphRepository):
    """Repository for company entity operations."""

    def create(self, company_id: str, name: str, **properties) -> None:
        """Create or update a company node.

        Args:
            company_id: Unique company identifier
            name: Company name
            **properties: Additional company properties
        """
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

    def get_evidence_summary(self, entity_id: str) -> dict[str, Any]:
        """Get evidence summary for a company.

        Args:
            entity_id: Company ID

        Returns:
            Evidence summary with claim counts and contradictions
        """
        query = """
        MATCH (c:Company {id: $entity_id})
        OPTIONAL MATCH (c)-[:HAS_CLAIM]->(claim:Claim)
        OPTIONAL MATCH (claim)-[:CONTRADICTS]-(contradiction:Contradiction)
        RETURN {
            company_id: c.id,
            company_name: c.name,
            total_claims: count(DISTINCT claim),
            verified_claims: count(DISTINCT CASE WHEN claim.status = 'VERIFIED' THEN claim END),
            disputed_claims: count(DISTINCT CASE WHEN claim.status = 'DISPUTED' THEN claim END),
            contradictions: count(DISTINCT contradiction),
            avg_confidence: avg(claim.overall_confidence)
        } as summary
        """

        with self._get_session() as session:
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            return dict(record["summary"]) if record else {}
