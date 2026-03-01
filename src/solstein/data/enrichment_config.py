"""
Phase 6: Configuration & Environment Management

Centralized configuration for the enrichment system with:
- .env file validation
- UnifiedCompanyLoaderConfig class
- Enrichment toggles (enabled/disabled)
- Per-connector toggles
- Configurable timeouts and retries
- Documentation and examples
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from dataclasses import dataclass, field

from loguru import logger


class ConfigError(Exception):
    """Configuration validation error."""

    pass


class EnvValidator:
    """Validates .env file and environment variables on startup."""

    REQUIRED_KEYS = {
        "SEC_EDGAR_API_KEY": "Optional: SEC EDGAR API key for enhanced rate limits",
        "COMPANIES_HOUSE_API_KEY": "Required: Companies House API key",
        "NEWS_API_KEY": "Optional: NewsAPI key for signal detection",
        "ENRICHMENT_ENABLED": "Optional: Enable/disable enrichment (default: true)",
    }

    OPTIONAL_KEYS = {
        "SEC_EDGAR_TIMEOUT": "API timeout in seconds (default: 30)",
        "COMPANIES_HOUSE_TIMEOUT": "API timeout in seconds (default: 30)",
        "NEWS_API_TIMEOUT": "API timeout in seconds (default: 30)",
        "MAX_RETRIES": "Max retry count for failed API calls (default: 3)",
        "ENRICHMENT_BATCH_SIZE": "Batch size for processing (default: 10)",
    }

    @staticmethod
    def validate_startup() -> dict:
        """
        Validate .env file on startup.

        Returns:
            Dictionary of validated environment variables

        Raises:
            ConfigError: If required keys missing or invalid
        """
        env_vars = {}

        # Check required keys
        for key, description in EnvValidator.REQUIRED_KEYS.items():
            value = os.getenv(key)
            if not value and key == "COMPANIES_HOUSE_API_KEY":
                raise ConfigError(f"Missing required environment variable: {key}\nDescription: {description}")
            env_vars[key] = value

        # Check optional keys with defaults
        env_vars["SEC_EDGAR_TIMEOUT"] = int(os.getenv("SEC_EDGAR_TIMEOUT", "30"))
        env_vars["COMPANIES_HOUSE_TIMEOUT"] = int(os.getenv("COMPANIES_HOUSE_TIMEOUT", "30"))
        env_vars["NEWS_API_TIMEOUT"] = int(os.getenv("NEWS_API_TIMEOUT", "30"))
        env_vars["MAX_RETRIES"] = int(os.getenv("MAX_RETRIES", "3"))
        env_vars["ENRICHMENT_BATCH_SIZE"] = int(os.getenv("ENRICHMENT_BATCH_SIZE", "10"))

        # Validate ranges
        if env_vars["SEC_EDGAR_TIMEOUT"] < 1 or env_vars["SEC_EDGAR_TIMEOUT"] > 300:
            raise ConfigError("SEC_EDGAR_TIMEOUT must be 1-300 seconds")
        if env_vars["COMPANIES_HOUSE_TIMEOUT"] < 1 or env_vars["COMPANIES_HOUSE_TIMEOUT"] > 300:
            raise ConfigError("COMPANIES_HOUSE_TIMEOUT must be 1-300 seconds")
        if env_vars["NEWS_API_TIMEOUT"] < 1 or env_vars["NEWS_API_TIMEOUT"] > 300:
            raise ConfigError("NEWS_API_TIMEOUT must be 1-300 seconds")
        if env_vars["MAX_RETRIES"] < 1 or env_vars["MAX_RETRIES"] > 10:
            raise ConfigError("MAX_RETRIES must be 1-10")
        if env_vars["ENRICHMENT_BATCH_SIZE"] < 1 or env_vars["ENRICHMENT_BATCH_SIZE"] > 1000:
            raise ConfigError("ENRICHMENT_BATCH_SIZE must be 1-1000")

        logger.info("✅ Environment configuration validated successfully")
        return env_vars

    @staticmethod
    def print_configuration_guide():
        """Print configuration guide for setup."""
        guide = """
# Enrichment System Configuration Guide

## Required Environment Variables

COMPANIES_HOUSE_API_KEY
  - Purpose: Access UK company financial data
  - Value: Your Companies House API key
  - Get it: https://www.register.companieshouse.gov.uk/developers/
  
## Optional Environment Variables

SEC_EDGAR_API_KEY
  - Purpose: Enhanced rate limits for SEC EDGAR
  - Value: Your SEC EDGAR API key
  - Get it: https://www.sec.gov/cgi-bin/browse-edgar
  - Default: Uses public tier without key
  
NEWS_API_KEY
  - Purpose: News signal detection
  - Value: Your NewsAPI key
  - Get it: https://newsapi.org/
  - Default: Signal detection disabled without key
  
## Configuration Parameters

SEC_EDGAR_TIMEOUT
  - Purpose: API timeout in seconds
  - Default: 30
  - Range: 1-300
  
COMPANIES_HOUSE_TIMEOUT
  - Purpose: API timeout in seconds
  - Default: 30
  - Range: 1-300
  
NEWS_API_TIMEOUT
  - Purpose: API timeout in seconds
  - Default: 30
  - Range: 1-300
  
MAX_RETRIES
  - Purpose: Max retry count for failed API calls
  - Default: 3
  - Range: 1-10
  
ENRICHMENT_BATCH_SIZE
  - Purpose: Batch size for processing
  - Default: 10
  - Range: 1-1000
  - Note: Higher batch size = faster but more memory
  
## Example .env file

COMPANIES_HOUSE_API_KEY=your-api-key-here
SEC_EDGAR_API_KEY=optional-api-key
NEWS_API_KEY=optional-news-api-key
SEC_EDGAR_TIMEOUT=30
COMPANIES_HOUSE_TIMEOUT=30
NEWS_API_TIMEOUT=30
MAX_RETRIES=3
ENRICHMENT_BATCH_SIZE=10
"""
        logger.info("Configuration guide", guide=guide)


@dataclass
class ConnectorConfig:
    """Configuration for individual data source connector."""

    enabled: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    api_key: Optional[str] = None
    batch_size: int = 10
    cache_ttl_hours: int = 24

    def validate(self) -> None:
        """Validate connector configuration."""
        if self.timeout_seconds < 1 or self.timeout_seconds > 300:
            raise ConfigError(f"timeout_seconds must be 1-300, got {self.timeout_seconds}")
        if self.max_retries < 1 or self.max_retries > 10:
            raise ConfigError(f"max_retries must be 1-10, got {self.max_retries}")
        if self.batch_size < 1 or self.batch_size > 1000:
            raise ConfigError(f"batch_size must be 1-1000, got {self.batch_size}")
        if self.cache_ttl_hours < 0 or self.cache_ttl_hours > 8760:
            raise ConfigError(f"cache_ttl_hours must be 0-8760, got {self.cache_ttl_hours}")


@dataclass
class UnifiedCompanyLoaderConfig:
    """
    Centralized configuration for UnifiedCompanyLoader (Phase 6 item 120).

    Controls all aspects of enrichment behavior without code changes.
    """

    # Global enrichment control (Phase 6 item 121)
    enrichment_enabled: bool = True

    # Per-connector configuration (Phase 6 item 122)
    sec_edgar_config: ConnectorConfig = field(
        default_factory=lambda: ConnectorConfig(
            enabled=True,
            timeout_seconds=30,
            max_retries=3,
        )
    )
    companies_house_config: ConnectorConfig = field(
        default_factory=lambda: ConnectorConfig(
            enabled=True,
            timeout_seconds=30,
            max_retries=3,
        )
    )
    news_signals_config: ConnectorConfig = field(
        default_factory=lambda: ConnectorConfig(
            enabled=True,
            timeout_seconds=30,
            max_retries=3,
        )
    )

    # Enrichment behavior
    skip_enrichment_if_complete: bool = True
    immutable_enrichment: bool = True
    rollback_on_error: bool = True

    # Logging and monitoring
    log_enrichment_metrics: bool = True
    track_enrichment_costs: bool = True

    # Dry-run mode for testing
    dry_run: bool = False

    # Timestamp for creation
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def validate(self) -> None:
        """
        Validate all configuration parameters.

        Raises:
            ConfigError: If any parameter is invalid
        """
        self.sec_edgar_config.validate()
        self.companies_house_config.validate()
        self.news_signals_config.validate()

        logger.debug("✅ UnifiedCompanyLoaderConfig validated successfully")

    @classmethod
    def from_env(cls) -> "UnifiedCompanyLoaderConfig":
        """
        Create configuration from environment variables.

        Returns:
            UnifiedCompanyLoaderConfig instance

        Raises:
            ConfigError: If environment validation fails
        """
        env_vars = EnvValidator.validate_startup()

        # Create connector configs from environment
        sec_edgar_config = ConnectorConfig(
            enabled=True,
            timeout_seconds=env_vars.get("SEC_EDGAR_TIMEOUT", 30),
            max_retries=env_vars.get("MAX_RETRIES", 3),
            api_key=env_vars.get("SEC_EDGAR_API_KEY"),
        )

        companies_house_config = ConnectorConfig(
            enabled=True,
            timeout_seconds=env_vars.get("COMPANIES_HOUSE_TIMEOUT", 30),
            max_retries=env_vars.get("MAX_RETRIES", 3),
            api_key=env_vars.get("COMPANIES_HOUSE_API_KEY"),
        )

        news_signals_config = ConnectorConfig(
            enabled=bool(env_vars.get("NEWS_API_KEY")),
            timeout_seconds=env_vars.get("NEWS_API_TIMEOUT", 30),
            max_retries=env_vars.get("MAX_RETRIES", 3),
            api_key=env_vars.get("NEWS_API_KEY"),
        )

        # Create config instance
        config = cls(
            enrichment_enabled=os.getenv("ENRICHMENT_ENABLED", "true").lower() == "true",
            sec_edgar_config=sec_edgar_config,
            companies_house_config=companies_house_config,
            news_signals_config=news_signals_config,
        )

        config.validate()
        return config

    def get_active_connectors(self) -> list[str]:
        """
        Get list of active (enabled) connectors.

        Returns:
            List of enabled connector names
        """
        active = []
        if self.enrichment_enabled:
            if self.sec_edgar_config.enabled:
                active.append("SEC_EDGAR")
            if self.companies_house_config.enabled:
                active.append("COMPANIES_HOUSE")
            if self.news_signals_config.enabled:
                active.append("NEWS_SIGNALS")
        return active

    def summary(self) -> str:
        """
        Get configuration summary for logging.

        Returns:
            Formatted configuration summary
        """
        active = self.get_active_connectors()
        return (
            f"UnifiedCompanyLoaderConfig:\n"
            f"  Enrichment Enabled: {self.enrichment_enabled}\n"
            f"  Active Connectors: {', '.join(active) if active else 'None'}\n"
            f"  SEC EDGAR Timeout: {self.sec_edgar_config.timeout_seconds}s\n"
            f"  Companies House Timeout: {self.companies_house_config.timeout_seconds}s\n"
            f"  News Signals Timeout: {self.news_signals_config.timeout_seconds}s\n"
            f"  Max Retries: {self.sec_edgar_config.max_retries}\n"
            f"  Dry Run: {self.dry_run}\n"
            f"  Immutable Enrichment: {self.immutable_enrichment}\n"
            f"  Rollback on Error: {self.rollback_on_error}"
        )


# Global configuration instance
_global_config: Optional[UnifiedCompanyLoaderConfig] = None


def get_config() -> UnifiedCompanyLoaderConfig:
    """
    Get or create global configuration instance.

    Returns:
        UnifiedCompanyLoaderConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = UnifiedCompanyLoaderConfig.from_env()
        logger.info(_global_config.summary())
    return _global_config


def reset_config() -> None:
    """Reset global configuration (mainly for testing)."""
    global _global_config
    _global_config = None


def load_config(config: UnifiedCompanyLoaderConfig) -> None:
    """
    Load custom configuration instance.

    Args:
        config: UnifiedCompanyLoaderConfig to use globally
    """
    global _global_config
    config.validate()
    _global_config = config
    logger.info("Custom configuration loaded")
