"""Database models package.

EPIC-021: Modularized database models.

This package contains all SQLAlchemy ORM models organized by domain:
- company: Company, scoring, signals, market snapshots, audit trails
- research: Research runs, stages, artifacts, sources, contradictions
- enrichment: Enrichment audit, cache, jobs, release gates
- infrastructure: Outbox, tenants

All models are re-exported from this package for convenience.
"""

from .base import Base

# Company and scoring models
from .company import (
    AuditTrailRecord,
    CompanyRecord,
    MarketSnapshot,
    ScoringRecord,
    SignalRecord,
)

# Enrichment models
from .enrichment import (
    EnrichmentAuditRecord,
    EnrichmentCacheRecord,
    EnrichmentJobRecord,
    ReleaseGateAuditRecord,
)

# Infrastructure models
from .infrastructure import ApiKeyRecord, ApiKeyUsageRecord, OutboxRecord, TenantRecord

# Research models
from .research import (
    ContradictionRecord,
    ContradictionTransitionRecord,
    EvidenceReadinessRecord,
    MetricObservationRecord,
    ResearchArtifactRecord,
    ResearchJobRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    SourceDocumentRecord,
)

__all__ = [
    # Base
    "Base",
    # Company
    "CompanyRecord",
    # Scoring
    "ScoringRecord",
    "SignalRecord",
    # Market
    "MarketSnapshot",
    # Audit
    "AuditTrailRecord",
    # Research
    "ResearchRunRecord",
    "OutboxRecord",
    "ResearchStageRecord",
    "ResearchArtifactRecord",
    "SourceDocumentRecord",
    "MetricObservationRecord",
    "EvidenceReadinessRecord",
    "ContradictionRecord",
    "ContradictionTransitionRecord",
    # Research Jobs (STORY-083)
    "ResearchJobRecord",
    # Enrichment
    "EnrichmentAuditRecord",
    "EnrichmentCacheRecord",
    "EnrichmentJobRecord",
    # Release
    "ReleaseGateAuditRecord",
    # Tenant
    "TenantRecord",
    # API Keys (EPIC-019)
    "ApiKeyRecord",
    "ApiKeyUsageRecord",
]
