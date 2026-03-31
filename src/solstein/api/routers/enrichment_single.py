"""Single company enrichment endpoint.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

import time

from fastapi import HTTPException, Request

from solstein.api.schemas.enrichment import EnrichmentRequest, EnrichmentResponse, EnrichmentResultData
from solstein.data.security_hardening import audit_logger, input_validator, rate_limiter
from solstein.data.unified_loader import UnifiedCompany

from .enrichment_base import (
    get_audit_repo_if_available,
    get_cache_repo_if_available,
    get_client_id,
    logger,
    router,
    unified_loader,
)


@router.post("/companies/{company_id}/enrich", response_model=EnrichmentResponse)
async def enrich_single_company(
    company_id: str, request_data: EnrichmentRequest, request: Request
) -> EnrichmentResponse:
    """Enrich a single company from available sources."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    is_valid, error = input_validator.validate_company_id(company_id)
    if not is_valid:
        audit_logger.log_validation_failure(
            company_name=company_id,
            company_id=company_id,
            validation_rule="company_id_format",
            reason=error or "Invalid format",
        )
        raise HTTPException(status_code=400, detail=error)

    logger.info(f"💼 Enriching company {company_id} from {request_data.sources}")

    audit_repo = await get_audit_repo_if_available()
    cache_repo = await get_cache_repo_if_available()

    if audit_repo:
        await audit_repo.log_operation(
            company_id=company_id,
            company_name=company_id,
            operation="enrich_start",
            source=",".join(request_data.sources),
            status="IN_PROGRESS",
        )
    else:
        audit_logger.log_enrichment_start(
            company_name=company_id, company_id=company_id, source=",".join(request_data.sources)
        )

    try:
        cached_company = None
        if cache_repo:
            try:
                cached_record = await cache_repo.get_cached(company_id)
                if cached_record:
                    logger.info(f"💾 Cache hit for {company_id}")
                    cached_company = cached_record.enriched_data
                    if audit_repo:
                        await audit_repo.log_operation(
                            company_id=company_id,
                            company_name=company_id,
                            operation="cache_hit",
                            source="cache",
                            status="SUCCESS",
                            duration_ms=0,
                        )
            except Exception as e:
                logger.debug(f"Cache read failed for {company_id}: {e}")

        company = UnifiedCompany(id=company_id, name=company_id)

        start_time = time.time()
        enriched = unified_loader.enrich_from_connectors(company)
        duration_ms = int((time.time() - start_time) * 1000)

        fields_enriched = []
        if (
            enriched.financials
            and enriched.financials.revenue
            and (not company.financials or not company.financials.revenue)
        ):
            fields_enriched.append("revenue")
        if (
            enriched.financials
            and enriched.financials.employees
            and (not company.financials or not company.financials.employees)
        ):
            fields_enriched.append("employees")

        if cache_repo and not cached_company:
            try:
                await cache_repo.cache_enrichment(
                    company_id=company_id,
                    enriched_data=enriched.model_dump(mode="json"),
                    sources_used=request_data.sources,
                    fields_enriched=fields_enriched,
                    ttl_seconds=86400,
                )
            except Exception as e:
                logger.warning(f"Failed to cache enrichment for {company_id}: {e}")

        if audit_repo:
            await audit_repo.log_operation(
                company_id=company_id,
                company_name=enriched.name or company_id,
                operation="enrich_success",
                source=",".join(request_data.sources),
                status="SUCCESS",
                duration_ms=duration_ms,
                fields_enriched=fields_enriched,
            )
        else:
            audit_logger.log_enrichment_success(
                company_name=enriched.name or company_id,
                company_id=company_id,
                source=",".join(request_data.sources),
                duration_ms=duration_ms,
                fields_enriched=fields_enriched,
            )

        return EnrichmentResponse(
            company_id=company_id,
            company_name=enriched.name or company_id,
            status="success",
            enrichment={
                "sources_used": request_data.sources,
                "fields_enriched": fields_enriched,
                "duration_ms": duration_ms,
            },
            data=EnrichmentResultData(
                revenue=enriched.financials.revenue if enriched.financials else None,
                employees=enriched.financials.employees if enriched.financials else None,
                growth_rate=enriched.financials.growth_rate if enriched.financials else None,
                profit_margin=enriched.financials.profit_margin if enriched.financials else None,
                funding_raised=enriched.financials.funding_raised if enriched.financials else None,
                valuation=enriched.financials.valuation if enriched.financials else None,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        if audit_repo:
            await audit_repo.log_operation(
                company_id=company_id,
                company_name=company_id,
                operation="enrich_failure",
                source=",".join(request_data.sources),
                status="FAILURE",
                error_message=str(e),
            )
        else:
            audit_logger.log_enrichment_failure(
                company_name=company_id,
                company_id=company_id,
                source=",".join(request_data.sources),
                error=str(e),
            )
        raise HTTPException(status_code=500, detail=str(e)) from e
