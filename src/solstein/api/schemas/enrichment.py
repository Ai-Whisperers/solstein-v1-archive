"""
API Schemas for Enrichment Endpoints (Phase 10)

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# REQUEST SCHEMAS (Input Validation)
# ============================================================================


class EnrichmentRequest(BaseModel):
    """Request to enrich a single company."""

    sources: Optional[List[str]] = Field(
        default=["SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS"], description="Data sources to use for enrichment"
    )
    dry_run: bool = Field(default=False, description="If true, don't persist results")

    class Config:
        schema_extra = {"example": {"sources": ["SEC_EDGAR", "COMPANIES_HOUSE"], "dry_run": False}}


class BatchEnrichmentRequest(BaseModel):
    """Request to batch enrich multiple companies."""

    company_ids: List[str] = Field(..., description="List of company IDs to enrich", min_items=1, max_items=1000)
    batch_size: int = Field(default=10, description="Number of companies to process per batch", ge=1, le=100)
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    dry_run: bool = Field(default=False, description="If true, don't persist results")

    @validator("company_ids")
    def validate_company_ids(cls, v):
        """Validate company ID format."""
        if not v:
            raise ValueError("company_ids must not be empty")
        for cid in v:
            if not isinstance(cid, str) or len(cid) > 100:
                raise ValueError(f"Invalid company ID: {cid}")
        return v

    class Config:
        schema_extra = {
            "example": {"company_ids": ["001", "002", "003"], "batch_size": 10, "use_cache": True, "dry_run": False}
        }


# ============================================================================
# RESPONSE SCHEMAS (Output Validation)
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Response from /health endpoint."""

    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    components: Dict[str, str] = Field(..., description="Component health statuses")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-25T21:00:00Z",
                "version": "1.0",
                "components": {
                    "database": "healthy",
                    "cache": "healthy",
                    "sec_edgar": "healthy",
                    "companies_house": "healthy",
                },
            }
        }


class ReadinessCheckResponse(BaseModel):
    """Response from /ready endpoint."""

    ready: bool = Field(..., description="Whether service is ready")
    timestamp: datetime = Field(..., description="Readiness check timestamp")
    checks: Dict[str, bool] = Field(..., description="Individual readiness checks")

    class Config:
        schema_extra = {
            "example": {
                "ready": True,
                "timestamp": "2026-02-25T21:00:00Z",
                "checks": {"configuration_loaded": True, "connectors_initialized": True, "cache_operational": True},
            }
        }


class MetricsResponse(BaseModel):
    """Response from /metrics endpoint."""

    timestamp: datetime = Field(..., description="Metrics collection time")
    enrichment: Dict[str, Any] = Field(..., description="Enrichment metrics")
    cache: Dict[str, Any] = Field(..., description="Cache metrics")
    rate_limiting: Dict[str, Any] = Field(..., description="Rate limit metrics")

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2026-02-25T21:00:00Z",
                "enrichment": {
                    "total": 156,
                    "successful": 152,
                    "failed": 4,
                    "success_rate": 97.4,
                    "avg_duration_ms": 892,
                },
                "cache": {"size": 45, "ttl_hours": 24, "hits": 230, "misses": 152, "hit_rate": 60.2},
                "rate_limiting": {"requests_per_minute": 100, "current_requests": 45, "remaining": 55},
            }
        }


class EnrichmentResultData(BaseModel):
    """Enriched company data fields."""

    revenue: Optional[float] = Field(None, description="Company revenue")
    employees: Optional[int] = Field(None, description="Number of employees")
    growth_rate: Optional[float] = Field(None, description="Revenue growth rate")
    profit_margin: Optional[float] = Field(None, description="Profit margin")
    funding_raised: Optional[float] = Field(None, description="Funding raised")
    valuation: Optional[float] = Field(None, description="Company valuation")

    class Config:
        schema_extra = {
            "example": {
                "revenue": 5000000,
                "employees": 150,
                "growth_rate": 0.15,
                "profit_margin": 0.12,
                "funding_raised": 2000000,
                "valuation": 50000000,
            }
        }


class EnrichmentResponse(BaseModel):
    """Response from POST /companies/{id}/enrich endpoint."""

    company_id: str = Field(..., description="Company ID")
    company_name: str = Field(..., description="Company name")
    status: str = Field(..., description="Enrichment status (success/failure)")
    enrichment: Dict[str, Any] = Field(..., description="Enrichment details")
    data: Optional[EnrichmentResultData] = Field(None, description="Enriched data")

    class Config:
        schema_extra = {
            "example": {
                "company_id": "001",
                "company_name": "Acme Corp",
                "status": "success",
                "enrichment": {
                    "sources_used": ["SEC_EDGAR", "COMPANIES_HOUSE"],
                    "fields_enriched": ["revenue", "employees", "profit_margin"],
                    "duration_ms": 1234,
                },
                "data": {"revenue": 5000000, "employees": 150, "growth_rate": 0.15, "profit_margin": 0.12},
            }
        }


class BatchEnrichmentResult(BaseModel):
    """Result for single company in batch enrichment."""

    company_id: str = Field(..., description="Company ID")
    status: str = Field(..., description="Enrichment status")
    duration_ms: float = Field(..., description="Processing duration")
    source: Optional[str] = Field(None, description="Data source (cache/SEC_EDGAR/etc)")
    error: Optional[str] = Field(None, description="Error message if failed")


class BatchEnrichmentResponse(BaseModel):
    """Response from POST /companies/enrich/batch endpoint."""

    status: str = Field(..., description="Overall batch status")
    batch_id: str = Field(..., description="Unique batch ID")
    total_companies: int = Field(..., description="Total companies requested")
    enriched_count: int = Field(..., description="Successfully enriched count")
    failed_count: int = Field(..., description="Failed count")
    results: List[BatchEnrichmentResult] = Field(..., description="Per-company results")
    metrics: Dict[str, Any] = Field(..., description="Batch metrics")

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "batch_id": "batch_12345",
                "total_companies": 3,
                "enriched_count": 3,
                "failed_count": 0,
                "results": [
                    {"company_id": "001", "status": "success", "duration_ms": 245, "source": "cache"},
                    {"company_id": "002", "status": "success", "duration_ms": 1234, "source": "SEC_EDGAR"},
                ],
                "metrics": {
                    "total_duration_ms": 1479,
                    "avg_duration_ms": 493,
                    "cache_hits": 1,
                    "cache_misses": 2,
                    "success_rate": 100.0,
                },
            }
        }


class AuditEntry(BaseModel):
    """Single audit log entry."""

    timestamp: datetime = Field(..., description="Operation timestamp")
    operation: str = Field(..., description="Operation type")
    source: Optional[str] = Field(None, description="Data source")
    fields: Optional[List[str]] = Field(None, description="Fields enriched")
    duration_ms: Optional[float] = Field(None, description="Operation duration")
    user_id: Optional[str] = Field(None, description="User who triggered operation")
    status: Optional[str] = Field(None, description="Operation status")


class AuditTrailResponse(BaseModel):
    """Response from GET /companies/{id}/enrichment/audit endpoint."""

    company_id: str = Field(..., description="Company ID")
    company_name: Optional[str] = Field(None, description="Company name")
    audit_entries: List[AuditEntry] = Field(..., description="Audit log entries")
    summary: Dict[str, Any] = Field(..., description="Audit summary")

    class Config:
        schema_extra = {
            "example": {
                "company_id": "001",
                "company_name": "Acme Corp",
                "audit_entries": [
                    {
                        "timestamp": "2026-02-25T21:00:00Z",
                        "operation": "enrich_success",
                        "source": "SEC_EDGAR",
                        "fields": ["revenue", "employees"],
                        "duration_ms": 450,
                        "user_id": "admin@example.com",
                    }
                ],
                "summary": {"total_enrichments": 5, "successful": 4, "failed": 1, "success_rate": 80.0},
            }
        }


class CacheCheckResponse(BaseModel):
    """Response from GET /companies/{id}/enrichment/cache endpoint."""

    company_id: str = Field(..., description="Company ID")
    cached: bool = Field(..., description="Whether company is cached")
    cache_key: Optional[str] = Field(None, description="Cache key")
    ttl_remaining_hours: Optional[float] = Field(None, description="Cache TTL remaining")
    cached_data: Optional[Dict[str, Any]] = Field(None, description="Cached data")

    class Config:
        schema_extra = {
            "example": {
                "company_id": "001",
                "cached": True,
                "cache_key": "enriched_001_AAPL",
                "ttl_remaining_hours": 23.5,
                "cached_data": {"revenue": 5000000, "employees": 150},
            }
        }


class CacheClearResponse(BaseModel):
    """Response from POST /enrichment/cache/clear endpoint."""

    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    entries_cleared: int = Field(..., description="Number of cache entries cleared")

    class Config:
        schema_extra = {"example": {"status": "success", "message": "Enrichment cache cleared", "entries_cleared": 47}}


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")

    class Config:
        schema_extra = {
            "example": {
                "error": "invalid_input",
                "message": "Invalid ticker format: ticker must be 1-10 alphanumeric characters",
                "code": "VAL_001",
                "details": {"field": "ticker", "value": "INVALID!!!"},
            }
        }


class RateLimitErrorResponse(BaseModel):
    """Rate limit exceeded error response."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    retry_after_seconds: int = Field(..., description="Seconds to wait before retry")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "error": "rate_limit_exceeded",
                "message": "Rate limit exceeded: 100 requests per minute",
                "retry_after_seconds": 35,
                "code": "RATELIMIT_001",
            }
        }


class ServiceUnavailableErrorResponse(BaseModel):
    """Service unavailable error response."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    affected_sources: List[str] = Field(..., description="Affected data sources")
    code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "error": "connector_unavailable",
                "message": "SEC EDGAR connector is currently unavailable",
                "affected_sources": ["SEC_EDGAR"],
                "code": "CONNECTOR_001",
            }
        }
