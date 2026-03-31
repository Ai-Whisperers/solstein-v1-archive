"""
Evidence Graph System - Public-web intelligence for Solstein.

EPIC-042: Evidence Graph and Claim Provenance
EPIC-041: Deep Web Crawling and Document Ingestion

All components use FREE tools:
- Neo4j Community Edition (graph database)
- Qdrant (vector search)
- Crawl4AI (web crawling)
- sentence-transformers (embeddings)
"""

from .crawler import CrawlResult, EvidenceCrawler, SimpleCrawler
from .graph import EvidenceGraph
from .models import (
    COMPANY_METRIC_FIELDS,
    CRITICAL_FIELDS,
    Claim,
    ClaimStatus,
    ConfidenceComponent,
    Contradiction,
    EvidenceReadiness,
    SourceDocument,
    SourceType,
    create_claim,
)
from .service import EvidenceService, get_evidence_service
from .vector_store import EvidenceVectorStore

__all__ = [
    # Models
    "Claim",
    "ClaimStatus",
    "SourceDocument",
    "SourceType",
    "Contradiction",
    "EvidenceReadiness",
    "ConfidenceComponent",
    "create_claim",
    "COMPANY_METRIC_FIELDS",
    "CRITICAL_FIELDS",
    # Components
    "EvidenceGraph",
    "EvidenceVectorStore",
    "EvidenceCrawler",
    "CrawlResult",
    "SimpleCrawler",
    # Service
    "EvidenceService",
    "get_evidence_service",
]
