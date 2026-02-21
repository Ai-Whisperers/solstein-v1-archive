"""Drill-down API endpoints for reasoning transparency.

Allows PE clients to explore the reasoning behind scores,
view all evidence, and understand source attribution.
"""

from fastapi import APIRouter, HTTPException

from solstein.api.services.drill_down_service import get_drill_down_service
from solstein.domain.models import CompanyAnalysisAuditTrail

router = APIRouter(prefix="/drill-down", tags=["transparency"])


def _get_service():
    return get_drill_down_service()


@router.get("/company/{company_id}/why/{signal_name}")
async def why_signal(
    company_id: str,
    signal_name: str,
) -> dict:
    """Explain why a company received a specific signal value.

    Shows:
    - Signal value and confidence
    - Contributing facts and sources
    - Reasoning/calculation method
    - Source credibility scores
    - Contradictions (if any)
    """
    service = _get_service()
    signals = service.get_signals(company_id)

    if not signals:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    for signal in signals:
        if signal.signal_name == signal_name:
            return {
                "company_id": company_id,
                "signal_name": signal.signal_name,
                "signal_value": signal.signal_value,
                "confidence": signal.signal_confidence,
                "reasoning": f"Calculated via {signal.calculation_method}",
                "source_facts": signal.source_facts,
                "calculation_method": signal.calculation_method,
            }

    raise HTTPException(
        status_code=404, detail=f"Signal {signal_name} not found for {company_id}"
    )


@router.get("/company/{company_id}/sources")
async def list_sources(
    company_id: str,
    fact_type: str | None = None,
) -> dict:
    """List all sources gathered for a company.

    Optionally filtered by fact type (e.g., 'revenue', 'employee_count').

    Shows:
    - Source name and type
    - URL/reference
    - Retrieval timestamp
    - Extracted facts from this source
    - Confidence score
    """
    service = _get_service()
    sources = service.get_sources(company_id, fact_type)

    if sources is None:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return {
        "company_id": company_id,
        "total_sources": len(sources),
        "fact_type_filter": fact_type,
        "sources": [
            {
                "source_id": s.id,
                "source_name": s.source_name,
                "source_type": s.source_type.value,
                "url": s.url,
                "confidence": s.confidence,
                "retrieval_timestamp": s.retrieval_timestamp.isoformat(),
                "facts_found": len(s.metadata.get("facts", [])) if s.metadata else 0,
            }
            for s in sources
        ],
    }


@router.get("/company/{company_id}/source/{source_id}")
async def source_details(
    company_id: str,
    source_id: str,
) -> dict:
    """Get detailed information about a specific source.

    Shows:
    - Original raw content (article text, filing data, etc.)
    - Publication date
    - Source credibility
    - Extracted facts
    - Agreement with other sources
    """
    service = _get_service()
    details = service.get_source_details(company_id, source_id)

    if not details:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")

    return details


@router.get("/company/{company_id}/facts")
async def list_facts(
    company_id: str,
    min_confidence: float = 0.0,
) -> dict:
    """List all aggregated facts for a company.

    Shows:
    - Fact type and value
    - Confidence score
    - Agreement across sources
    - Contributing sources
    - Contradictions (if any)
    """
    service = _get_service()
    facts = service.get_facts(company_id, min_confidence)

    if facts is None:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    contradictions = service.get_contradictions(company_id) or []

    return {
        "company_id": company_id,
        "facts_count": len(facts),
        "min_confidence_filter": min_confidence,
        "facts": [
            {
                "fact_type": f.fact_type,
                "value": f.value,
                "confidence": f.confidence,
                "sources_used": f.sources_used,
                "source_agreement_percentage": f.source_agreement_percentage,
            }
            for f in facts
        ],
        "contradictions_count": len(contradictions),
        "contradictions": contradictions,
    }


@router.get("/company/{company_id}/fact/{fact_type}")
async def fact_details(
    company_id: str,
    fact_type: str,
    value: str,
) -> dict:
    """Get detailed information about a specific fact.

    Shows:
    - Fact type, value, and confidence
    - All sources that support this fact
    - Source agreement percentage
    - Contradiction details (if any)
    - Source credibility breakdown
    """
    service = _get_service()
    details = service.get_fact_details(company_id, fact_type, value)

    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Fact {fact_type}={value} not found for {company_id}",
        )

    return details


@router.get("/company/{company_id}/audit-trail")
async def audit_trail(company_id: str) -> CompanyAnalysisAuditTrail:
    """Get complete audit trail for a company analysis.

    Returns:
    - All raw sources gathered
    - All aggregated facts
    - All extracted signals
    - Analysis metadata (timing, completeness, confidence)
    """
    service = _get_service()
    trail = service.get_audit_trail(company_id)

    if not trail:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return trail


@router.get("/company/{company_id}/signals")
async def list_signals(company_id: str) -> dict:
    """List all extracted business signals for a company.

    Shows:
    - Signal name and value
    - Calculation method
    - Source facts used
    - Signal confidence
    - Reasoning
    """
    service = _get_service()
    signals = service.get_signals(company_id)

    if signals is None:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return {
        "company_id": company_id,
        "signals_count": len(signals),
        "signals": [
            {
                "signal_name": s.signal_name,
                "signal_value": s.signal_value,
                "signal_confidence": s.signal_confidence,
                "calculation_method": s.calculation_method,
                "source_facts": s.source_facts,
            }
            for s in signals
        ],
    }


@router.get("/company/{company_id}/contradictions")
async def list_contradictions(company_id: str) -> dict:
    """List all contradictions detected during analysis.

    Shows:
    - Fact type
    - Conflicting values and sources
    - Resolution strategy (which source is trusted more)
    - Notes from coordinator
    """
    service = _get_service()
    contradictions = service.get_contradictions(company_id) or []

    return {
        "company_id": company_id,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions,
    }


@router.get("/company/{company_id}/data-quality")
async def data_quality(company_id: str) -> dict:
    """Get data quality metrics for a company analysis.

    Shows:
    - Data completeness percentage
    - Average fact confidence
    - Number of sources gathered
    - Coverage gaps
    - Confidence level (very_high, high, medium, low)
    """
    service = _get_service()
    metrics = service.get_data_quality(company_id)

    if not metrics:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return {
        "company_id": company_id,
        **metrics,
    }


@router.get("/company/{company_id}/timeline")
async def analysis_timeline(company_id: str) -> dict:
    """Get timeline of the analysis process.

    Shows:
    - Analysis start/end time
    - Duration
    - Agent execution times
    - Batch ID and metadata
    """
    service = _get_service()
    trail = service.get_audit_trail(company_id)

    if not trail:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return {
        "company_id": company_id,
        "started_at": (
            trail.analysis_started_at.isoformat() if trail.analysis_started_at else None
        ),
        "completed_at": (
            trail.analysis_completed_at.isoformat()
            if trail.analysis_completed_at
            else None
        ),
        "duration_seconds": trail.analysis_duration_seconds,
        "batch_id": trail.gathering_batch_id,
    }
