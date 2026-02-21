"""
Configuration management for SolStein.

Handles environment variables, configuration files, and settings.
"""

import os
import sys
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

    url: str = Field(default="postgresql://postgres:postgres@localhost:5432/solstein")
    pool_size: int = Field(default=20, ge=1, le=100)
    echo: bool = Field(default=False)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        return v


class RedisConfig(BaseModel):
    """Redis configuration for caching and job queues."""

    url: str = Field(default="redis://localhost:6379/0")
    cache_ttl: int = Field(default=3600, ge=60, description="Cache TTL in seconds")

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


class TemporalConfig(BaseModel):
    """Temporal orchestration configuration."""

    host_url: str = Field(default="localhost:7233")
    namespace: str = Field(default="default")
    api_key: str | None = Field(default=None)


class APIConfig(BaseModel):
    """API configuration."""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000, ge=1, le=65535)
    debug: bool = Field(default=False)
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    api_prefix: str = Field(default="/api/v1")

    @property
    def base_url(self) -> str:
        """Get base URL for API."""
        return f"http://{self.host}:{self.port}{self.api_prefix}"


class SecurityConfig(BaseModel):
    """Security configuration."""

    secret_key: str = Field(default="change-me-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key."""
        if v == "change-me-in-production":
            logger.warning("Using default secret key - change in production!")
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

    # Components
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    data: DataConfig = Field(default_factory=DataConfig)

    # New Intelligence Engine Backends
    supabase: SupabaseConfig = Field(default_factory=SupabaseConfig)
    temporal: TemporalConfig = Field(default_factory=TemporalConfig)

    # External APIs (optional)
    openai_api_key: str | None = Field(default=None)
    perplexity_api_key: str | None = Field(default=None)

    # News & Patent APIs
    news_api_key: str | None = Field(default=None)
    patentsview_api_key: str | None = Field(default=None)

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
        settings.data.ensure_dirs()

        # Log configuration summary
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Data directory: {settings.data.data_dir}")

        return settings

    def get_database_url(self, test: bool = False) -> str:
        """Get database URL, optionally for tests."""
        url = self.database.url
        if test and "test" not in url and "/" in url:
            parts = url.rsplit("/", 1)
            url = f"{parts[0]}_test/{parts[1]}"
        return url

    def check_configuration(self) -> None:
        """Check required configuration at startup.

        Validates that required API keys are set. Raises ConfigurationError
        if critical keys are missing. Warns if optional keys are missing.

        Required:
            GITHUB_TOKEN - Used for GitHub API calls

        Optional (warns if missing):
            COMPANIES_HOUSE_API_KEY - For Companies House data extraction
            GOOGLE_API_KEY - For web search data extraction

        Raises:
            ConfigurationError: If GITHUB_TOKEN is not set.
        """
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ConfigurationError(
                "GITHUB_TOKEN environment variable is required but not set. "
                "Please set it before starting the application. "
                "Get a token from: https://github.com/settings/tokens"
            )

        companies_house_key = os.getenv("COMPANIES_HOUSE_API_KEY")
        if not companies_house_key:
            logger.warning(
                "COMPANIES_HOUSE_API_KEY not configured. "
                "Companies House data gathering will be disabled."
            )

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning(
                "GOOGLE_API_KEY not configured. "
                "Web search data gathering will be disabled."
            )

        logger.info("Configuration validation passed")


@lru_cache
def get_settings() -> "Settings":
    """Get cached settings instance."""
    settings = Settings.load()

    # Try to load from .env file
    env_file = Path(".env")
    if env_file.exists():
        logger.info(f"Loading configuration from {env_file}")
    else:
        logger.warning("No .env file found, using defaults")

    settings.data.ensure_dirs()

    # Log configuration summary
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Data directory: {settings.data.data_dir}")

    return settings


def configure_logging(settings: Settings) -> None:
    """Configure logging based on settings."""
    from loguru import logger

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level=settings.logging.level,
        colorize=True,
    )

    # Add file handler if configured
    if settings.logging.file_path:
        settings.logging.file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(settings.logging.file_path),
            rotation=settings.logging.rotation,
            retention=settings.logging.retention,
            level=settings.logging.level,
            format=settings.logging.format,
            compression="zip",
        )

    logger.info(f"Logging configured at level {settings.logging.level}")


# Template for .env file
ENV_TEMPLATE = """# SolStein Configuration
# Copy this file to .env and update values

# Environment
ENVIRONMENT=development
DEBUG=true

# Database (legacy, kept for SQLAlchemy compatibility)
DATABASE__URL=postgresql://postgres:postgres@localhost:5432/solstein
DATABASE__POOL_SIZE=20
DATABASE__ECHO=false

# Supabase
SUPABASE__URL=https://your-project.supabase.co
SUPABASE__KEY=sb_secret_your_key
SUPABASE__ANON_KEY=sb_publishable_your_key

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
SECURITY__SECRET_KEY=change-me-in-production
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
# PERPLEXITY_API_KEY=pplx-...
"""


def create_env_template(output_path: Path = Path(".env.example")) -> None:
    """Create .env template file."""
    output_path.write_text(ENV_TEMPLATE)
    logger.info(f"Created environment template at {output_path}")
