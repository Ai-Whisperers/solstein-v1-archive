"""Contradiction repository for Neo4j evidence graph.

EPIC-022: Extracted from EvidenceGraph for modularity.
"""

import logging
from typing import Any

from ..models import Contradiction
from .base import EvidenceGraphRepository

logger = logging.getLogger(__name__)


class ContradictionRepository(EvidenceGraphRepository):
    """Repository for contradiction entity operations."""

    def create(self, contradiction: Contradiction) -> None:
        """Create a contradiction and link to involved claims.

        Args:
            contradiction: Contradiction to create
        """
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

    def get_for_entity(self, entity_id: str) -> list[dict[str, Any]]:
        """Get all contradictions involving an entity's claims.

        Args:
            entity_id: Entity ID

        Returns:
            List of contradiction dictionaries
        """
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
