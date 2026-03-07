"""Base classes for health check strategies.

EPIC-022: Extracted from HealthMonitor to enable modular health checks.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class HealthStatus:
    """Health status indicator."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Result of a health check."""

    name: str
    status: str
    message: str
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class HealthCheckStrategy(ABC):
    """Base class for health check strategies.

    Each health check is implemented as a separate strategy class
    for modularity and testability.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this health check."""
        pass

    @abstractmethod
    async def check(self) -> HealthCheck:
        """Execute the health check.

        Returns:
            HealthCheck result with status and details
        """
        pass
