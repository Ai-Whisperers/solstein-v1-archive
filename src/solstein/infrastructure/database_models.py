"""Database models for Solstein.

EPIC-021: This file now re-exports from the modular models package.
The original monolithic implementation has been split into:
- models/company.py - Company, scoring, signals, market, audit
- models/research.py - Research runs, stages, artifacts, contradictions
- models/enrichment.py - Enrichment audit, cache, jobs
- models/infrastructure.py - Outbox, tenants
- models/base.py - SQLAlchemy Base

This file maintains backward compatibility for existing imports.
"""

# Re-export all models from the new modular package
from solstein.infrastructure.models import (
    AuditTrailRecord,
    Base,
    CompanyRecord,
    ContradictionRecord,
    ContradictionTransitionRecord,
    EnrichmentAuditRecord,
    EnrichmentCacheRecord,
    EnrichmentJobRecord,
    EvidenceReadinessRecord,
    MarketSnapshot,
    MetricObservationRecord,
    OutboxRecord,
    ReleaseGateAuditRecord,
    ResearchArtifactRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    ScoringRecord,
    SignalRecord,
    SourceDocumentRecord,
    TenantRecord,
)

__all__ = [
    "Base",
    "CompanyRecord",
    "ScoringRecord",
    "SignalRecord",
    "MarketSnapshot",
    "AuditTrailRecord",
    "ResearchRunRecord",
    "OutboxRecord",
    "ResearchStageRecord",
    "ResearchArtifactRecord",
    "SourceDocumentRecord",
    "MetricObservationRecord",
    "EvidenceReadinessRecord",
    "ContradictionRecord",
    "ContradictionTransitionRecord",
    "EnrichmentAuditRecord",
    "EnrichmentCacheRecord",
    "EnrichmentJobRecord",
    "ReleaseGateAuditRecord",
    "TenantRecord",
]
