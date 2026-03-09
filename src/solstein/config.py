"""
Configuration management for SolStein.

Handles environment variables, configuration files, and settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(Exception):
    """Raised when configuration is invalid or incomplete."""

    pass


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = Field(default="sqlite:///./solstein.db")
    pool_size: int = Field(default=20, ge=1, le=100)
    echo: bool = Field(default=False)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        # Check for placeholder/insecure default
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
    """Security configuration."""

    secret_key: str = Field(default="", description="JWT signing secret. Set SECURITY__SECRET_KEY env var to a strong value.")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)
    admin_email: str | None = Field(default=None, description="Admin login email (set ADMIN_EMAIL env var)")
    admin_password_hash: str | None = Field(
        default=None, description="SHA-256 hex hash of admin password (set ADMIN_PASSWORD_HASH env var)"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key."""
        if not v:
            logger.warning("SECURITY__SECRET_KEY is not set — set it to a strong secret before production use.")
        return v


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

    @field_validator("data_dir", "cache_dir", "export_dir", mode="before")
    @classmethod
    def resolve_paths(cls, v: Any) -> Path:
        """Resolve paths to absolute."""
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
    sec_user_agent: str | None = Field(default=None)

    # Data source APIs
    exa_api_key: str | None = Field(default=None)
    crunchbase_api_key: str | None = Field(default=None)
    news_api_key: str | None = Field(default=None)
    patentsview_api_key: str | None = Field(default=None)

    feature_new_classifier: bool = Field(default=False)
    feature_new_readiness_gate: bool = Field(default=False)
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

    llm_provider: str = Field(
        default="auto",
        description="LLM provider selection: auto|ollama|openai|groq|fireworks|mistral|deepinfra|gemini|nvidia|cerebras|kimi|anthropic|siliconflow|alibaba|none",
    )
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
        # Try to load from .env file
        env_file = Path(".env")
        if env_file.exists():
            logger.info(f"Loading configuration from {env_file}")
        else:
            logger.warning("No .env file found, using defaults")

        settings = cls()
        settings._validate_runtime_safety()
        settings.data.ensure_dirs()

        # Log configuration summary
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
        """Check required configuration at startup.
        
        Raises ConfigurationError if critical keys are missing.
        Warns for optional keys. Logs a full startup summary.
        """
        self._validate_runtime_safety()
        
        # Security key
        if not self.security.secret_key:
            logger.warning(
                "SECURITY__SECRET_KEY is not set. Set this env var to a strong secret before production use."
            )
        
        # Required: GitHub token
        if not (self.github_token or "").strip():
            raise ConfigurationError(
                "GITHUB_TOKEN environment variable is required. "
                "Get a token from: https://github.com/settings/tokens and set it before starting."
            )
        
        # Optional data source keys
        optional_data: dict[str, str | None] = {
            "COMPANIES_HOUSE_API_KEY": self.companies_house_api_key,
            "GOOGLE_API_KEY": self.google_api_key,
            "EXA_API_KEY": self.exa_api_key,
            "CRUNCHBASE_API_KEY": self.crunchbase_api_key,
            "NEWS_API_KEY": self.news_api_key,
        }
        for name, value in optional_data.items():
            if not value:
                logger.warning(f"{name} not configured — related data gathering will be disabled.")
        
        # LLM provider summary
        llm_providers: dict[str, str | None] = {
            "OPENAI_API_KEY": self.openai_api_key,
            "ANTHROPIC_API_KEY": self.anthropic_api_key,
            "GROQ_API_KEY": self.groq_api_key,
            "GEMINI_API_KEY": self.gemini_api_key,
            "FIREWORKS_API_KEY": self.fireworks_api_key,
            "MISTRAL_API_KEY": self.mistral_api_key,
            "DEEPINFRA_API_KEY": self.deepinfra_api_key,
            "CEREBRAS_API_KEY": self.cerebras_api_key,
            "KIMI_API_KEY": self.kimi_api_key,
            "SILICONFLOW_API_KEY": self.siliconflow_api_key,
            "ALIBABA_API_KEY": self.alibaba_api_key,
            "NVIDIA_NIM_API_KEY": self.nvidia_nim_api_key,
            "PERPLEXITY_API_KEY": self.perplexity_api_key,
        }
        configured = [name for name, val in llm_providers.items() if val]
        missing = [name for name, val in llm_providers.items() if not val]
        
        if not configured:
            logger.warning(
                "No LLM provider API keys configured. "
                "AI features (report generation, analysis) will be unavailable. "
                f"Set any of: {', '.join(llm_providers)}"
            )
        
        status_lines = [f"  \u2713 {n}" for n in configured] + [f"  - {n} (not set)" for n in missing[:5]]
        if len(missing) > 5:
            status_lines.append(f"  - ... and {len(missing) - 5} more not configured")
        
        logger.info("Configuration validation passed.\n\u2500\u2500 LLM Providers \u2500\u2500\n" + "\n".join(status_lines))

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, v: Any) -> str:
        if isinstance(v, str):
            value = v.strip().lower()
            return value or "development"
        return "development"

    def _validate_runtime_safety(self) -> None:
        if self.environment != "production":
            return

        if not self.security.secret_key.strip():
            raise ConfigurationError("SECURITY__SECRET_KEY must be set to a strong non-default value in production.")

        if len(self.security.secret_key) < 32:
            raise ConfigurationError("SECURITY__SECRET_KEY must be at least 32 characters in production.")

        if self.debug:
            raise ConfigurationError("DEBUG must be false in production.")

        if self.debug_errors:
            raise ConfigurationError("DEBUG_ERRORS must be false in production.")

        if not self.api.require_api_key:
            raise ConfigurationError("API__REQUIRE_API_KEY must be true in production.")

        lowered_db_url = self.database.url.lower()
        if "postgres:postgres@" in self.database.url or "password" in lowered_db_url:
            raise ConfigurationError("DATABASE__URL appears to use insecure default credentials in production.")


@lru_cache
def get_settings() -> "Settings":
    """Get cached settings instance."""
    return Settings.load()


def configure_logging(settings: Settings) -> None:
    """Configure logging based on settings."""
    from .utils.logging import setup_logging

    setup_logging(
        level=settings.logging.level,
        json_format=settings.logging.format.lower() == "json",
        log_file=settings.logging.file_path,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
    )


# Template for .env file
ENV_TEMPLATE = """# SolStein Configuration
# Copy this file to .env and update values

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (legacy, kept for SQLAlchemy compatibility)
DATABASE__URL=postgresql://<user>:<password>@localhost:5432/solstein
DATABASE__POOL_SIZE=20
DATABASE__ECHO=false

# Supabase
SUPABASE__URL=https://your-project.supabase.co
SUPABASE__KEY=sb_secret_your_key
SUPABASE__ANON_KEY=sb_publishable_your_key
SUPABASE__DB_URL=postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres

# Temporal
TEMPORAL__HOST_URL=localhost:7233
TEMPORAL__NAMESPACE=default
TEMPORAL__API_KEY=

# API
API__HOST=0.0.0.0
API__PORT=8000
API__DEBUG=true
API__CORS_ORIGINS=["http://localhost:3000"]
API__API_PREFIX=/api/v1

# Security
SECURITY__SECRET_KEY=replace-with-a-strong-32-char-min-secret
SECURITY__ALGORITHM=HS256
SECURITY__ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOGGING__LEVEL=INFO
LOGGING__FORMAT=json
LOGGING__FILE_PATH=data/output/logs/solstein.log
LOGGING__ROTATION="500 MB"
LOGGING__RETENTION="30 days"

# Data
DATA__DATA_DIR=data
DATA__CACHE_DIR=.cache
DATA__EXPORT_DIR=exports

# External APIs (optional)
# OPENAI_API_KEY=sk-...
# GROQ_API_KEY=gsk_...
# FIREWORKS_API_KEY=fw_...
# PERPLEXITY_API_KEY=pplx-...  # (currently unused)

# Feature flags (safe cutover controls)
# FEATURE_NEW_CLASSIFIER=false
# FEATURE_NEW_READINESS_GATE=false
# FEATURE_NEW_UNIFIED_LOADER=false

# LLM Runtime (optional)
# LLM_PROVIDER=auto  # auto|ollama|fireworks|openai|groq|none
# OLLAMA_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2:latest
# OPENAI_MODEL=gpt-4o-mini
# GROQ_MODEL=llama-3.3-70b-versatile
# FIREWORKS_MODEL=qwen2-72b-instruct
"""


def create_env_template(output_path: Path = Path(".env.example")) -> None:
    """Create .env template file."""
    output_path.write_text(ENV_TEMPLATE)
    logger.info(f"Created environment template at {output_path}")
