from fastapi import APIRouter, Depends, HTTPException

from solstein.domain.models import CompanyAnalysisAuditTrail

from ..dependencies import get_drill_down_service
from ..services.drill_down_service import DrillDownService

router = APIRouter(prefix="/drill-down", tags=["transparency"])


@router.get("/company/{company_id}/why/{signal_name}")
async def why_signal(
    company_id: str,
    signal_name: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """Explain why a company received a specific signal value."""
    signals = await service.get_signals(company_id)

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
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """List all sources gathered for a company."""
    sources = await service.get_sources(company_id, fact_type)

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
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """Get detailed information about a specific source."""
    details = await service.get_source_details(company_id, source_id)

    if not details:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")

    return details


@router.get("/company/{company_id}/facts")
async def list_facts(
    company_id: str,
    min_confidence: float = 0.0,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """List all aggregated facts for a company."""
    facts = await service.get_facts(company_id, min_confidence)

    if facts is None:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    contradictions = await service.get_contradictions(company_id) or []

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
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """Get detailed information about a specific fact."""
    details = await service.get_fact_details(company_id, fact_type, value)

    if not details:
        raise HTTPException(
            status_code=404,
            detail=f"Fact {fact_type}={value} not found for {company_id}",
        )

    return details


@router.get("/company/{company_id}/audit-trail")
async def audit_trail(
    company_id: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> CompanyAnalysisAuditTrail:
    """Get complete audit trail for a company analysis."""
    trail = await service.get_audit_trail(company_id)

    if not trail:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return trail


@router.get("/company/{company_id}/signals")
async def list_signals(
    company_id: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """List all extracted business signals for a company."""
    signals = await service.get_signals(company_id)

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
async def list_contradictions(
    company_id: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """List all contradictions detected during analysis."""
    contradictions = await service.get_contradictions(company_id) or []

    return {
        "company_id": company_id,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions,
    }


@router.get("/company/{company_id}/data-quality")
async def data_quality(
    company_id: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """Get data quality metrics for a company analysis."""
    metrics = await service.get_data_quality(company_id)

    if not metrics:
        raise HTTPException(
            status_code=404, detail=f"No analysis found for {company_id}"
        )

    return {
        "company_id": company_id,
        **metrics,
    }


@router.get("/company/{company_id}/timeline")
async def analysis_timeline(
    company_id: str,
    service: DrillDownService = Depends(get_drill_down_service),
) -> dict:
    """Get timeline of the analysis process."""
    trail = await service.get_audit_trail(company_id)

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
