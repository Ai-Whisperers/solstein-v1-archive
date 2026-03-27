"""Timeout, circuit breaker, and Celery timing configuration models.

Extracted from config.py to keep file size within limits.
All models are imported by the top-level Settings class in config.py.
"""

from pydantic import BaseModel, Field, model_validator


class HttpTimeoutsConfig(BaseModel):
    """HTTP timeout configuration for external API adapters.

    All values are in seconds. Defaults reflect the original hardcoded values
    and have not been validated against actual API SLAs. Tune per environment.
    Override any value via environment variable using nested delimiter:
    e.g. HTTP_TIMEOUTS__GITHUB=20
    """

    default: int = Field(
        default=10,
        ge=1,
        description="Default HTTP timeout (seconds) used when no adapter-specific value is set.",
    )
    github: int = Field(
        default=15,
        ge=1,
        description=(
            "GitHub API timeout (seconds). Default: 15s — original hardcoded value. "
            "GitHub p99 latency is well under 5s; raise only if you see spurious timeouts."
        ),
    )
    companies_house: int = Field(
        default=10,
        ge=1,
        description="Companies House API timeout (seconds). Default: 10s — UK government API.",
    )
    news_api: int = Field(
        default=10,
        ge=1,
        description="NewsAPI timeout (seconds). Default: 10s — original hardcoded value.",
    )
    sec_edgar: int = Field(
        default=30,
        ge=1,
        description=(
            "SEC EDGAR timeout (seconds). Default: 30s — EDGAR responses can be large. "
            "Reduce if your queries are lightweight."
        ),
    )
    exa: int = Field(
        default=15,
        ge=1,
        description="Exa search API timeout (seconds). Default: 15s — original hardcoded value.",
    )
    web_research: int = Field(
        default=30,
        ge=1,
        description="Web research pipeline HTTP timeout (seconds). Default: 30s.",
    )
    patent: int = Field(
        default=30,
        ge=1,
        description="Patent search (PatentsView) timeout (seconds). Default: 30s — large result sets.",
    )
    website_scraper: int = Field(
        default=10,
        ge=1,
        description="Company website scraper timeout (seconds). Default: 10s.",
    )
    funding: int = Field(
        default=10,
        ge=1,
        description="Funding data API (Crunchbase) timeout (seconds). Default: 10s.",
    )
    opencorporates: int = Field(
        default=15,
        ge=1,
        description="OpenCorporates API timeout (seconds). Default: 15s.",
    )
    openfigi: int = Field(
        default=15,
        ge=1,
        description="OpenFIGI API timeout (seconds). Default: 15s.",
    )
    web_search_agent: int = Field(
        default=15,
        ge=1,
        description="Web search agent HTTP timeout (seconds). Default: 15s.",
    )
    evidence_crawler: int = Field(
        default=30,
        ge=1,
        description="Evidence crawler HTTP timeout (seconds). Default: 30s.",
    )
    health_celery_inspect: float = Field(
        default=2.0,
        ge=0.1,
        description=(
            "Celery inspect timeout (seconds) used by the health endpoint. Default: 2.0s — fast health check."
        ),
    )


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration applied uniformly across all adapters.

    Previously failure_threshold varied between 3–5 across agents. Unified to 5
    as a conservative default; tune via environment variables once SLA data exists.

    Override via env: CIRCUIT_BREAKER__FAILURE_THRESHOLD=10, etc.
    """

    failure_threshold: int = Field(
        default=5,
        ge=1,
        description=(
            "Consecutive failures before the circuit opens. Default: 5. Previously varied between 3–5 across agents."
        ),
    )
    recovery_timeout: float = Field(
        default=60.0,
        ge=1.0,
        description=(
            "Seconds in OPEN state before allowing a HALF_OPEN probe. "
            "Default: 60s. Previously varied between 45–90s across agents."
        ),
    )
    half_open_max_calls: int = Field(
        default=3,
        ge=1,
        description="Maximum probe calls in HALF_OPEN state before deciding to close or reopen.",
    )
    cooldown_seconds: float = Field(
        default=30.0,
        ge=0.0,
        description=(
            "Cooldown period (seconds) for the connector runtime circuit breaker. "
            "Default: 30s — shorter than the agent-level breaker for faster bulk-connector recovery."
        ),
    )


class CeleryTimingConfig(BaseModel):
    """Celery task timing configuration.

    Validation ensures soft limit is strictly less than the hard limit.
    Override via env: CELERY_TIMING__TASK_TIME_LIMIT=60, etc.
    """

    task_time_limit: int = Field(
        default=30,
        ge=1,
        description="Hard time limit (seconds) for a single Celery task. Default: 30s.",
    )
    task_soft_time_limit: int = Field(
        default=25,
        ge=1,
        description=(
            "Soft time limit (seconds) for graceful task shutdown. "
            "Default: 25s. Must be strictly less than task_time_limit."
        ),
    )
    result_expires: int = Field(
        default=3600,
        ge=60,
        description="Seconds before task results are purged from the result backend. Default: 3600.",
    )

    @model_validator(mode="after")
    def validate_soft_less_than_hard(self) -> "CeleryTimingConfig":
        """Ensure soft time limit is strictly less than the hard time limit."""
        if self.task_soft_time_limit >= self.task_time_limit:
            raise ValueError(
                f"CELERY_TIMING__TASK_SOFT_TIME_LIMIT ({self.task_soft_time_limit}s) "
                f"must be strictly less than CELERY_TIMING__TASK_TIME_LIMIT ({self.task_time_limit}s). "
                "Increase task_time_limit or decrease task_soft_time_limit."
            )
        return self
