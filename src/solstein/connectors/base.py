"""
Base connector interface for all data sources.

This module defines the contract that all data source connectors must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class SourceConfig:
    """Configuration for a data source connector."""

    name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    cache_ttl: int = 3600  # seconds
    timeout: int = 30  # seconds
    retry_attempts: int = 3


@dataclass
class RawData:
    """Raw data extracted from a source."""

    source_name: str
    source_url: str
    raw_content: Any
    extracted_at: datetime
    metadata: dict[str, Any]


@dataclass
class ConnectorResult:
    """Result from a connector operation."""

    success: bool
    data: list[RawData]
    error_message: Optional[str] = None
    total_found: int = 0
    rate_limit_remaining: Optional[int] = None


class BaseConnector(ABC):
    """Abstract base class for all data source connectors."""

    def __init__(self, config: SourceConfig):
        self.config = config
        self._session = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def search(self, query: str, **kwargs) -> ConnectorResult:
        """Search for data matching the query."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> ConnectorResult:
        """Get a specific entity by ID."""
        pass

    @abstractmethod
    def normalize(self, raw_data: RawData) -> dict[str, Any]:
        """Normalize raw data to common format."""
        pass

    async def close(self) -> None:
        """Close connection and cleanup resources."""
        if self._session:
            await self._session.close()

    def _handle_rate_limit(self, response_headers: dict) -> None:
        """Handle rate limiting based on response headers."""
        # Override in subclasses for source-specific rate limit handling
        pass

    def _cache_key(self, query: str, **kwargs) -> str:
        """Generate cache key for a query."""
        import hashlib

        key_data = f"{self.config.name}:{query}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
