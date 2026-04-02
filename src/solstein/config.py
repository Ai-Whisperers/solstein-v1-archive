"""Configuration management for SolStein."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from solstein._config_timeouts import CeleryTimingConfig, CircuitBreakerConfig, HttpTimeoutsConfig
from solstein.utils.logging import setup_logging as _setup_logging


class ConfigurationError(Exception):
    """Raised when configuration is invalid or incomplete."""

    pass


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = Field(..., description="Database connection URL (required)")
    pool_size: int = Field(default=20, ge=1, le=100)
    echo: bool = Field(default=False)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        if "postgres:postgres@" in v or "password" in v.lower():
            logger.warning("Database URL may contain default credentials - ensure this is for development only")
        return v


class RedisConfig(BaseModel):
    """Redis configuration for caching and job queues."""

    url: str = Field(...)
    cache_ttl: int = Field(default=3600, ge=60, description="Cache TTL in seconds")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate Redis URL."""
        if not v:
            raise ValueError("Redis URL cannot be empty")
        return v

    @property
    def host(self) -> str:
        """Extract host from URL."""
        parts = self.url.split("://")[1].split(":")
        return parts[0]

    @property
    def port(self) -> int:
        """Extract port from URL."""
        parts = self.url.split("://")[1].split(":")
        if len(parts) > 1 and "/" in parts[1]:
            return int(parts[1].split("/")[0])
        return 6379


class SupabaseConfig(BaseModel):
    """Supabase configuration."""

    url: str = Field(default="")
    key: str = Field(default="")
    anon_key: str = Field(default="")
    db_url: str = Field(default="")


class APIConfig(BaseModel):
    """API configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Comma-separated list of allowed CORS origins",
    )
    cors_methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE"], description="Allowed HTTP methods")
    cors_headers: list[str] = Field(default=["Authorization", "Content-Type"], description="Allowed request headers")
    api_prefix: str = Field(default="/api/v1")
    require_api_key: bool = Field(
        default=True,
        description="Require X-API-Key tenant authentication for non-public endpoints",
    )

    @property
    def base_url(self) -> str:
        """Get base URL for API."""
        return f"http://{self.host}:{self.port}{self.api_prefix}"


class SecurityConfig(BaseModel):
    """Security configuration.

    STORY-067: JWT signing and user management are now delegated to Supabase Auth.
    The secret_key is retained for backward compatibility with middleware that
    may still reference it, but Supabase manages JWT secrets externally.
    admin_email and admin_password_hash have been removed -- Supabase Auth
    manages user credentials.
    """

    secret_key: str = Field(
        default="supabase-managed",
        description="Legacy JWT secret. Supabase Auth manages JWT signing externally.",
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file_path: Path | None = Field(default=None)
    rotation: str = Field(default="500 MB")
    retention: str = Field(default="30 days")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


class DataConfig(BaseModel):
    """Data configuration."""

    data_dir: Path = Field(default=Path("data/input"))
    cache_dir: Path = Field(default=Path("data/cache"))
    export_dir: Path = Field(default=Path("data/output/exports"))
    market_data_dir: Path | None = Field(
        default=None,
        description="Directory containing market data files (e.g. company markdown profiles). "
        "When set, the unified loader reads from this directory instead of requiring "
        "MARKET_DATA_DIR env var. No hardcoded market or date defaults are used.",
    )

    @field_validator("data_dir", "cache_dir", "export_dir", "market_data_dir", mode="before")
    @classmethod
    def resolve_paths(cls, v: Any) -> Path | None:
        """Resolve paths to absolute."""
        if v is None:
            return None
        v_path = Path(v) if isinstance(v, str) else v

        if v_path and not v_path.is_absolute():
            # Resolve relative to project root
            project_root = Path(__file__).parent.parent.parent
            v_path = project_root / v_path
        return v_path

    def ensure_dirs(self) -> None:
        """Ensure all directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Main settings class that loads from environment variables."""

    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    debug_errors: bool = Field(
        default=False, description="Include debug info (tracebacks) in error responses. NEVER enable in production."
    )
    # Timeout and resilience configuration
    http_timeouts: HttpTimeoutsConfig = Field(default_factory=HttpTimeoutsConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    celery_timing: CeleryTimingConfig = Field(default_factory=CeleryTimingConfig)
    # Components
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data: DataConfig = Field(default_factory=DataConfig)

    # New Intelligence Engine Backends
    supabase: SupabaseConfig = Field(default_factory=SupabaseConfig)

    # External APIs (optional)
    openai_api_key: str | None = Field(default=None)
    perplexity_api_key: str | None = Field(default=None)
    github_token: str | None = Field(default=None)
    companies_house_api_key: str | None = Field(default=None)
    google_api_key: str | None = Field(default=None)
    google_search_engine_id: str | None = Field(default=None)
    sec_user_agent: str | None = Field(default=None)

    # STORY-101: SearXNG self-hosted meta-search engine (primary web search backend)
    searxng_url: str = Field(
        default="http://searxng:8080",
        description="SearXNG instance URL. docker-compose provides this as a service.",
    )
    searxng_engines: str | None = Field(
        default=None,
        description="Comma-separated SearXNG engine list (e.g. 'google,bing,duckduckgo,brave').",
    )
    search_cache_ttl: int = Field(
        default=3600,
        ge=60,
        description="Search result cache TTL in seconds (default: 1 hour).",
    )

    # Data source APIs
    exa_api_key: str | None = Field(default=None)
    crunchbase_api_key: str | None = Field(default=None)
    news_api_key: str | None = Field(default=None)
    patentsview_api_key: str | None = Field(default=None)

    # STORY-091: Top-level alias so CELERY_RESULT_EXPIRES_SECONDS env var works alongside
    # the nested CELERY_TIMING__RESULT_EXPIRES.
    celery_result_expires_seconds: int | None = Field(
        default=None,
        ge=60,
        description="Override for Celery result TTL (seconds).",
    )

    connector_max_attempts: int = Field(default=3, ge=1, le=10)
    connector_retry_base_delay: float = Field(default=0.25, ge=0.0, le=30.0)
    connector_retry_max_delay: float = Field(default=2.0, ge=0.0, le=120.0)
    connector_circuit_failure_threshold: int = Field(default=5, ge=1, le=100)
    connector_circuit_cooldown_seconds: float = Field(default=30.0, ge=1.0, le=3600.0)

    feature_new_classifier: bool = Field(default=False)
    feature_new_readiness_gate: bool = Field(default=False)
    # DEPRECATED (STORY-256): feature_new_unified_loader is no longer read by
    # build_default_registry.  The legacy enrichment path is canonical.
    # Kept for config-file backward compatibility; will be removed in a
    # future cleanup pass.  Deletion trigger: EPIC-067 complete.
    feature_new_unified_loader: bool = Field(default=False)

    # LLM APIs
    groq_api_key: str | None = Field(default=None)
    fireworks_api_key: str | None = Field(default=None)
    mistral_api_key: str | None = Field(default=None)
    deepinfra_api_key: str | None = Field(default=None)
    gemini_api_key: str | None = Field(default=None)
    nvidia_nim_api_key: str | None = Field(default=None)
    cerebras_api_key: str | None = Field(default=None)
    kimi_api_key: str | None = Field(default=None)

    celery_broker_url: str | None = Field(default=None)
    celery_result_backend: str | None = Field(default=None)
    refresh_schedule: dict[str, Any] | None = Field(default=None)

    llm_provider: str = Field(default="auto")
    llm_provider_order: list[str] = Field(default=["deepinfra", "mistral", "nvidia"])
    llm_circuit_breaker_enabled: bool = Field(default=True)
    ollama_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.2:latest")
    openai_model: str = Field(default="gpt-4o-mini")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    fireworks_model: str = Field(default="accounts/fireworks/models/mixtral-8x22b-instruct")
    mistral_model: str = Field(default="mistral-large-2411")
    deepinfra_model: str = Field(default="meta-llama/Llama-3.3-70B-Instruct")
    gemini_model: str = Field(default="gemini-1.5-flash")
    nvidia_model: str = Field(default="meta/llama-3.3-70b-instruct")
    cerebras_model: str = Field(default="llama-3.3-70b")
    kimi_model: str = Field(default="kimi-k2-32k")
    anthropic_api_key: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-3-5-haiku-20241022")
    siliconflow_api_key: str | None = Field(default=None)
    siliconflow_model: str = Field(default="Qwen/Qwen2.5-72B-Instruct")
    alibaba_api_key: str | None = Field(default=None)
    alibaba_model: str = Field(default="qwen-plus")

    # OpenTelemetry (STORY-050)
    otlp_endpoint: str | None = Field(default=None)

    # Langfuse observability (STORY-073)
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: str | None = Field(default=None)
    langfuse_host: str = Field(default="https://cloud.langfuse.com")

    # Embedding (EPIC-023)
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)
    embedding_batch_size: int = Field(default=50, ge=1, le=500)

    # STORY-079: LangGraph checkpointing and human-in-the-loop
    graph_checkpoint_db_path: Path = Field(default=Path("data/checkpoints/research_graph.db"))
    human_review_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    review_queue_db_path: Path = Field(default=Path("data/checkpoints/review_queue.db"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    @classmethod
    def load(cls) -> "Settings":
        """Load settings with environment variable overrides."""
        env_file = Path(".env")
        if env_file.exists():
            logger.info(f"Loading configuration from {env_file}")
        else:
            logger.warning("No .env file found, using defaults")

        settings = cls()
        _validate_runtime_safety(settings)
        settings.data.ensure_dirs()

        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Data directory: {settings.data.data_dir}")
        return settings

    def get_database_url(self, test: bool = False) -> str:
        """Get database URL, optionally for tests."""
        url = self.supabase.db_url or self.database.url
        if test and "test" not in url and "/" in url:
            parts = url.rsplit("/", 1)
            url = f"{parts[0]}_test/{parts[1]}"
        return url

    def check_configuration(self) -> None:
        """Check required configuration at startup."""
        _check_settings_configuration(self)

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, v: Any) -> str:
        if isinstance(v, str):
            value = v.strip().lower()
            return value or "development"
        return "development"


# ---------------------------------------------------------------------------
# Extracted validation helpers (keep Settings class under 300 lines)
# ---------------------------------------------------------------------------


def _validate_runtime_safety(settings: Settings) -> None:
    """Validate production safety constraints."""
    if settings.environment != "production":
        return

    if not settings.supabase.url or not settings.supabase.key:
        raise ConfigurationError(
            "SUPABASE__URL and SUPABASE__KEY must be configured in production. "
            "Supabase Auth manages authentication and JWT signing."
        )

    if settings.debug:
        raise ConfigurationError("DEBUG must be false in production.")

    if settings.debug_errors:
        raise ConfigurationError("DEBUG_ERRORS must be false in production.")

    if not settings.api.require_api_key:
        raise ConfigurationError("API__REQUIRE_API_KEY must be true in production.")

    lowered_db_url = settings.database.url.lower()
    if "postgres:postgres@" in settings.database.url or "password" in lowered_db_url:
        raise ConfigurationError("DATABASE__URL appears to use insecure default credentials in production.")


def _check_settings_configuration(settings: Settings) -> None:
    """Check required configuration at startup.

    Raises ConfigurationError if critical keys are missing.
    Warns for optional keys. Logs a full startup summary.
    """
    _validate_runtime_safety(settings)

    if not settings.database.url:
        raise ConfigurationError(
            "DATABASE__URL environment variable is required. Set DATABASE__URL before starting the application."
        )

    if settings.supabase.url and not settings.supabase.key:
        logger.warning(
            "SUPABASE__URL is set but SUPABASE__KEY is missing. Supabase Auth will not function without a valid key."
        )

    if not (settings.github_token or "").strip():
        raise ConfigurationError(
            "GITHUB_TOKEN environment variable is required. "
            "Get a token from: https://github.com/settings/tokens and set it before starting."
        )

    optional_data: dict[str, str | None] = {
        "COMPANIES_HOUSE_API_KEY": settings.companies_house_api_key,
        "GOOGLE_API_KEY": settings.google_api_key,
        "EXA_API_KEY": settings.exa_api_key,
        "CRUNCHBASE_API_KEY": settings.crunchbase_api_key,
        "NEWS_API_KEY": settings.news_api_key,
        "SEC_USER_AGENT": settings.sec_user_agent,
    }
    for name, value in optional_data.items():
        if not value:
            logger.warning(f"{name} not configured — related data gathering will be disabled.")

    llm_providers: dict[str, str | None] = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "ANTHROPIC_API_KEY": settings.anthropic_api_key,
        "GROQ_API_KEY": settings.groq_api_key,
        "GEMINI_API_KEY": settings.gemini_api_key,
        "FIREWORKS_API_KEY": settings.fireworks_api_key,
        "MISTRAL_API_KEY": settings.mistral_api_key,
        "DEEPINFRA_API_KEY": settings.deepinfra_api_key,
        "CEREBRAS_API_KEY": settings.cerebras_api_key,
        "KIMI_API_KEY": settings.kimi_api_key,
        "SILICONFLOW_API_KEY": settings.siliconflow_api_key,
        "ALIBABA_API_KEY": settings.alibaba_api_key,
        "NVIDIA_NIM_API_KEY": settings.nvidia_nim_api_key,
        "PERPLEXITY_API_KEY": settings.perplexity_api_key,
        "OLLAMA_URL": settings.ollama_url if settings.llm_provider == "ollama" else None,
    }
    configured = [name for name, val in llm_providers.items() if val]
    missing = [name for name, val in llm_providers.items() if not val]

    if not configured:
        logger.warning(
            "No LLM provider API keys configured. "
            "AI features (report generation, analysis) will be unavailable. "
            f"Set any of: {', '.join(llm_providers.keys())}"
        )

    configured_lines = [f"  ✓ {n}" for n in sorted(configured)]
    missing_lines = [f"  - {n} (optional)" for n in sorted(missing)]

    logger.info(
        "Configuration validation passed.\n"
        "───────────────────────────────────────────────\n"
        "Startup Summary\n"
        "───────────────────────────────────────────────\n" + "\n".join(configured_lines + missing_lines)
    )


@lru_cache
def get_settings() -> "Settings":
    """Get cached settings instance."""
    return Settings.load()


def configure_logging(settings: Settings) -> None:
    """Configure logging based on settings."""
    _setup_logging(
        level=settings.logging.level,
        json_format=settings.logging.format.lower() == "json",
        log_file=settings.logging.file_path,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
    )


# Re-exported from config_template for backward compatibility
from solstein.config_template import ENV_TEMPLATE, create_env_template  # noqa: F401
