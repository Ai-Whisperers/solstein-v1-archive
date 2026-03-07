"""Neo4j Evidence Graph - Graph database client for claims and relationships.

EPIC-042: Evidence Graph Implementation
EPIC-022: Refactored to use Repository Pattern

This module provides the Neo4j integration using modular repositories.
Each entity type (Company, Source, Claim, Contradiction) has its own
repository for clean separation of concerns.

FREE tools used:
- Neo4j Community Edition (free)
- neo4j Python driver
"""

from __future__ import annotations

import logging
from typing import Any

from .models import Claim, ClaimStatus, Contradiction, SourceDocument
from .repositories import (
    ClaimRepository,
    CompanyRepository,
    ContradictionRepository,
    SourceRepository,
)

logger = logging.getLogger(__name__)


class EvidenceGraph:
    """Neo4j-based evidence graph using Repository Pattern.

    EPIC-022: Refactored to delegate operations to specialized repositories.
    Each entity type has its own repository for modularity and testability.

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
        password: str = "password",
    ):
        """Initialize EvidenceGraph with repositories.

        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        # Initialize repositories
        self.companies = CompanyRepository(uri, user, password)
        self.sources = SourceRepository(uri, user, password)
        self.claims = ClaimRepository(uri, user, password)
        self.contradictions = ContradictionRepository(uri, user, password)

        logger.info(f"EvidenceGraph initialized with {uri}")

    def connect(self) -> None:
        """Connect to Neo4j database."""
        # Connect through any repository (they share the same connection)
        self.companies.connect()

    def close(self) -> None:
        """Close Neo4j connection."""
        self.companies.close()

    def init_schema(self) -> None:
        """Initialize the graph schema with constraints and indexes."""
        self.companies.init_schema()

    # Backward compatibility methods delegate to repositories
    def create_company(self, company_id: str, name: str, **properties) -> None:
        """Create or update a company node."""
        self.companies.create(company_id, name, **properties)

    def create_source(self, source: SourceDocument) -> None:
        """Create or update a source node."""
        self.sources.create(source)

    def create_claim(self, claim: Claim) -> None:
        """Create a claim and link it to company and source."""
        self.claims.create(claim)

    def create_contradiction(self, contradiction: Contradiction) -> None:
        """Create a contradiction and link to involved claims."""
        self.contradictions.create(contradiction)

    def get_claims_for_entity(
        self,
        entity_id: str,
        field: str | None = None,
        status: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[dict[str, Any]]:
        """Get claims for an entity with optional filters."""
        return self.claims.get_for_entity(entity_id, field, status, min_confidence)

    def get_contradictions_for_entity(self, entity_id: str) -> list[dict[str, Any]]:
        """Get all contradictions involving an entity's claims."""
        return self.contradictions.get_for_entity(entity_id)

    def get_evidence_lineage(self, claim_id: str) -> dict[str, Any]:
        """Get full evidence lineage for a claim."""
        return self.claims.get_evidence_lineage(claim_id)

    def update_claim_status(
        self,
        claim_id: str,
        status: ClaimStatus,
        reviewed_by: str | None = None,
        notes: str | None = None,
    ) -> None:
        """Update claim status."""
        self.claims.update_status(claim_id, status.value, notes)

    def get_entity_evidence_summary(self, entity_id: str) -> dict[str, Any]:
        """Get evidence summary for an entity."""
        return self.companies.get_evidence_summary(entity_id)
