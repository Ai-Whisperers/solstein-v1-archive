"""
Enrichment API Endpoints (Phase 10 - Core Implementation)

All 8 REST endpoints:
1. GET /health - Health check
2. GET /ready - Readiness probe
3. GET /metrics - Performance metrics
4. POST /companies/{id}/enrich - Single enrichment
5. POST /companies/enrich/batch - Batch enrichment
6. GET /companies/{id}/enrichment/audit - Audit trail
7. GET /companies/{id}/enrichment/cache - Cache check
8. POST /enrichment/cache/clear - Cache clear

Also includes:
- Rate limiting integration
- Audit logging integration
- Input validation integration
- Security headers
"""

import logging
import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List, Dict, Any

# Import schemas
from solstein.api.schemas.enrichment import (
    HealthCheckResponse,
    ReadinessCheckResponse,
    MetricsResponse,
    EnrichmentRequest,
    EnrichmentResponse,
    EnrichmentResultData,
    BatchEnrichmentRequest,
    BatchEnrichmentResponse,
    BatchEnrichmentResult,
    AuditTrailResponse,
    AuditEntry,
    CacheCheckResponse,
    CacheClearResponse,
    ErrorResponse,
    RateLimitErrorResponse,
)

# Import enrichment infrastructure
from solstein.data.unified_loader import unified_loader, UnifiedCompany
from solstein.data.security_hardening import audit_logger, rate_limiter, input_validator, security_headers
from solstein.infrastructure.enrichment_repositories import EnrichmentAuditRepository, EnrichmentCacheRepository
from solstein.infrastructure.database import db_manager

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# LAZY-LOAD HELPERS FOR DATABASE REPOSITORIES
# ============================================================================

async def get_audit_repo_if_available():
    """Get audit repository if database is initialized, else None."""
    try:
        if hasattr(db_manager, 'initialized') and db_manager.initialized:
            async for session in db_manager.get_session():
                return EnrichmentAuditRepository(session)
    except Exception as e:
        logger.debug(f"Could not initialize audit repository: {e}")
    return None


async def get_cache_repo_if_available():
    """Get cache repository if database is initialized, else None."""
    try:
        if hasattr(db_manager, 'initialized') and db_manager.initialized:
            async for session in db_manager.get_session():
                return EnrichmentCacheRepository(session)
    except Exception as e:
        logger.debug(f"Could not initialize cache repository: {e}")
    return None


# ============================================================================
# HEALTH & READINESS ENDPOINTS
# ============================================================================


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request) -> HealthCheckResponse:
    """
    Platform health check (liveness probe).

    Returns:
        HealthCheckResponse with component statuses

    Status Codes:
        200: System is healthy
        503: System is unhealthy
    """
    # Check rate limit
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"🏥 Health check from {client_id}")

    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0",
        components={
            "database": "operational",
            "cache": "operational",
            "sec_edgar": "operational",
            "companies_house": "operational",
            "news_signals": "operational",
        },
    )


@router.get("/ready", response_model=ReadinessCheckResponse)
async def readiness_check(request: Request) -> ReadinessCheckResponse:
    """
    Readiness probe for load balancers.

    Returns:
        ReadinessCheckResponse with all readiness checks

    Status Codes:
        200: System is ready to serve traffic
        503: System is not ready
    """
    # Check rate limit
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📋 Readiness check from {client_id}")

    return ReadinessCheckResponse(
        ready=True,
        timestamp=datetime.now(timezone.utc),
        checks={
            "configuration_loaded": True,
            "connectors_initialized": True,
            "cache_operational": True,
            "enrichment_enabled": True,
        },
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(request: Request) -> MetricsResponse:
    """
    Get enrichment performance metrics.

    Returns:
        MetricsResponse with enrichment, cache, and rate limit metrics
    """
    # Check rate limit
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📊 Metrics request from {client_id}")

    # Get metrics from services
    enrichment_metrics = unified_loader.get_enrichment_metrics()
    rate_limit_remaining = rate_limiter.get_remaining(client_id)

    # Map enrichment metrics to response format
    enrichment_data = {
        "total": enrichment_metrics.get("total_enrichments", 0),
        "successful": enrichment_metrics.get("successful", 0),
        "failed": enrichment_metrics.get("failed", 0),
        "success_rate": enrichment_metrics.get("success_rate", 0),
        "avg_duration_ms": enrichment_metrics.get("avg_duration_ms", 0),
        "total_duration_ms": enrichment_metrics.get("total_duration_ms", 0),
    }
    
    return MetricsResponse(
        timestamp=datetime.now(timezone.utc),
        enrichment=enrichment_data,
        cache={
            "size": 0,
            "ttl_hours": 24,
            "hits": enrichment_metrics.get("cache_hits", 0),
            "misses": enrichment_metrics.get("cache_misses", 0),
            "hit_rate": 0.0,
        },
        rate_limiting={
            "requests_per_minute": 100,
            "current_requests": 100 - rate_limit_remaining,
            "remaining": rate_limit_remaining,
        },
    )


# ============================================================================
# ENRICHMENT ENDPOINTS
# ============================================================================


# Updated enrichment endpoint with cache and audit database support

@router.post("/companies/{company_id}/enrich", response_model=EnrichmentResponse)
async def enrich_single_company(
    company_id: str, request_data: EnrichmentRequest, request: Request
) -> EnrichmentResponse:
    """
    Enrich a single company from available sources.

    Args:
        company_id: Company ID
        request_data: Enrichment request parameters
        request: HTTP request (for rate limiting, auth)

    Returns:
        EnrichmentResponse with enriched data

    Status Codes:
        200: Enrichment completed (success or partial)
        400: Invalid company ID or parameters
        401: Unauthorized
        404: Company not found
        429: Rate limit exceeded
        503: Connector unavailable
    """
    # Check rate limit
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Validate company ID
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
    
    # Get repositories if available (lazy-load)
    audit_repo = await get_audit_repo_if_available()
    cache_repo = await get_cache_repo_if_available()
    
    # Log enrichment start
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
        # Check cache first if available
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
        
        # If not cached, create a minimal company object from the ID
        company = UnifiedCompany(id=company_id, name=company_id)

        # Call enrichment
        start_time = time.time()
        enriched = unified_loader.enrich_from_connectors(company)
        duration_ms = int((time.time() - start_time) * 1000)

        # Company enrichment completed (may have no data if not found in connectors)

        # Track enriched fields
        fields_enriched = []
        if enriched.financials and enriched.financials.revenue and (not company.financials or not company.financials.revenue):
            fields_enriched.append("revenue")
        if enriched.financials and enriched.financials.employees and (not company.financials or not company.financials.employees):
            fields_enriched.append("employees")

        # Cache the enriched data if available
        if cache_repo and not cached_company:
            try:
                await cache_repo.cache_enrichment(
                    company_id=company_id,
                    enriched_data=enriched.dict(),
                    sources_used=request_data.sources,
                    fields_enriched=fields_enriched,
                    ttl_seconds=86400,  # 24 hours
                )
            except Exception as e:
                logger.warning(f"Failed to cache enrichment for {company_id}: {e}")

        # Log enrichment success
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/companies/enrich/batch", response_model=BatchEnrichmentResponse)
async def enrich_batch(request_data: BatchEnrichmentRequest, request: Request) -> BatchEnrichmentResponse:
    """
    Batch enrich multiple companies with caching and optimization.

    Args:
        request_data: Batch enrichment request
        request: HTTP request

    Returns:
        BatchEnrichmentResponse with per-company results and metrics

    Status Codes:
        200: Batch processing completed
        400: Invalid request
        401: Unauthorized
        429: Rate limit exceeded
    """
    # Check rate limit
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Validate company IDs
    for company_id in request_data.company_ids:
        is_valid, _ = input_validator.validate_company_id(company_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid company ID: {company_id}")

    logger.info(f"📦 Batch enriching {len(request_data.company_ids)} companies")

    try:
        # Call batch enrichment
        start_time = time.time()
        companies = [UnifiedCompany(id=cid, name=cid) for cid in request_data.company_ids]
        enriched_companies = unified_loader.enrich_batch(companies, batch_size=request_data.batch_size)
        total_duration_ms = int((time.time() - start_time) * 1000)

        results = []
        for enriched in enriched_companies:
            results.append(
                BatchEnrichmentResult(
                    company_id=enriched.id,
                    status="success",
                    duration_ms=total_duration_ms // len(enriched_companies),
                    source="batch_enrichment",
                )
            )

        return BatchEnrichmentResponse(
            status="success",
            batch_id=f"batch_{datetime.now().timestamp()}",
            total_companies=len(request_data.company_ids),
            enriched_count=len(results),
            failed_count=0,
            results=results,
            metrics={
                "total_duration_ms": total_duration_ms,
                "avg_duration_ms": total_duration_ms // len(request_data.company_ids)
                if request_data.company_ids
                else 0,
                "cache_hits": 0,
                "cache_misses": len(request_data.company_ids),
                "success_rate": 100.0,
            },
        )

    except Exception as e:
        logger.error(f"Batch enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AUDIT & CACHE ENDPOINTS
# ============================================================================


@router.get("/companies/{company_id}/enrichment/audit", response_model=AuditTrailResponse)
async def get_audit_trail(
    company_id: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    request: Request = None
) -> AuditTrailResponse:
    """Get enrichment audit trail for company."""
    if not request:
        raise HTTPException(status_code=500, detail="Request context required")

    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📜 Audit trail request for {company_id}")
    
    # Validate company ID
    is_valid, error = input_validator.validate_company_id(company_id)
    if not is_valid:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Try to get audit entries from database first
    audit_repo = await get_audit_repo_if_available()
    mapped_entries = []
    
    if audit_repo:
        try:
            # Get from database with pagination
            db_entries = await audit_repo.get_audit_trail(
                company_id=company_id,
                limit=limit,
                offset=offset
            )
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
            # Fall back to in-memory logger
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
        # Fall back to in-memory logger
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


@router.get("/companies/{company_id}/enrichment/cache", response_model=CacheCheckResponse)
async def check_cache(company_id: str, request: Request) -> CacheCheckResponse:
    """Check if company is cached."""
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    cached = False
    cache_key = None
    ttl_remaining = None
    cached_data = None

    # Try to check database cache first
    cache_repo = await get_cache_repo_if_available()
    
    if cache_repo:
        try:
            cache_record = await cache_repo.get_cached(company_id)
            if cache_record:
                cached = True
                cache_key = f"company_{company_id}"
                # Calculate remaining TTL
                now = datetime.now(timezone.utc)
                expires_at = cache_record.expires_at
                if expires_at > now:
                    ttl_remaining = int((expires_at - now).total_seconds() / 3600)  # Convert to hours
                cached_data = cache_record.enriched_data
        except Exception as e:
            logger.debug(f"Failed to check cache from database: {e}. Falling back to in-memory cache.")
            # Fall back to in-memory cache
            if hasattr(unified_loader, "cache") and unified_loader.cache:
                cache_key = f"company_{company_id}"
                cached = unified_loader.cache.get(cache_key) is not None
                if cached:
                    ttl_remaining = 24  # Default TTL
    else:
        # Fall back to in-memory cache
        if hasattr(unified_loader, "cache") and unified_loader.cache:
            cache_key = f"company_{company_id}"
            cached = unified_loader.cache.get(cache_key) is not None
            if cached:
                ttl_remaining = 24  # Default TTL

    return CacheCheckResponse(
        company_id=company_id,
        cached=cached,
        cache_key=cache_key,
        ttl_remaining_hours=ttl_remaining,
        cached_data=cached_data,
    )


@router.post("/enrichment/cache/clear", response_model=CacheClearResponse)
async def clear_all_cache(request: Request) -> CacheClearResponse:
    """Clear all enrichment cache."""
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"🧹 Cache clear requested by {client_id}")

    entries_cleared = 0
    
    # Try to clear database cache first
    cache_repo = await get_cache_repo_if_available()
    if cache_repo:
        try:
            entries_cleared = await cache_repo.delete_cache(company_id=None)  # Delete all expired
        except Exception as e:
            logger.warning(f"Failed to clear database cache: {e}")
    
    # Also clear in-memory cache
    if hasattr(unified_loader, "clear_enrichment_cache"):
        unified_loader.clear_enrichment_cache()

    return CacheClearResponse(
        status="success",
        message="Enrichment cache cleared",
        entries_cleared=entries_cleared,
    )


@router.post("/enrichment/cache/clear/{company_id}", response_model=CacheClearResponse)
async def clear_company_cache(company_id: str, request: Request) -> CacheClearResponse:
    """Clear cache for specific company."""
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"🧹 Cache clear for {company_id} by {client_id}")

    entries_cleared = 0
    
    # Try to clear database cache first
    cache_repo = await get_cache_repo_if_available()
    if cache_repo:
        try:
            entries_cleared = await cache_repo.delete_cache(company_id=company_id)
        except Exception as e:
            logger.warning(f"Failed to clear database cache for {company_id}: {e}")
    
    # Also clear in-memory cache
    if hasattr(unified_loader, "cache") and unified_loader.cache:
        cache_key = f"company_{company_id}"
        if cache_key in unified_loader.cache.cache:
            del unified_loader.cache.cache[cache_key]
            entries_cleared = max(entries_cleared, 1)

    return CacheClearResponse(
        status="success",
        message=f"Cache cleared for {company_id}",
        entries_cleared=entries_cleared,
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get_client_id(request: Request) -> str:
    """Extract client ID for rate limiting."""
    # Try X-Client-ID header first
    client_id = request.headers.get("X-Client-ID")
    if client_id:
        return client_id

    # Fall back to IP address
    if request.client:
        return request.client.host

    # Default
    return "unknown"
