"""Service for managing drill-down data and audit trail retrieval."""

from solstein.domain.models import CompanyAnalysisAuditTrail


class DrillDownService:
    """Service for managing and retrieving audit trails for transparency."""

    def __init__(self):
        """Initialize drill-down service with in-memory storage."""
        self._audit_trails: dict[str, CompanyAnalysisAuditTrail] = {}

    def store_audit_trail(self, audit_trail: CompanyAnalysisAuditTrail) -> None:
        """Store an audit trail for a company."""
        self._audit_trails[audit_trail.company_id] = audit_trail

    def get_audit_trail(self, company_id: str) -> CompanyAnalysisAuditTrail | None:
        """Retrieve an audit trail for a company."""
        return self._audit_trails.get(company_id)

    def get_signals(self, company_id: str) -> list | None:
        """Get extracted signals for a company."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.extracted_signals:
            return None
        return audit_trail.extracted_signals.signals

    def get_facts(self, company_id: str, min_confidence: float = 0.0) -> list | None:
        """Get aggregated facts for a company, filtered by confidence."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.aggregated_facts:
            return None
        return [
            f
            for f in audit_trail.aggregated_facts.facts
            if f.confidence >= min_confidence
        ]

    def get_sources(self, company_id: str, fact_type: str | None = None) -> list | None:
        """Get raw sources for a company, optionally filtered by fact type."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.raw_data:
            return None

        sources = audit_trail.raw_data.sources

        if fact_type:
            filtered = []
            for source in sources:
                if source.metadata and "facts" in source.metadata:
                    facts = source.metadata["facts"]
                    if any(f.get("type") == fact_type for f in facts):
                        filtered.append(source)
            return filtered

        return sources

    def get_source_details(self, company_id: str, source_id: str) -> dict | None:
        """Get details about a specific source."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.raw_data:
            return None

        for source in audit_trail.raw_data.sources:
            if source.id == source_id:
                return {
                    "source_id": source.id,
                    "source_name": source.source_name,
                    "source_type": source.source_type.value,
                    "url": source.url,
                    "confidence": source.confidence,
                    "retrieval_timestamp": source.retrieval_timestamp,
                    "raw_content": source.raw_content,
                    "metadata": source.metadata,
                    "facts": source.metadata.get("facts", [])
                    if source.metadata
                    else [],
                }
        return None

    def get_fact_details(
        self, company_id: str, fact_type: str, value: str
    ) -> dict | None:
        """Get details about a specific aggregated fact."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.aggregated_facts:
            return None

        for fact in audit_trail.aggregated_facts.facts:
            if fact.fact_type == fact_type and fact.value == value:
                return {
                    "fact_type": fact.fact_type,
                    "value": fact.value,
                    "confidence": fact.confidence,
                    "sources_used": fact.sources_used,
                    "source_agreement_percentage": fact.source_agreement_percentage,
                }
        return None

    def get_contradictions(self, company_id: str) -> list | None:
        """Get detected contradictions for a company."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail or not audit_trail.aggregated_facts:
            return None

        contradictions = []
        for fact in audit_trail.aggregated_facts.facts:
            if hasattr(fact, "contradiction_detected") and fact.contradiction_detected:
                contradictions.append(
                    {
                        "fact_type": fact.fact_type,
                        "value": fact.value,
                        "confidence": fact.confidence,
                    }
                )
        return contradictions

    def get_data_quality(self, company_id: str) -> dict | None:
        """Get data quality metrics for a company."""
        audit_trail = self.get_audit_trail(company_id)
        if not audit_trail:
            return None

        return {
            "completeness": audit_trail.data_completeness,
            "average_confidence": (
                audit_trail.aggregated_facts.average_confidence
                if audit_trail.aggregated_facts
                else 0.0
            ),
            "sources_count": len(audit_trail.raw_data.sources)
            if audit_trail.raw_data
            else 0,
            "confidence_level": audit_trail.confidence_level,
            "coverage_gaps": getattr(audit_trail, "coverage_gaps", []),
        }


# Global instance for now (will be dependency-injected later)
_drill_down_service = DrillDownService()


def get_drill_down_service() -> DrillDownService:
    """Get the drill-down service instance."""
    return _drill_down_service
