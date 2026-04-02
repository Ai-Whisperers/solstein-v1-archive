"""
API Schemas for Enrichment Endpoints (Phase 10)

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ============================================================================
# REQUEST SCHEMAS (Input Validation)
# ============================================================================


class EnrichmentRequest(BaseModel):
    """Request to enrich a single company."""

    sources: list[str] | None = Field(
        default=["SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS"],
        min_length=1,
        max_length=10,
        description="Data sources to use for enrichment",
    )
    dry_run: bool = Field(default=False, description="If true, don't persist results")

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: list[str] | None) -> list[str] | None:
        """Validate data sources are valid."""
        if v:
            valid_sources = {"SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS", "GITHUB", "CRUNCHBASE"}
            for source in v:
                if not source.strip():
                    raise ValueError("Each source must be a non-empty string")
                if source not in valid_sources:
                    raise ValueError(f"Invalid source '{source}'. Valid: {sorted(valid_sources)}")
            return [s.strip() for s in v]
        return v

    model_config = ConfigDict(
        json_schema_extra={"example": {"sources": ["SEC_EDGAR", "COMPANIES_HOUSE"], "dry_run": False}}
    )


class BatchEnrichmentRequest(BaseModel):
    """Request to batch enrich multiple companies."""

    company_ids: list[str] = Field(..., description="List of company IDs to enrich", min_length=1, max_length=1000)
    batch_size: int = Field(default=10, description="Number of companies to process per batch", ge=1, le=100)
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    dry_run: bool = Field(default=False, description="If true, don't persist results")

    @field_validator("company_ids")
    @classmethod
    def validate_company_ids(cls, v: list[str]) -> list[str]:
        """Validate company ID format."""
        if not v:
            raise ValueError("company_ids must not be empty")
        for cid in v:
            if not cid.strip():
                raise ValueError("Company IDs cannot be empty or whitespace")
            if len(cid) > 100:
                raise ValueError(f"Company ID '{cid}' exceeds max length of 100 characters")
        return [cid.strip() for cid in v]

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size is reasonable."""
        if v < 1 or v > 100:
            raise ValueError("batch_size must be between 1 and 100")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"company_ids": ["001", "002", "003"], "batch_size": 10, "use_cache": True, "dry_run": False}
        }
    )


# ============================================================================
# RESPONSE SCHEMAS (Output Validation)
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Response from /health endpoint."""

    status: str = Field(..., min_length=1, max_length=50, description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., min_length=1, max_length=50, description="API version")
    components: dict[str, str] = Field(..., description="Component health statuses")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is a known value."""
        valid_statuses = {"healthy", "degraded", "unhealthy"}
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {sorted(valid_statuses)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class ReadinessCheckResponse(BaseModel):
    """Response from /ready endpoint."""

    ready: bool = Field(..., description="Whether service is ready")
    timestamp: datetime = Field(..., description="Readiness check timestamp")
    checks: dict[str, bool] = Field(..., description="Individual readiness checks")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ready": True,
                "timestamp": "2026-02-25T21:00:00Z",
                "checks": {"configuration_loaded": True, "connectors_initialized": True, "cache_operational": True},
            }
        }
    )


class MetricsResponse(BaseModel):
    """Response from /metrics endpoint."""

    timestamp: datetime = Field(..., description="Metrics collection time")
    enrichment: dict[str, Any] = Field(..., description="Enrichment metrics")
    cache: dict[str, Any] = Field(..., description="Cache metrics")
    rate_limiting: dict[str, Any] = Field(..., description="Rate limit metrics")

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class EnrichmentResultData(BaseModel):
    """Enriched company data fields."""

    revenue: float | None = Field(None, ge=0, le=1e12, description="Company revenue")
    employees: int | None = Field(None, ge=1, le=1000000, description="Number of employees")
    growth_rate: float | None = Field(None, ge=-1.0, le=10.0, description="Revenue growth rate")
    profit_margin: float | None = Field(None, ge=-1.0, le=1.0, description="Profit margin")
    funding_raised: float | None = Field(None, ge=0, le=1e12, description="Funding raised")
    valuation: float | None = Field(None, ge=0, le=1e12, description="Company valuation")

    @field_validator("revenue", "funding_raised", "valuation")
    @classmethod
    def validate_positive_amounts(cls, v: float | None) -> float | None:
        """Validate monetary amounts are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Monetary amounts must be non-negative")
        return v

    @field_validator("growth_rate", "profit_margin")
    @classmethod
    def validate_rates(cls, v: float | None) -> float | None:
        """Validate rates are within reasonable bounds."""
        if v is not None and not (-1.0 <= v <= 10.0):
            raise ValueError("Rates must be between -1.0 and 10.0")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "revenue": 5000000,
                "employees": 150,
                "growth_rate": 0.15,
                "profit_margin": 0.12,
                "funding_raised": 2000000,
                "valuation": 50000000,
            }
        }
    )


class EnrichmentResponse(BaseModel):
    """Response from POST /companies/{id}/enrich endpoint."""

    company_id: str = Field(..., min_length=1, max_length=100, description="Company ID")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    status: str = Field(..., min_length=1, max_length=50, description="Enrichment status (success/failure)")
    enrichment: dict[str, Any] = Field(..., description="Enrichment details")
    data: EnrichmentResultData | None = Field(None, description="Enriched data")

    @field_validator("company_id")
    @classmethod
    def validate_company_id(cls, v: str) -> str:
        """Validate company ID is not empty."""
        if not v or not v.strip():
            raise ValueError("company_id cannot be empty or whitespace")
        return v.strip()

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        """Validate company name is not empty."""
        if not v or not v.strip():
            raise ValueError("company_name cannot be empty or whitespace")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is a known value."""
        valid_statuses = {"success", "failure", "partial", "pending"}
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {sorted(valid_statuses)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class BatchEnrichmentResult(BaseModel):
    """Result for single company in batch enrichment."""

    company_id: str = Field(..., min_length=1, max_length=100, description="Company ID")
    company_name: str | None = Field(None, min_length=1, max_length=255, description="Company name")
    status: Literal["success", "failure", "partial", "pending", "skipped"] = Field(..., description="Enrichment status")
    duration_ms: float = Field(..., ge=0, le=3600000, description="Processing duration in milliseconds")
    source: str | None = Field(None, min_length=1, max_length=100, description="Data source (cache/SEC_EDGAR/etc)")
    error: str | None = Field(None, max_length=1000, description="Error message if failed")
    errors: list[str] = Field(default_factory=list, description="Explicit enrichment errors for this company")
    from_cache: bool = Field(default=False, description="Whether this result was served from cache")

    @field_validator("company_id")
    @classmethod
    def validate_company_id(cls, v: str) -> str:
        """Validate company ID is not empty."""
        if not v or not v.strip():
            raise ValueError("company_id cannot be empty or whitespace")
        return v.strip()

    @field_validator("duration_ms")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate duration is non-negative."""
        if v < 0:
            raise ValueError("duration_ms must be non-negative")
        return v

    model_config = ConfigDict(extra="forbid")


class BatchEnrichmentMetrics(BaseModel):
    total_duration_ms: int = Field(..., ge=0, description="Total batch duration in milliseconds")
    avg_duration_ms: int = Field(..., ge=0, description="Average per-company duration in milliseconds")
    cache_hits: int = Field(..., ge=0, description="Number of cached outcomes returned")
    cache_misses: int = Field(..., ge=0, description="Number of non-cached outcomes returned")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Percent of non-failed outcomes")

    model_config = ConfigDict(extra="forbid")


class BatchEnrichmentResponse(BaseModel):
    """Response from POST /companies/enrich/batch endpoint."""

    status: Literal["success", "failure", "partial", "pending"] = Field(..., description="Overall batch status")
    batch_id: str = Field(..., min_length=1, max_length=100, description="Unique batch ID")
    total_companies: int = Field(..., ge=0, le=1000000, description="Total companies requested")
    enriched_count: int = Field(..., ge=0, le=1000000, description="Successfully enriched count")
    failed_count: int = Field(..., ge=0, le=1000000, description="Failed count")
    results: list[BatchEnrichmentResult] = Field(..., description="Per-company results")
    metrics: BatchEnrichmentMetrics = Field(..., description="Batch metrics")

    @field_validator("batch_id")
    @classmethod
    def validate_batch_id(cls, v: str) -> str:
        """Validate batch ID is not empty."""
        if not v or not v.strip():
            raise ValueError("batch_id cannot be empty or whitespace")
        return v.strip()

    @field_validator("enriched_count", "failed_count")
    @classmethod
    def validate_counts(cls, v: int) -> int:
        """Validate counts are non-negative."""
        if v < 0:
            raise ValueError("Counts must be non-negative")
        return v

    @model_validator(mode="after")
    def validate_batch_consistency(self) -> "BatchEnrichmentResponse":
        if len(self.results) != self.total_companies:
            raise ValueError("results length must equal total_companies")
        if self.enriched_count + self.failed_count != self.total_companies:
            raise ValueError("enriched_count + failed_count must equal total_companies")
        if self.metrics.cache_hits + self.metrics.cache_misses != self.total_companies:
            raise ValueError("cache_hits + cache_misses must equal total_companies")
        return self

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "status": "success",
                "batch_id": "batch_12345",
                "total_companies": 3,
                "enriched_count": 3,
                "failed_count": 0,
                "results": [
                    {
                        "company_id": "001",
                        "company_name": "Acme Corp",
                        "status": "success",
                        "duration_ms": 245,
                        "source": "cache",
                        "errors": [],
                        "from_cache": True,
                    },
                    {
                        "company_id": "002",
                        "company_name": "Beta Corp",
                        "status": "partial",
                        "duration_ms": 1234,
                        "source": "SEC_EDGAR",
                        "errors": ["[SEC_EDGAR] degraded response"],
                        "from_cache": False,
                    },
                ],
                "metrics": {
                    "total_duration_ms": 1479,
                    "avg_duration_ms": 493,
                    "cache_hits": 1,
                    "cache_misses": 2,
                    "success_rate": 100.0,
                },
            }
        },
    )


class AuditEntry(BaseModel):
    """Single audit log entry."""

    timestamp: datetime = Field(..., description="Operation timestamp")
    operation: str = Field(..., description="Operation type")
    source: str | None = Field(None, description="Data source")
    fields: list[str] | None = Field(None, description="Fields enriched")
    duration_ms: float | None = Field(None, description="Operation duration")
    user_id: str | None = Field(None, description="User who triggered operation")
    status: str | None = Field(None, description="Operation status")


class AuditTrailResponse(BaseModel):
    """Response from GET /companies/{id}/enrichment/audit endpoint."""

    company_id: str = Field(..., description="Company ID")
    company_name: str | None = Field(None, description="Company name")
    audit_entries: list[AuditEntry] = Field(..., description="Audit log entries")
    summary: dict[str, Any] = Field(..., description="Audit summary")

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class CacheCheckResponse(BaseModel):
    """Response from GET /companies/{id}/enrichment/cache endpoint."""

    company_id: str = Field(..., description="Company ID")
    cached: bool = Field(..., description="Whether company is cached")
    cache_key: str | None = Field(None, description="Cache key")
    ttl_remaining_hours: float | None = Field(None, description="Cache TTL remaining")
    cached_data: dict[str, Any] | None = Field(None, description="Cached data")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": "001",
                "cached": True,
                "cache_key": "enriched_001_AAPL",
                "ttl_remaining_hours": 23.5,
                "cached_data": {"revenue": 5000000, "employees": 150},
            }
        }
    )


class CacheClearResponse(BaseModel):
    """Response from POST /enrichment/cache/clear endpoint."""

    status: str = Field(..., min_length=1, max_length=50, description="Operation status")
    message: str = Field(..., min_length=1, max_length=500, description="Status message")
    entries_cleared: int = Field(..., ge=0, le=1000000, description="Number of cache entries cleared")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is a known value."""
        valid_statuses = {"success", "failure", "partial"}
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {sorted(valid_statuses)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": "success", "message": "Enrichment cache cleared", "entries_cleared": 47}
        }
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., min_length=1, max_length=100, description="Error code")
    message: str = Field(..., min_length=1, max_length=1000, description="Error message")
    code: str | None = Field(None, min_length=1, max_length=50, description="Specific error code")
    details: dict[str, Any] | None = Field(None, description="Additional details")

    @field_validator("error")
    @classmethod
    def validate_error(cls, v: str) -> str:
        """Validate error code is not empty."""
        if not v or not v.strip():
            raise ValueError("error cannot be empty or whitespace")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("message cannot be empty or whitespace")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "invalid_input",
                "message": "Invalid ticker format: ticker must be 1-10 alphanumeric characters",
                "code": "VAL_001",
                "details": {"field": "ticker", "value": "INVALID!!!"},
            }
        }
    )


class RateLimitErrorResponse(BaseModel):
    """Rate limit exceeded error response."""

    error: str = Field(..., min_length=1, max_length=100, description="Error code")
    message: str = Field(..., min_length=1, max_length=1000, description="Error message")
    retry_after_seconds: int = Field(..., ge=1, le=3600, description="Seconds to wait before retry")
    code: str | None = Field(None, min_length=1, max_length=50, description="Error code")

    @field_validator("error", "message")
    @classmethod
    def validate_fields(cls, v: str) -> str:
        """Validate fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("retry_after_seconds")
    @classmethod
    def validate_retry_seconds(cls, v: int) -> int:
        """Validate retry seconds is positive."""
        if v < 1:
            raise ValueError("retry_after_seconds must be at least 1")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "rate_limit_exceeded",
                "message": "Rate limit exceeded: 100 requests per minute",
                "retry_after_seconds": 35,
                "code": "RATELIMIT_001",
            }
        }
    )


class ServiceUnavailableErrorResponse(BaseModel):
    """Service unavailable error response."""

    error: str = Field(..., min_length=1, max_length=100, description="Error code")
    message: str = Field(..., min_length=1, max_length=1000, description="Error message")
    affected_sources: list[str] = Field(..., min_length=1, max_length=100, description="Affected data sources")
    code: str | None = Field(None, min_length=1, max_length=50, description="Error code")

    @field_validator("error", "message")
    @classmethod
    def validate_fields(cls, v: str) -> str:
        """Validate fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("affected_sources")
    @classmethod
    def validate_affected_sources(cls, v: list[str]) -> list[str]:
        """Validate affected sources list."""
        if not v:
            raise ValueError("affected_sources must not be empty")
        for source in v:
            if not source.strip():
                raise ValueError("Each source must be a non-empty string")
        return [s.strip() for s in v]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "connector_unavailable",
                "message": "SEC EDGAR connector is currently unavailable",
                "affected_sources": ["SEC_EDGAR"],
                "code": "CONNECTOR_001",
            }
        }
    )
