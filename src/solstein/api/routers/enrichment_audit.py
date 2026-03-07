"""Audit trail endpoint.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, Query, Request

from solstein.api.schemas.enrichment import AuditEntry, AuditTrailResponse
from solstein.data.security_hardening import audit_logger, rate_limiter

from .enrichment_base import get_audit_repo_if_available, get_client_id, logger, router


@router.get("/companies/{company_id}/enrichment/audit", response_model=AuditTrailResponse)
async def get_audit_trail(
    company_id: str, limit: int = Query(50, ge=1, le=1000), offset: int = Query(0, ge=0), request: Request = None
) -> AuditTrailResponse:
    """Get enrichment audit trail for company."""
    if not request:
        raise HTTPException(status_code=500, detail="Request context required")

    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📜 Audit trail request for {company_id}")

    audit_repo = await get_audit_repo_if_available()
    mapped_entries = []

    if audit_repo:
        try:
            db_entries = await audit_repo.get_audit_trail(company_id=company_id, limit=limit, offset=offset)
            for entry in db_entries:
                mapped_entries.append(
                    AuditEntry(
                        timestamp=entry.timestamp,
                        operation=entry.operation,
                        source=entry.source,
                        status=entry.status,
                        fields=entry.fields_enriched,
                        duration_ms=entry.duration_ms,
                        user_id=entry.user_id,
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to get audit trail from database: {e}. Falling back to in-memory logger.")
            audit_entries = audit_logger.get_audit_trail(company_id=company_id)
            if audit_entries:
                for entry in audit_entries[:limit]:
                    ts = entry.get("timestamp")
                    if isinstance(ts, str):
                        from datetime import datetime as dt

                        ts = dt.fromisoformat(ts)
                    else:
                        ts = ts or datetime.now(timezone.utc)

                    mapped_entries.append(
                        AuditEntry(
                            timestamp=ts,
                            operation=entry.get("operation", "unknown"),
                            source=entry.get("source"),
                            status=entry.get("status"),
                            fields=entry.get("fields"),
                            duration_ms=entry.get("duration_ms"),
                            user_id=entry.get("user_id"),
                        )
                    )
    else:
        audit_entries = audit_logger.get_audit_trail(company_id=company_id)
        if audit_entries:
            for entry in audit_entries[:limit]:
                ts = entry.get("timestamp")
                if isinstance(ts, str):
                    from datetime import datetime as dt

                    ts = dt.fromisoformat(ts)
                else:
                    ts = ts or datetime.now(timezone.utc)

                mapped_entries.append(
                    AuditEntry(
                        timestamp=ts,
                        operation=entry.get("operation", "unknown"),
                        source=entry.get("source"),
                        status=entry.get("status"),
                        fields=entry.get("fields"),
                        duration_ms=entry.get("duration_ms"),
                        user_id=entry.get("user_id"),
                    )
                )

    return AuditTrailResponse(
        company_id=company_id,
        company_name=None,
        audit_entries=mapped_entries,
        summary=audit_logger.get_stats(),
    )
